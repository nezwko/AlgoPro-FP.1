import pygame
from settings import *
from timer import Timer
from ui import *

class Instructions:
    def __init__(self, player, toggle_instructions):
        #General setup
        self.player = player  #Reference to the player object
        self.toggle_instructions = toggle_instructions  #Function to toggle instructions visibility
        self.display_surface = pygame.display.get_surface()  #Get the current display surface

        # Load the instruction image
        self.instruction_image = pygame.image.load('instruction.jpg').convert_alpha()  #Load and convert the instruction image
        self.image_rect = self.instruction_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))  #Center the image

    def input(self):
        keys = pygame.key.get_pressed()  #Get the current state of all keyboard keys
        if keys[pygame.K_ESCAPE]:  
            self.toggle_instructions()  #Call the toggle function to hide instructions

    def update(self):
        self.input()  #Check for input every frame

    def draw(self):
        self.display_surface.blit(self.instruction_image, self.image_rect)  #Draw the instruction image on the display surface

class Menu:
    def __init__(self, player, toggle_menu):
        # General setup
        self.player = player  #Reference to the player object
        self.toggle_menu = toggle_menu  #Function to toggle menu visibility
        self.display_surface = pygame.display.get_surface()  #Get the current display surface
        self.font = pygame.font.Font('font/LycheeSoda.ttf', 30)  #Load the font for menu text

        # Options
        self.width = 400  #Width of the menu
        self.space = 10  #Space between menu entries
        self.padding = 8  #Padding around each entry

        # Entries
        self.options = list(self.player.item_inventory.keys()) + list(self.player.seed_inventory.keys())  #Combine item and seed inventories into options
        self.sell_border = len(self.player.item_inventory) - 1  #Index to differentiate between sell and buy options
        self.setup()  #Call setup to initialize text surfaces

        # Movement
        self.index = 0  #Current selected index in the menu
        self.timer = Timer(200)  #Timer to control input delay

        # Instruction toggle
        self.show_instructions = False  #Flag to show/hide instructions
        self.instructions = Instructions(self.player, self.toggle_instructions)  #Create an Instructions object

    def setup(self):
        #Create the text surfaces for each menu option
        self.text_surfs = []  #List to hold text surfaces
        self.total_height = 0  #Total height of the menu

        for item in self.options:
            text_surf = self.font.render(item, False, 'Black')  #Render the text surface for each item
            self.text_surfs.append(text_surf)  #Add the text surface to the list
            self.total_height += text_surf.get_height() + (self.padding * 2)  #Update total height

        self.total_height += (len(self.text_surfs) - 1) * self.space  #Add space between entries
        self.menu_top = SCREEN_HEIGHT / 2 - self.total_height / 2  #Calculate the top position of the menu
        self.main_rect = pygame.Rect(SCREEN_WIDTH / 2 - self.width / 2, self.menu_top, self.width, self.total_height)  #Create a rectangle for the menu

        # Buy / sell text surfaces
        self.buy_text = self.font.render('buy', False, 'Black')  #Render 'buy' text
        self.sell_text = self.font.render('sell', False, 'Black')  #Render 'sell' text

    def input(self):
        keys = pygame.key.get_pressed()  #Get the current state of all keyboard keys
        self.timer.update()  #Update the timer

        if keys[pygame.K_ESCAPE]:  #Press 'ESC' to close the menu
            self.toggle_menu()  #Call the toggle function to hide the menu

        if not self.timer.active:  
            if keys[pygame.K_w]: 
                self.index -= 1  
                self.timer.activate()  #Activate the timer to prevent rapid input

            if keys[pygame.K_s]: 
                self.index += 1 
                self.timer.activate()  # Activate the timer

            if keys[pygame.K_SPACE]:  
                self.timer.activate()  # Activate the timer

                #Get the currently selected item
                current_item = self.options[self.index]

                #Sell item logic
                if self.index <= self.sell_border:  #Check if the selected index is for selling
                    if self.player.item_inventory[current_item] > 0:  #Ensure the player has the item to sell
                        self.player.item_inventory[current_item] -= 1  #Decrease the item count
                        self.player.money += SALE_PRICES[current_item]  #Increase player's money by sale price

                # Buy item logic
                else:  #Buying seeds
                    seed_price = PURCHASE_PRICES[current_item]  #Get the price of the seed
                    if self.player.money >= seed_price:  #Check if the player has enough money
                        self.player.seed_inventory[current_item] += 1  #Increase the seed count
                        self.player.money -= seed_price  #Decrease player's money by seed price

        #Wrap the index to allow circular navigation
        if self.index < 0:  # If index goes below 0
            self.index = len(self.options) - 1  # Wrap to the last option
        if self.index > len(self.options) - 1:  # If index exceeds the number of options
            self.index = 0  # Wrap to the first option

    def toggle_instructions(self):
        self.show_instructions = not self.show_instructions  # Toggle the visibility of instructions

    def show_entry(self, text_surf, amount, top, selected):
        # Draw the background for the menu entry
        bg_rect = pygame.Rect(self.main_rect.left, top, self.width, text_surf.get_height() + (self.padding * 2))  # Create a rectangle for the entry background
        pygame.draw.rect(self.display_surface, 'White', bg_rect, 0, 4)  # Draw the background rectangle

        # Draw the text for the entry
        text_rect = text_surf.get_rect(midleft=(self.main_rect.left + 20, bg_rect.centery))  # Position the text
        self.display_surface.blit(text_surf, text_rect)  # Draw the text surface

        # Draw the amount of the item
        amount_surf = self.font.render(str(amount), False, 'Black')  # Render the amount text
        amount_rect = amount_surf.get_rect(midright=(self.main_rect.right - 20, bg_rect.centery))  # Position the amount text
        self.display_surface.blit(amount_surf, amount_rect)  # Draw the amount surface

        # Highlight the selected entry
        if selected:  # If this entry is selected
            pygame.draw.rect(self.display_surface, 'black', bg_rect, 4, 4)  # Draw a border around the selected entry
            if self.index <= self.sell_border:  # If selling
                pos_rect = self.sell_text.get_rect(midleft=(self.main_rect.left + 150, bg_rect.centery))  # Position the sell text
                self.display_surface.blit(self.sell_text, pos_rect)  # Draw the sell text
            else:  # If buying
                pos_rect = self.buy_text.get_rect(midleft=(self.main_rect.left + 150, bg_rect.centery))  # Position the buy text
                self.display_surface.blit(self.buy_text, pos_rect)  # Draw the buy text

    def update(self):
        if self.show_instructions:  # If instructions are to be shown
            self.instructions.update()  # Update the instructions
        else:  # Otherwise, update the menu input
            self.input()

        # Draw each entry in the menu
        for text_index, text_surf in enumerate(self.text_surfs):
            top = self.main_rect.top + text_index * (text_surf.get_height() + (self.padding * 2) + self.space)  # Calculate the top position for each entry
            amount_list = list(self.player.item_inventory.values()) + list(self.player.seed_inventory.values())  # Get the amounts for each item
            amount = amount_list[text_index]  # Get the amount for the current entry
            self.show_entry(text_surf, amount, top, self.index == text_index)  # Show the entry

    def draw(self):
        if self.show_instructions:  # If instructions are to be shown
            self.instructions.draw()  # Draw the instructions
        else:  # Otherwise, draw the menu entries
            for text_index, text_surf in enumerate(self.text_surfs):
                top = self.main_rect.top + text_index * (text_surf.get_height() + (self.padding * 2) + self.space)  # Calculate the top position for each entry
                amount_list = list(self.player.item_inventory.values()) + list(self.player.seed_inventory.values())  # Get the amounts for each item
                amount = amount_list[text_index]  # Get the amount for the current entry
                self.show_entry(text_surf, amount, top, self.index == text_index)  # Show the entry