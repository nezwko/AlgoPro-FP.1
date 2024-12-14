import pygame

class Timer:
    def __init__(self, duration, func=None):
        self.duration = duration  #Duration of the timer in milliseconds
        self.func = func  #Optional function to call when the timer expires
        self.active = False  #Flag to indicate if the timer is active
        self.start_time = 0  #Variable to store the start time of the timer

    def activate(self):
        self.active = True  #Set the timer to active
        self.start_time = pygame.time.get_ticks()  #Record the current time in milliseconds

    def deactivate(self):
        self.active = False  #Set the timer to inactive
        self.start_time = 0  #Reset the start time

    def update(self):
        current_time = pygame.time.get_ticks()  #Get the current time in milliseconds
        #Check if the elapsed time since the start time is greater than or equal to the duration
        if current_time - self.start_time >= self.duration:             
            if self.func and self.start_time != 0:  #If a function is set and the timer has started
                self.func()  #Call the function
            self.deactivate()  #Deactivate the timer after the function is called

