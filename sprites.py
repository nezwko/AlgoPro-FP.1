import pygame
from settings import *
from timer import Timer
from spritelayer import *

#Generic Class is for all objects that need to be sprite-based
class Generic(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, z = LAYERS['Main']):
        super().__init__(groups) 
        #Calls and Initialize pygame.sprite.Sprite to add sprite to the groups
        self.image = surf #Sets the surface image for the sprite
        self.rect = self.image.get_rect(topleft = pos) #Creates rectangle around sprite at given position
        self.z = z #Layer for the order of rendering
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.75)

class Interaction(Generic):
    #Interaction class represents objects that are meant to be interacted
	def __init__(self, pos, size, groups, name):
		surf = pygame.Surface(size) #Creates a surface with given size
		super().__init__(pos, surf, groups) #Calls Generic Constructor
		self.name = name #Sets name for object

class Water(Generic):
    def __init__(self, pos, frames, groups):
        self.frames = frames #Stores water animation frames
        self.frame_index = 0 #Sets initial frame index to be 0, Hence, Starting at first frame
        
        #Calls Generic Constructor
        super().__init__(pos = pos,
                         surf = self.frames[self.frame_index],
                         groups = groups,
                         z = LAYERS['Water'])
        
    def animate(self,dt):
        #Function for animating water surface, Changing frames based on dt
        self.frame_index += 5 * dt #Increases frame index by a factor of 5 and dt
        #5 is a scaling factor that controls how fast the frame index increases.
        if self.frame_index >= len(self.frames): #If end of frame is reached,
            self.frame_index = 0 #it will be reset to first frame
        self.image = self.frames[int(self.frame_index)] #Updates sprite image to new frame
    
    def update(self,dt):
        #Function to update water's animation state
        self.animate(dt)

        
class Particle(Generic):
    #Class Particle is for visual effects animation
    def __init__ (self, pos, surf, groups, z, duration = 200):
        super().__init__(pos, surf, groups, z) #Inherits from Generic Class
        self.start_time = pygame.time.get_ticks() #Records the start time of the particle
        self.duration = duration 
        #Defines how long the visual effects lasts before being removed.

        #Masks sprite image, allows transparency
        mask_surf = pygame.mask.from_surface(self.image)
        new_surf = mask_surf.to_surface() 
        new_surf.set_colorkey((0,0,0)) #Remove black pixels
        self.image = new_surf #Updates image with transparency
        
    def update(self,dt):
        #To check if particle's time has passed
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time > self.duration:
            self.kill() #If it does, it is killed.


class Log_Class(Generic): 
    #Class Log_Class is for logs that can be destroyed and collected as Wood.
    def __init__(self, pos, surf, groups, player_add):
        super().__init__(pos, surf, groups) #Inherits from Generic Class
        self.health = 3 #Initializes the health as 3
        self.alive = True #Log is alive as default

        self.player_add = player_add #Function to add item

    def damage(self):
        self.health -= 1 #Decreases health by 1 when damaged

    def check_death(self):
        if self.health <= 0: #Checks if health is gone
            Particle(self.rect.topleft, self.image, self.groups()[0], LAYERS['Main'])
            #Calls the Particle Class
            self.alive = False #Log set as dead
            self.kill() #Removes log from game
            self.player_add('Wood') #Wood added to inventory
    
    def update(self,dt):
        if self.alive: #Check if log is alive
            self.check_death() #Check if log is dead
        

class Rock_Class(Generic):
    #Similar to Log Class
    def __init__(self, pos, surf, groups, player_add):
        super().__init__(pos, surf, groups)
        self.health = 4
        self.alive = True

        self.player_add = player_add

    def damage(self):
        self.health -= 1

    def check_death(self):
        if self.health <= 0: 
            Particle(self.rect.topleft, self.image, self.groups()[0], LAYERS['Main'])
            self.alive = False
            self.player_add('Stone')
            self.kill()
            
    
    def update(self,dt):
        if self.alive:
            self.check_death()
        

class Grass_Class(Generic):
    #Similar to Log Class
    def __init__(self, pos, surf, groups, player_add):
        super().__init__(pos, surf, groups)
        self.health = 2
        self.alive = True

        self.player_add = player_add

    def damage(self):
        self.health -= 1

    def check_death(self):
        if self.health <= 0:
            Particle(self.rect.topleft, self.image, self.groups()[0], LAYERS['Main'])
            self.alive = False
            self.kill()
            self.player_add('Seed')

    def update(self,dt):
        if self.alive:
            self.check_death()


