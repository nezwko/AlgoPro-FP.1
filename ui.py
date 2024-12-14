import pygame
from settings import *
from player import *

class Overlay:
    def __init__(self, player):
        #General setup
        self.display_surface = pygame.display.get_surface()  #Get the current display surface
        self.player = player  #Reference to the player object

        overlay_path = 'graphics/overlay/'  #Path to the overlay graphics
        #Load tool images into a dictionary, using the player's tools as keys
        self.tools_surf = {tool: pygame.image.load(f'{overlay_path}{tool}.png').convert_alpha() for tool in player.tools}
        #Load seed images into a dictionary, using the player's seeds as keys (currently only loading corn)
        self.seeds_surf = {seed: pygame.image.load(f'{overlay_path}corn.png').convert_alpha() for seed in player.seeds}

        self.font = pygame.font.Font('font/LycheeSoda.ttf', 30)  #Load the font for displaying text

    def display(self):
        #Display the currently selected seed
        seed_surf = self.seeds_surf[self.player.selected_seed]  #Get the surface for the selected seed
        seed_rect = seed_surf.get_rect(midbottom=(70, SCREEN_HEIGHT - 5))  #Position it at the bottom left
        self.display_surface.blit(seed_surf, seed_rect)  #Draw the seed surface on the display

        #Display the currently selected tool
        tool_surf = self.tools_surf[self.player.selected_tool]  #Get the surface for the selected tool
        tool_rect = tool_surf.get_rect(midbottom=(40, SCREEN_HEIGHT - 15))  #Position it just above the seed
        self.display_surface.blit(tool_surf, tool_rect)  #Draw the tool surface on the display

        self.display_money() 

    def display_money(self):
        #Render the money amount
        money_text = f'${self.player.money}'  #Format the money amount as a string
        text_surf = self.font.render(money_text, True, 'Black')  #Create a text surface for the money amount
        text_rect = text_surf.get_rect(midbottom=(SCREEN_WIDTH - 70, SCREEN_HEIGHT - 20))  #Position it at the bottom right

        # Draw a background rectangle for better visibility
        pygame.draw.rect(self.display_surface, 'White', text_rect.inflate(10, 10), 0, 4)  #Draw a white rectangle behind the text
        self.display_surface.blit(text_surf, text_rect)  #Draw the money text surface on the display