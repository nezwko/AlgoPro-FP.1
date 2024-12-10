import pygame
from settings import *
from timer import Timer
from level import *

class Generic(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, z = LAYERS['Main']):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = z 
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.75)

class Interaction(Generic):
	def __init__(self, pos, size, groups, name):
		surf = pygame.Surface(size)
		super().__init__(pos, surf, groups)
		self.name = name

class Water(Generic):
    def __init__(self, pos, frames, groups):
        self.frames = frames
        self.frame_index = 0

        super().__init__(pos = pos,
                         surf = self.frames[self.frame_index],
                         groups = groups,
                         z = LAYERS['Water'])
        
    def animate(self,dt):
        self.frame_index += 5 * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]
    
    def update(self,dt):
        self.animate(dt)

        
class Particle(Generic):
    def __init__ (self, pos, surf, groups, z, duration = 200):
        super().__init__(pos, surf, groups, z)
        self.start_time = pygame.time.get_ticks()
        self.duration = duration

        mask_surf = pygame.mask.from_surface(self.image)
        new_surf = mask_surf.to_surface()
        new_surf.set_colorkey((0,0,0))
        self.image = new_surf
        
    def update(self,dt):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time > self.duration:
            self.kill()


class Log_Class(Generic):  
    def __init__(self, pos, surf, groups, player_add):
        super().__init__(pos, surf, groups)
        self.health = 3
        self.alive = True

        self.player_add = player_add

    def damage(self):
        self.health -= 1

    def check_death(self):
        if self.health <= 0:
            Particle(self.rect.topleft, self.image, self.groups()[0], LAYERS['Death'], 300)
            self.alive = False
            self.kill()
            self.player_add('Wood')
    
    def update(self,dt):
        if self.alive:
            self.check_death()
        

class Rock_Class(Generic):
    def __init__(self, pos, surf, groups, player_add):
        super().__init__(pos, surf, groups)
        self.health = 4
        self.alive = True

        self.player_add = player_add

    def damage(self):
        self.health -= 1

    def check_death(self):
        if self.health <= 0:
            Particle(self.rect.topleft, self.image, self.groups()[0], LAYERS['Death'], 300)
            self.alive = False
            self.kill()
            self.player_add('Stone')
    
    def update(self,dt):
        if self.alive:
            self.check_death()
        

class Grass_Class(Generic):
    def __init__(self, pos, surf, groups, player_add):
        super().__init__(pos, surf, groups)
        self.health = 2
        self.alive = True

        self.player_add = player_add

    def damage(self):
        self.health -= 1

    def check_death(self):
        if self.health <= 0:
            Particle(self.rect.topleft, self.image, self.groups()[0], LAYERS['Death'], 300)
            self.alive = False
            self.kill()
            self.player_add('Seed')

    def update(self,dt):
        if self.alive:
            self.check_death()


