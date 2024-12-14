import pygame
import random
from settings import *
from player import *
from sprites import *
from pytmx.util_pygame import load_pygame
from support import *
from soil import *
from inventory import *
from ui import Overlay


class Level:
    def __init__(self):
        #Get Game's Display Surface
        self.display_surface = pygame.display.get_surface()

        #Sprites Groups
        self.all_sprites = CameraGroup() #Calls CameraGroup class
        self.collision_sprites = pygame.sprite.Group() #Collision
        self.log_sprites = pygame.sprite.Group() #Logs To Be Collected
        self.rock_sprites = pygame.sprite.Group() #Rocks To Be Collected
        self.grass_sprites = pygame.sprite.Group() #Grass To Be Collected
        self.interaction_sprites = pygame.sprite.Group() #Object to Interact

        #Soil Layer, Manages Soil and Farming
        self.soil_layer = SoilLayer(self.all_sprites)

        #Calls Setup Method
        self.setup()

        #UI Elements above all of the sprites group above
        self.overlay = Overlay(self.player) #Tool Overlay
        self.menu = Menu(self.player, self.toggle_shop) #In-game Menu/Inventory
        self.show_instructions = False #Indicates whether variable should be visible
        self.instruction = Instructions(self.player, self.toggle_instructions) #In-game Instructions
        self.shop_active = False #Indicates whether variable should be visible

    def setup(self):
        #With pytmx.util_pygame module, this loads the map file
        tmx_data = load_pygame('MAP.tmx')

        #Loads Water tile layer
        water_frames = import_folder('graphics/water')
        for x,y, surf in tmx_data.get_layer_by_name('Water').tiles():
            Water((x*TILE_SIZE, y*TILE_SIZE), water_frames, self.all_sprites)
                #Tile positions is scaled by TILE_SIZE 
                #Animations set as water_frames
                #The water tiles are added to the all_sprites group for rendering

        #Loads Decorations tile layer
        for x, y, surf in tmx_data.get_layer_by_name('Decorations').tiles():
            upscaled_surf = pygame.transform.scale(surf, (surf.get_width() * UPSCALE_FACTOR, surf.get_height() * UPSCALE_FACTOR))
                #Upscales surface with UPSCALE_FACTOR, from 16-bit pixels
            Generic((x * NEW_TILE_SIZE_UPSCALED, y * NEW_TILE_SIZE_UPSCALED), upscaled_surf, [self.all_sprites, self.collision_sprites])
                #Set as Generic Object, positions it, and adds it to sprite group
                #all_sprites: group to render the decoration
                #collision_sprites: group for enabling collision with the decoration

        #load Decorations2 which overlaps Decorations
        for x, y, surf in tmx_data.get_layer_by_name('Decorations2').tiles():
            upscaled_surf = pygame.transform.scale(surf, (surf.get_width() * UPSCALE_FACTOR, surf.get_height() * UPSCALE_FACTOR))
            Generic((x * NEW_TILE_SIZE_UPSCALED, y * NEW_TILE_SIZE_UPSCALED), upscaled_surf, [self.all_sprites, self.collision_sprites])

        #Loads Fences
        for x, y, surf in tmx_data.get_layer_by_name('Fences').tiles():
            upscaled_surf = pygame.transform.scale(surf, (surf.get_width() * UPSCALE_FACTOR, surf.get_height() * UPSCALE_FACTOR))
            Generic((x * NEW_TILE_SIZE_UPSCALED, y * NEW_TILE_SIZE_UPSCALED), upscaled_surf, [self.all_sprites, self.collision_sprites])

        #Loads Logs and make it Interactive
        for obj in tmx_data.get_layer_by_name('Logs'):
            #Upscale surface image by UPSCALE_FACTOR, making it bigger
            upscaled_surf = pygame.transform.scale(obj.image, 
                (obj.image.get_width() * UPSCALE_FACTOR, 
                obj.image.get_height() * UPSCALE_FACTOR))
            
            #Upscales the position by UPSCALE_FACTOR, so it could match the upsized game world
            upscaled_position = (obj.x * UPSCALE_FACTOR, obj.y * UPSCALE_FACTOR)

            #Set as Log_Class from sprite.py, upscaling the position and surfaces
            #log_sprites: Adds log sprite and Handles the interaction
            Log_Class(pos = upscaled_position, 
                      surf = upscaled_surf, 
                      groups = [self.all_sprites, self.collision_sprites, self.log_sprites],
                      player_add = self.player_add) #Adds item to inventory

        #Loads Rocks and make it Interactive
        for obj in tmx_data.get_layer_by_name('Rocks'):
            upscaled_surf = pygame.transform.scale(obj.image, 
                (obj.image.get_width() * UPSCALE_FACTOR, 
                obj.image.get_height() * UPSCALE_FACTOR))
            
            upscaled_position = (obj.x * UPSCALE_FACTOR, obj.y * UPSCALE_FACTOR)

            Rock_Class(pos = upscaled_position, 
                       surf = upscaled_surf, 
                       groups = [self.all_sprites, self.collision_sprites, self.rock_sprites],
                       player_add = self.player_add)

        #Loads Grass and make it Interactive
        for obj in tmx_data.get_layer_by_name('Grass'):
            upscaled_surf = pygame.transform.scale(obj.image, 
                (obj.image.get_width() * UPSCALE_FACTOR, 
                obj.image.get_height() * UPSCALE_FACTOR))
            
            upscaled_position = (obj.x * UPSCALE_FACTOR, obj.y * UPSCALE_FACTOR)

            Grass_Class(pos = upscaled_position, 
                        surf = upscaled_surf, 
                        groups = [self.all_sprites, self.collision_sprites, self.grass_sprites],
                        player_add = self.player_add)

        #Loads Land Barrier, making player not be able to go through it, Inherits Generic
        for x,y,surf in tmx_data.get_layer_by_name('Collisions').tiles():
            Generic((x * NEW_TILE_SIZE_UPSCALED, y * NEW_TILE_SIZE_UPSCALED), pygame.Surface((NEW_TILE_SIZE_UPSCALED, NEW_TILE_SIZE_UPSCALED)), self.collision_sprites)

        #Loads Player in game and in the SpawnPoint, already set through the tmx file
        for obj in tmx_data.get_layer_by_name('Player'):
            if obj.name == 'SpawnPoint':
                #Player position is upscaled, adjusting it to the world
                self.player = Player(pos = (obj.x * UPSCALE_FACTOR,obj.y * UPSCALE_FACTOR), 
                                     group = self.all_sprites, #Group to store and update player sprite
                                     collision_sprites = self.collision_sprites, #Group for handling collisions
                                     log_sprites = self.log_sprites, #Group to track logs
                                     rock_sprites = self.rock_sprites, #Group to track Rocks
                                     grass_sprites = self.grass_sprites, #Group to track Grass
                                     soil_layer = self.soil_layer, #Group to interact with soil layer
                                     interaction_sprites = self.interaction_sprites, 
                                     toggle_shop = self.toggle_shop, #Method to toggle shop
                                     toggle_instructions = self.toggle_instructions) #Method to toggle instructions
                
        #Loads image 'NEW_MAP'
        original_image = pygame.image.load('NEW_MAP.png').convert_alpha()
        #Upscales the image
        upscaled_image = pygame.transform.scale(original_image, (original_image.get_width() * 4, original_image.get_height() * 4))

        #Creates Generic Object
        Generic(
            pos=(0, 0), #Position at (0,0)
            surf=upscaled_image, 
            groups=self.all_sprites, #Adds sprite to all_sprites group 
            z=LAYERS['Land'] #Set Layer to Land
        )
        
    def player_add(self,item): #Function to add Item
        if item == 'Wood':
            self.player.item_inventory['Wood'] += 3
        elif item == 'Stone':
            self.player.item_inventory['Stone'] += 2
        elif item == 'Seed':
            if random.random() <= 0.3:
                self.player.seed_inventory['Seed'] += 1

    def toggle_instructions(self): #Function to toggle instructions
        self.show_instructions = not self.show_instructions #Reverses the value

    def toggle_shop(self): #Function to toggle shop
        self.shop_active = not self.shop_active #Reverse the value

    def harvest_add(self,item): #Function to add Harvested Item
        if item == 'Wheat':
            self.player.item_inventory['Wheat'] += 1

    def plant_collision(self):
        #Check if there are plants in the soil layer
        if self.soil_layer.plant_sprites:
            #Loop through each plant in the soil_layer's plant_sprites group
            for plant in self.soil_layer.plant_sprites.sprites():
                #Check if plant is harvestable and create a rectangle that collides with player's hitbox
                if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
                    self.harvest_add('Wheat') #Adds Wheat to inventory
                    plant.kill() #Kills item from the game

                    #Creates Particle Effect
                    Particle(pos = plant.rect.topleft,
                             surf = plant.image,
                             groups = self.all_sprites,
                             z = LAYERS['Main'])
                    
                    #Find tile position and based it on its center
                    tile_x = plant.rect.centerx // TILE_SIZE
                    tile_y = plant.rect.centery // TILE_SIZE

                    #Remove the plant marker 'P' from the soil grid
                    self.soil_layer.grid[tile_y][tile_x].remove('P')

                    #If there is water marked with 'W' in the soil grid at the plant's location, remove the water
                    if 'W' in self.soil_layer.grid[tile_y][tile_x]:
                        self.soil_layer.remove_water()

    def run(self,dt):

        #Draw
        self.display_surface.fill('black') #Fill screen with a black color
        self.all_sprites.custom_draw(self.player) #Draw all sprites
        self.overlay.display() #Display Overlay

        #Check and Update Instruction and Menu
        if self.shop_active:
            self.menu.update() 
        elif self.show_instructions:    
            self.instruction.update()
            self.instruction.draw()

        #Update game state normally
        else:
            self.all_sprites.update(dt)
            self.plant_collision()

class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__() #Initializes the sprite group base class
        self.display_surface = pygame.display.get_surface() #Get Screen Surface
        self.offset = pygame.math.Vector2() #Initialize the offset vector used for camera scrolling
          
    def custom_draw(self, player):
        #Set camera offset to center
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2

        #Loop through all sprite layers
        for layer in LAYERS.values():
            #Sorts in their vertical position
            for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
                if sprite.z == layer: #Check if sprite is part of current layer
                    #Copy the sprite's rect and apply the offset(simulating camera scroll)
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect) #Draw sprite to new offset position

    