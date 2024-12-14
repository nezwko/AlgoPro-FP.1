import pygame, sys
from settings import *
from spritelayer import Level        

class Game:                    
    def __init__(self):   
        pygame.init() #Initialize Pygame Modules
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) #Game Window Dimensions Set Up 
        pygame.display.set_caption('Sunny Sprouts') #Title on Window
        self.clock = pygame.time.Clock() #Initializes CLock to control the Game's Frame Rate
        self.level = Level() #Calls Level class, Assigning it to self.level 
                        
    def run(self): 
        while True: #Main Game Loop
            for event in pygame.event.get(): #Checks for user input
                if event.type == pygame.QUIT: #Checks if quitting is detected
                    pygame.quit() #All Modules Uninitializes
                    sys.exit() #If detected, Game ends, Program exits

            #Delta time (dt): The time that passes in between two consecutive frames.
            dt = self.clock.tick() / 1000 #Time is converted to Seconds from Milliseconds
            self.level.run(dt) #Update and Renders Level, passing delta time (dt)
            pygame.display.update() #Refreshes and shows updated frames

#Runs the Game
if __name__ ==  '__main__':
    game = Game()
    game.run() #Game Start