import pygame
from pygame.sprite import Group
from settings import *
from support import *
from timer import Timer
from sprites import *
from inventory import *

# The Player class defines the player character's behavior and interactions in the game.
class Player(pygame.sprite.Sprite):
    # The constructor sets up the player's initial properties like position, sprite group,
    # collision groups, tools, inventory, and other important attributes.
    def __init__(self, pos, group, collision_sprites, log_sprites, rock_sprites, grass_sprites, interaction_sprites, soil_layer, toggle_shop, toggle_instructions) -> None:
        super().__init__(group)

        self.import_assets()  # Load the character sprites.
        self.status = 'down_idle'  # Initial state of the player, idle and facing down.
        self.frame_index = 0  # Initially set the frame index for animations.
        
        self.image = self.animations[self.status][self.frame_index]  # Get the image for the current status.
        self.rect = self.image.get_rect(center=pos)  # Create a rectangle for collision and positioning.
        self.z = LAYERS['Main']  # Define the player's layer.

        # Initialize movement attributes.
        self.direction = pygame.math.Vector2()  # Direction vector for movement.
        self.pos = pygame.math.Vector2(self.rect.center)  # Set initial position in the center.
        self.speed = 200  # Speed of the player's movement.

        # Initialize the hitbox for more accurate collision detection.
        self.hitbox = self.rect.copy().inflate((-126, -70))  # Shrinks the rect for collisions.
        self.collision_sprites = collision_sprites  # Stores the other sprites for collision detection.

        # Initialize timers for tool use and seed switching.
        self.timers = {
            'tool use': Timer(350, self.use_tool),  # Timer for using tools with a 350ms cooldown.
            'tool switch': Timer(200),  # Timer for switching tools with a 200ms cooldown.
            'seed use': Timer(350, self.use_seed),  # Timer for using seeds with a 350ms cooldown.
            'seed switch': Timer(200),  # Timer for switching seeds with a 200ms cooldown.
        }

        # Initialize inventory, including tools and seeds.
        self.seeds = ['Seed']  # A list of seeds the player has.
        self.seed_index = 0  # Index for tracking selected seed.
        self.selected_seed = self.seeds[self.seed_index]  # Initially selected seed.

        self.tools = ['axe', 'hoe', 'water']  # List of tools available to the player.
        self.tool_index = 0  # Index for tracking selected tool.
        self.selected_tool = self.tools[self.tool_index]  # Initially selected tool.

        # Inventory for collecting items such as Wood, Stone, and Wheat.
        self.item_inventory = {
            'Wood': 0,
            'Stone': 0,
            'Wheat': 0,
        }

        # Seed inventory, starting with two Seed items.
        self.seed_inventory = {
            'Seed': 2,
        }

        # Money the player has.
        self.money = 0
        
        # Various sprites and layers the player can interact with.
        self.log_sprites = log_sprites
        self.rock_sprites = rock_sprites
        self.grass_sprites = grass_sprites
        self.soil_layer = soil_layer  # For interacting with the farm's soil.
        self.interaction_sprites = interaction_sprites  # Sprites that can be interacted with (like NPCs or objects).

        # Functions to open the shop or instructions menu.
        self.toggle_shop = toggle_shop
        self.toggle_instructions = toggle_instructions

    # Load animations for each possible player action.
    def import_assets(self):
        self.animations = {'up':[], 'down':[], 'left':[], 'right':[],
                           'up_idle':[], 'down_idle':[], 'left_idle':[],'right_idle':[],
                           'up_hoe':[], 'down_hoe':[], 'left_hoe':[], 'right_hoe':[],
                           'up_axe':[],'down_axe':[], 'left_axe':[], 'right_axe':[],
                           'up_water': [],'down_water':[], 'left_water':[], 'right_water':[]}

        # Load animation images for the player from the assets folder.
        for animation in self.animations.keys():
            full_path = 'graphics/character/' + animation  # Path for the animation files.
            self.animations[animation] = import_folder(full_path)

    # Logic for using tools, like hoeing the soil, cutting logs, mining rocks, or watering.
    def use_tool(self):
        if self.selected_tool == 'hoe':
            self.soil_layer.get_hit(self.target_pos)  # Hoe the soil where the target position is.

        if self.selected_tool == 'axe':
            if self.target_pos is not None:
                # Check for collisions and damage with logs, rocks, and grass.
                for log in self.log_sprites.sprites():
                    if isinstance(log, Log_Class) and log.rect.collidepoint(self.target_pos):
                        log.damage()

                for rock in self.rock_sprites.sprites():
                    if isinstance(rock, Rock_Class) and rock.rect.collidepoint(self.target_pos):
                        rock.damage()

                for grass in self.grass_sprites.sprites():
                    if isinstance(grass, Grass_Class) and grass.rect.collidepoint(self.target_pos):
                        grass.damage()

        if self.selected_tool == 'water':
            self.soil_layer.water(self.target_pos)  # Water the soil at the target position.

    # Logic for planting seeds on the soil.
    def use_seed(self):
        if self.seed_inventory[self.selected_seed] > 0:
            self.soil_layer.plant_seed(self.target_pos, self.selected_seed)  # Plant the selected seed.
            self.seed_inventory[self.selected_seed] -= 1  # Decrease seed count after planting.

    # Determine the target position based on where the player is facing and what action they are doing.
    def get_target_pos(self):
        self.target_pos = self.rect.center + PLAYER_TOOL_OFFSET[self.status.split('_')[0]]

    # Animate the player based on movement and status.
    def animate(self, dt):
        self.frame_index += 4 * dt  # Update the frame index based on the elapsed time.
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0  # Reset the frame index if it exceeds the animation length.
        self.image = self.animations[self.status][int(self.frame_index)]  # Update the player's image.

    # Handle player input for movement, tool usage, menu access, etc.
    def input(self):
        keys = pygame.key.get_pressed()  # Get currently pressed keys.

        if not self.timers["tool use"].active:  # Check if tool usage is on cooldown.
            if keys[pygame.K_w]:  # Moving up
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_s]:  # Moving down
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0

            if keys[pygame.K_a]:  # Moving left
                self.direction.x = -1
                self.status = 'left'
            elif keys[pygame.K_d]:  # Moving right
                self.direction.x = 1
                self.status = 'right'
            else:
                self.direction.x = 0

            # Tool usage
            if keys[pygame.K_SPACE]:
                self.timers['tool use'].activate()  # Use the currently selected tool.
                self.direction = pygame.math.Vector2()
                self.frame_index = 0  # Reset frame index when tool is used.

            # Change tool
            if keys[pygame.K_q] and not self.timers['tool switch'].active:
                self.timers['tool switch'].activate()
                self.tool_index += 1
                self.tool_index = self.tool_index if self.tool_index < len(self.tools) else 0
                self.selected_tool = self.tools[self.tool_index]

            # Seed usage
            if keys[pygame.K_LCTRL]:
                self.timers['seed use'].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0

            # Open shop menu
            if keys[pygame.K_m]:
                self.toggle_shop()
                collided_interaction_sprite = pygame.sprite.spritecollide(self, self.interaction_sprites, False)
                if collided_interaction_sprite:
                    self.toggle_shop()
                else:
                    self.status = 'left_idle'

            # Open instructions menu
            if keys[pygame.K_i]:
                self.toggle_instructions()

    # Update the player's status based on their movement.
    def get_status(self):
        if self.direction.magnitude() == 0:  # If the player is not moving, set status to idle.
            self.status = self.status.split('_')[0] + '_idle'

        if self.timers["tool use"].active:
            self.status = self.status.split("_")[0] + "_" + self.selected_tool  # Update status during tool use.

    # Update the timers for tool and seed actions.
    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    # Handle collisions for the player, preventing them from passing through objects.
    def collide(self, direction):
        for sprite in self.collision_sprites.sprites():
            if hasattr(sprite, 'hitbox'):
                if sprite.hitbox.colliderect(self.hitbox):
                    if direction == 'horizontal':
                        # Handle horizontal collision.
                        if self.direction.x > 0:
                            self.hitbox.right = sprite.hitbox.left
                        if self.direction.x < 0:
                            self.hitbox.left = sprite.hitbox.right
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx

                    if direction == 'vertical':
                        # Handle vertical collision.
                        if self.direction.y > 0:
                            self.hitbox.bottom = sprite.hitbox.top
                        if self.direction.y < 0:
                            self.hitbox.top = sprite.hitbox.bottom
                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery

    # Move the player based on input and apply collision handling.
    def move(self, dt):
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()  # Normalize movement to prevent diagonal speed boost.

        # Update player position based on the direction and speed.
        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collide('horizontal')  # Handle horizontal collision.

        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collide('vertical')  # Handle vertical collision.

    # Update the player each frame.
    def update(self, dt):
        self.input()  # Handle input.
        self.move(dt)  # Update position based on input.
        self.get_status()  # Update status.
        self.update_timers()  # Update timers for actions.
        self.get_target_pos()  # Update target position for tools and planting.
        self.animate(dt)  # Animate player based on current status.
