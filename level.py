import pygame
import random
from settings import *
from player import *
from sprites import *
from pytmx.util_pygame import load_pygame
from support import *
from soil import *
from menu import *
from overlay import Overlay


class Level:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()

        self.all_sprites = CameraGroup()
        
        self.collision_sprites = pygame.sprite.Group()

        self.log_sprites = pygame.sprite.Group()
        self.rock_sprites = pygame.sprite.Group()
        self.grass_sprites = pygame.sprite.Group()
        self.interaction_sprites = pygame.sprite.Group()

        self.soil_layer = SoilLayer(self.all_sprites)

        self.setup()

        self.overlay = Overlay(self.player)
        self.menu = Menu(self.player, self.toggle_shop)
        self.show_instructions = False 
        self.instruction = Instructions(self.player, self.toggle_instructions)
        self.shop_active = False

    def setup(self):
        tmx_data = load_pygame('MAP.tmx')

        #Water
        water_frames = import_folder('graphics/water')
        for x,y, surf in tmx_data.get_layer_by_name('Water').tiles():
            Water((x*TILE_SIZE, y*TILE_SIZE), water_frames, self.all_sprites)

        #Decorations
        for x, y, surf in tmx_data.get_layer_by_name('Decorations').tiles():
            upscaled_surf = pygame.transform.scale(surf, (surf.get_width() * UPSCALE_FACTOR, surf.get_height() * UPSCALE_FACTOR))
            Generic((x * NEW_TILE_SIZE_UPSCALED, y * NEW_TILE_SIZE_UPSCALED), upscaled_surf, [self.all_sprites, self.collision_sprites])

        #Decorations2
        for x, y, surf in tmx_data.get_layer_by_name('Decorations2').tiles():
            upscaled_surf = pygame.transform.scale(surf, (surf.get_width() * UPSCALE_FACTOR, surf.get_height() * UPSCALE_FACTOR))
            Generic((x * NEW_TILE_SIZE_UPSCALED, y * NEW_TILE_SIZE_UPSCALED), upscaled_surf, [self.all_sprites, self.collision_sprites])

        #Fences
        for x, y, surf in tmx_data.get_layer_by_name('Fences').tiles():
            upscaled_surf = pygame.transform.scale(surf, (surf.get_width() * UPSCALE_FACTOR, surf.get_height() * UPSCALE_FACTOR))
            Generic((x * NEW_TILE_SIZE_UPSCALED, y * NEW_TILE_SIZE_UPSCALED), upscaled_surf, [self.all_sprites, self.collision_sprites])

        #Logs 
        for obj in tmx_data.get_layer_by_name('Logs'):
            upscaled_surf = pygame.transform.scale(obj.image, 
                (obj.image.get_width() * UPSCALE_FACTOR, 
                obj.image.get_height() * UPSCALE_FACTOR))
            
            upscaled_position = (obj.x * UPSCALE_FACTOR, obj.y * UPSCALE_FACTOR)

            Log_Class(pos = upscaled_position, 
                      surf = upscaled_surf, 
                      groups = [self.all_sprites, self.collision_sprites, self.log_sprites],
                      player_add = self.player_add)

        #Rocks
        for obj in tmx_data.get_layer_by_name('Rocks'):
            upscaled_surf = pygame.transform.scale(obj.image, 
                (obj.image.get_width() * UPSCALE_FACTOR, 
                obj.image.get_height() * UPSCALE_FACTOR))
            
            upscaled_position = (obj.x * UPSCALE_FACTOR, obj.y * UPSCALE_FACTOR)

            Rock_Class(pos = upscaled_position, 
                       surf = upscaled_surf, 
                       groups = [self.all_sprites, self.collision_sprites, self.rock_sprites],
                       player_add = self.player_add)

        #Grass
        for obj in tmx_data.get_layer_by_name('Grass'):
            upscaled_surf = pygame.transform.scale(obj.image, 
                (obj.image.get_width() * UPSCALE_FACTOR, 
                obj.image.get_height() * UPSCALE_FACTOR))
            
            upscaled_position = (obj.x * UPSCALE_FACTOR, obj.y * UPSCALE_FACTOR)

            Grass_Class(pos = upscaled_position, 
                        surf = upscaled_surf, 
                        groups = [self.all_sprites, self.collision_sprites, self.grass_sprites],
                        player_add = self.player_add)

        #Land Barrier
        for x,y,surf in tmx_data.get_layer_by_name('Collisions').tiles():
            Generic((x * NEW_TILE_SIZE_UPSCALED, y * NEW_TILE_SIZE_UPSCALED), pygame.Surface((NEW_TILE_SIZE_UPSCALED, NEW_TILE_SIZE_UPSCALED)), self.collision_sprites)

        #Spawn Player
        for obj in tmx_data.get_layer_by_name('Player'):
            if obj.name == 'SpawnPoint':
                self.player = Player(pos = (obj.x * UPSCALE_FACTOR,obj.y * UPSCALE_FACTOR), 
                                     group = self.all_sprites, 
                                     collision_sprites = self.collision_sprites, 
                                     log_sprites = self.log_sprites,
                                     rock_sprites = self.rock_sprites,
                                     grass_sprites = self.grass_sprites,
                                     soil_layer = self.soil_layer,
                                     interaction_sprites = self.interaction_sprites,
                                     toggle_shop = self.toggle_shop,
                                     toggle_instructions = self.toggle_instructions)
                
            if obj.name == 'Trader':
                Interaction((obj.x * UPSCALE_FACTOR,obj.y * UPSCALE_FACTOR), (obj.width, obj.height), self.interaction_sprites, obj.name)

        original_image = pygame.image.load('NEW_MAP.png').convert_alpha()

        upscaled_image = pygame.transform.scale(original_image, (original_image.get_width() * 4, original_image.get_height() * 4))

        Generic(
            pos=(0, 0),
            surf=upscaled_image,
            groups=self.all_sprites,
            z=LAYERS['Land']
        )
        
    def player_add(self,item):
        if item == 'Wood':
            self.player.item_inventory['Wood'] += 3
        elif item == 'Stone':
            self.player.item_inventory['Stone'] += 2
        elif item == 'Seed':
            if random.random() <= 0.3:
                self.player.seed_inventory['Seed'] += 1

    def toggle_instructions(self):
        self.show_instructions = not self.show_instructions

    def toggle_shop(self):
        self.shop_active = not self.shop_active

    def harvest_add(self,item):
        if item == 'Wheat':
            self.player.item_inventory['Wheat'] += 1

    def plant_collision(self):
        if self.soil_layer.plant_sprites:
            for plant in self.soil_layer.plant_sprites.sprites():
                if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
                    self.harvest_add('Wheat')
                    plant.kill()

                    Particle(pos = plant.rect.topleft,
                             surf = plant.image,
                             groups = self.all_sprites,
                             z = LAYERS['Main'])
                    
                    tile_x = plant.rect.centerx // TILE_SIZE
                    tile_y = plant.rect.centery // TILE_SIZE
                    self.soil_layer.grid[tile_y][tile_x].remove('P')

                    if 'W' in self.soil_layer.grid[tile_y][tile_x]:
                        self.soil_layer.remove_water()

    def run(self,dt):

        #Draw
        self.display_surface.fill('black')
        self.all_sprites.custom_draw(self.player)
        self.overlay.display()

        # Update
        if self.shop_active:
            self.menu.update()    # Draw instructions
        elif self.show_instructions:    # Check if instructions should be shown
            self.instruction.update()
            self.instruction.draw()

        else:
            self.all_sprites.update(dt)
            self.plant_collision()

class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()
          
    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2

        for layer in LAYERS.values():
            for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)

    