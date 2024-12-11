import pygame
from settings import *
from player import *

class Overlay:
    def __init__(self,player):

        #general setup
        self.display_surface = pygame.display.get_surface()
        self.player = player

        overlay_path = 'graphics/overlay/'
        self.tools_surf = {tool: pygame.image.load(f'{overlay_path}{tool}.png').convert_alpha() for tool in player.tools}
        self.seeds_surf = {seed: pygame.image.load(f'{overlay_path}corn.png').convert_alpha() for seed in player.seeds}

        self.font = pygame.font.Font('font/LycheeSoda.ttf', 30)

    def display(self):

        #seed
        seed_surf = self.seeds_surf[self.player.selected_seed]
        seed_rect = seed_surf.get_rect(midbottom = (70, SCREEN_HEIGHT - 5))
        self.display_surface.blit(seed_surf,seed_rect)

        #tool
        tool_surf = self.tools_surf[self.player.selected_tool]
        tool_rect = tool_surf.get_rect(midbottom = (40, SCREEN_HEIGHT - 15))
        self.display_surface.blit(tool_surf,tool_rect)

        self.display_money()

    def display_money(self):
        # Render the money amount
        money_text = f'${self.player.money}'
        text_surf = self.font.render(money_text, True, 'Black')
        text_rect = text_surf.get_rect(midbottom=(SCREEN_WIDTH - 70, SCREEN_HEIGHT - 20))  # Position it at the bottom right

        # Draw a background rectangle for better visibility
        pygame.draw.rect(self.display_surface, 'White', text_rect.inflate(10, 10), 0, 4)
        self.display_surface.blit(text_surf, text_rect)