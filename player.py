import pygame
from pygame.sprite import Group
from settings import *
from support import *
from timer import Timer
from sprites import *
from menu import *


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group, collision_sprites, log_sprites, rock_sprites, grass_sprites, interaction_sprites, soil_layer, toggle_shop, toggle_instructions) -> None:
        super().__init__(group)

        self.import_assets()
        self.status = 'down_idle'
        self.frame_index = 0
        
        self.image = self.animations[self.status][self.frame_index] #w,h
        self.rect = self.image.get_rect(center=pos)
        self.z = LAYERS['Main']

        # move atribute
        self.direction = pygame.math.Vector2() #x,y atau 0,0
        self.pos = pygame.math.Vector2(self.rect.center) # ini supaya posisi awal ditengah
        self.speed = 200

        #collision
        self.hitbox = self.rect.copy().inflate((-126,-70))
        self.collision_sprites = collision_sprites

		# timers 
        self.timers = {
            'tool use': Timer(350,self.use_tool),
            'tool switch': Timer(200),
            'seed use': Timer(350,self.use_seed),
            'seed switch': Timer(200),
        }

        #seeds
        self.seeds = ['Seed']
        self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]

        # tools
        self.tools = ['axe','hoe', 'water']
        self.tool_index = 0
        self.selected_tool = self.tools [self.tool_index]

        #inventory
        self.item_inventory = {
            'Wood': 0,
            'Stone': 0,
            'Wheat': 0,
        }

        self.seed_inventory = {
            'Seed': 2,
        }

        self.money = 0
        
        #interaction
        self.log_sprites = log_sprites
        self.rock_sprites = rock_sprites
        self.grass_sprites = grass_sprites
        self.soil_layer = soil_layer
        self.interaction_sprites = interaction_sprites

        self.toggle_shop = toggle_shop
        self.toggle_instructions = toggle_instructions

    def import_assets(self):
        self.animations = {'up':[], 'down':[], 'left':[], 'right':[],
                           'up_idle':[], 'down_idle':[], 'left_idle':[],'right_idle':[],
                           'up_hoe':[], 'down_hoe':[], 'left_hoe':[], 'right_hoe':[],
                           'up_axe':[],'down_axe':[], 'left_axe':[], 'right_axe':[],
                           'up_water': [],'down_water':[], 'left_water':[], 'right_water':[]}

        for animation in self.animations.keys():
            full_path = 'graphics/character/' + animation #pastikan path sesuai
            self.animations[animation] = import_folder(full_path)

    def use_tool(self):
        if self.selected_tool == 'hoe':
            self.soil_layer.get_hit(self.target_pos)
		
        if self.selected_tool == 'axe':
            if self.target_pos is not None:

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
            self.soil_layer.water(self.target_pos)
    
    def use_seed(self):
        if self.seed_inventory[self.selected_seed] > 0:
            self.soil_layer.plant_seed(self.target_pos, self.selected_seed)
            self.seed_inventory[self.selected_seed] -= 1

    def get_target_pos(self):
        self.target_pos = self.rect.center + PLAYER_TOOL_OFFSET[self.status.split('_')[0]]

    # for animation running  
    def animate(self, dt):
        self.frame_index += 4 * dt
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0
        self.image = self.animations[self.status][int(self.frame_index)]

    def input(self):
        # move event
        keys = pygame.key.get_pressed()
        if not self.timers["tool use"].active:
            if keys[pygame.K_w]:
                self.direction.y = -1  #naik ketatas meskipun button di release
                self.status = 'up'

            elif keys[pygame.K_s]:
                self.direction.y = 1
                self.status = 'down'
            else :
                self.direction.y = 0 #makannya dibuat 0 jika tidak ada klik apapun
            if keys[pygame.K_a]:
                # print("LEFT")
                self.direction.x = -1
                self.status = 'left'
            elif keys[pygame.K_d]:
                # print("RIGHT")
                self.direction.x = 1
                self.status = 'right'
            else :
                self.direction.x = 0

			# tool
            if keys[pygame.K_SPACE]:
                self.timers['tool use'].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0

			# change tool
            if keys[pygame.K_q] and not self.timers['tool switch'].active:
                self.timers['tool switch'].activate()
                self.tool_index += 1
                self.tool_index = self.tool_index if self.tool_index < len(self.tools) else 0
                self.selected_tool = self.tools[self.tool_index]

			# seed use
            if keys[pygame.K_LCTRL]:
                self.timers['seed use'].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0

            #menu
            if keys[pygame.K_m]:
                self.toggle_shop()
                collided_interaction_sprite = pygame.sprite.spritecollide(self,self.interaction_sprites,False)
                if collided_interaction_sprite:
                    self.toggle_shop()
                else:
                    self.status = 'left_idle'

            if keys[pygame.K_i]:
                self.toggle_instructions()

    def get_status(self):
        #if player not moving add idle
        if self.direction.magnitude()==0:
            # add idle status
            self.status = self.status.split('_')[0]+ '_idle'

        if self.timers["tool use"].active:
            self.status = self.status.split("_")[0]+"_"+self.selected_tool

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def collide(self,direction):
        for sprite in self.collision_sprites.sprites():
            if hasattr(sprite, 'hitbox'):
                if sprite.hitbox.colliderect(self.hitbox):
                    if direction == 'horizontal':
                        if self.direction.x > 0:
                            self.hitbox.right = sprite.hitbox.left
                        if self.direction.x < 0:
                            self.hitbox.left = sprite.hitbox.right
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx

                    if direction == 'vertical':
                        if self.direction.y > 0:
                            self.hitbox.bottom = sprite.hitbox.top
                        if self.direction.y < 0:
                            self.hitbox.top = sprite.hitbox.bottom
                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery


    def move(self, dt):
        # normalize
        if self.direction.magnitude() >0 :
            self.direction = self.direction.normalize()

        # vertikal & horizontal movement
        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collide('horizontal')

        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collide('vertical')

    def update(self,dt):
        self.input()
        self.move(dt)
        self.get_status()
        self.update_timers()
        self.get_target_pos()
        self.animate(dt)
