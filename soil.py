import pygame
from settings import *
from pytmx.util_pygame import load_pygame
from support import *
from random import choice

class SoilTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)  #Initialize the parent class to register the sprite with groups
        self.image = surf  # et the surface image for the tile
        self.rect = self.image.get_rect(topleft=pos)  #Set the position of the tile using its top-left corner
        self.z = LAYERS['Soil']  #Set the 'z' order for rendering based on its layer

class WaterTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)  #Initialize the parent class to register the sprite with groups
        self.image = surf  #Set the surface for the water tile
        self.rect = self.image.get_rect(topleft=pos)  #Set the position of the tile
        self.z = LAYERS['Watered Soil']  #Set the rendering layer order for the water tiles

class Plant(pygame.sprite.Sprite):
    def __init__(self, plant_type, groups, soil, check_watered):
        super().__init__(groups)  #Register the plant in sprite groups
        self.plant_type = plant_type  #Define the plant type
        self.frames = import_folder('graphics/fruit/corn')  #Load all frames for plant growth stages
        self.soil = soil  #The soil object where the plant is growing
        self.check_watered = check_watered  #Function to check if the plant is watered

        self.age = 0  #Initial age of the plant (starting at 0)
        self.max_age = len(self.frames) - 1  #Maximum age corresponds to the number of growth stages
        self.harvestable = False  #Initially, the plant is not harvestable

        self.image = self.frames[self.age]  #Set the initial image/frame for the plant
        self.y_offset = -16  #Y offset to position the plant above the soil tile
        self.rect = self.image.get_rect(midbottom=soil.rect.midbottom + pygame.math.Vector2(0, self.y_offset))  #Position the plant above the soil
        self.z = LAYERS['Plant']  #Set the z-order for rendering the plant (higher than soil)


    def grow(self):
        # Check if the plant is watered by calling check_watered function
        if self.check_watered(self.rect.center):
            # If the plant is not fully grown, it will grow to the next stage
            if self.age < self.max_age:
                self.age += 1  # Increase the plant age
                self.image = self.frames[self.age]  # Change the plant's image to the next growth stage
                self.rect = self.image.get_rect(midbottom=self.soil.rect.midbottom + pygame.math.Vector2(0, self.y_offset))  # Update position based on growth

            # Once fully grown, the plant becomes harvestable
            if self.age == self.max_age:
                self.harvestable = True

class SoilLayer:
    def __init__(self, all_sprites):
        #Sprite groups
        self.all_sprites = all_sprites
        self.soil_sprites = pygame.sprite.Group()
        self.water_sprites = pygame.sprite.Group()
        self.plant_sprites = pygame.sprite.Group()

        #Graphics
        self.soil_surfs = import_folder_dict('graphics/soil')
        self.water_surfs = import_folder('graphics/soil_water')

        self.grid = self.create_soil_grid()
        self.create_hit_rects()

    def create_soil_grid(self):
        h_tiles = 100
        v_tiles = 80

        #Initialize the grid as a 2D list of lists
        grid = [[[] for _ in range(h_tiles)] for _ in range(v_tiles)]
        
        #Load the tile map and populate the grid
        for x, y, _ in load_pygame('MAP.tmx').get_layer_by_name('Farmable').tiles():
            if 0 <= x < h_tiles and 0 <= y < v_tiles:  #Ensure x and y are within bounds
                grid[y][x].append('F')  #Set the cell to contain 'F'

        return grid
    
    def create_hit_rects(self):
        self.hit_rects = []  # List to store collision rectangles for the soil tiles
        # Iterate over the soil grid and create a rectangle for each valid soil tile ('F' in grid)
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'F' in cell:
                    x = index_col * TILE_SIZE  # Calculate x position for the tile
                    y = index_row * TILE_SIZE  # Calculate y position for the tile
                    rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)  # Create rectangle for the tile
                    self.hit_rects.append(rect)  # Add rectangle to the list

    def get_hit(self, point):
        # Check if any of the soil hit rectangles are clicked (colliding with point)
        for rect in self.hit_rects:
            if rect.collidepoint(point):  # If the point collides with this rectangle
                x = rect.x // TILE_SIZE  # Get x coordinate in grid
                y = rect.y // TILE_SIZE  # Get y coordinate in grid
                if 0 <= y < len(self.grid) and 0 <= x < len(self.grid[0]):
                    if 'F' in self.grid[y][x]:  # If the tile is farmable ('F')
                        self.grid[y][x].append('X')  # Mark it as clicked ('X')
                        self.create_soil_tiles()  # Recreate the soil tiles after modification
    
    def water(self, target_pos):
    # Water the soil at the specified position
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(target_pos):  # If the water target intersects with a soil tile
                x = soil_sprite.rect.x // TILE_SIZE  # Get x coordinate of the tile in the grid
                y = soil_sprite.rect.y // TILE_SIZE  # Get y coordinate of the tile in the grid
                self.grid[y][x].append('W')  # Add water marker 'W' to the tile in the grid

                pos = soil_sprite.rect.topleft  # Get the top-left position of the soil sprite
                surf = choice(self.water_surfs)  # Randomly choose a water tile graphic
                WaterTile(pos, surf, [self.all_sprites, self.water_sprites])  # Create a water tile sprite

                self.update_plants()  # Update the plants after watering

    def remove_water(self):
        # Remove all water tiles (sprites) and update the grid
        for sprite in self.water_sprites.sprites():
            sprite.kill()  # Remove the water sprite

        # Clean up water markers in the soil grid
        for row in self.grid:
            for cell in row:
                if 'W' in cell:
                    cell.remove('W')  # Remove the 'W' marker indicating water

    def check_watered(self, pos):
        # Check if the given position has been watered (contains 'W' in the grid)
        x = pos[0] // TILE_SIZE  # Get the x index in the grid
        y = pos[1] // TILE_SIZE  # Get the y index in the grid
        cell = self.grid[y][x]  # Access the cell in the grid
        is_watered = 'W' in cell  # Check if it has a 'W' (water) marker
        return is_watered  # Return True or False based on whether the cell is watered

    def plant_seed(self, target_pos, seed):
        # Plant a seed at the specified position, provided the position isn't occupied by another plant
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(target_pos):  # If a soil tile is clicked
                x = soil_sprite.rect.x // TILE_SIZE  # Get x coordinate of the tile
                y = soil_sprite.rect.y // TILE_SIZE  # Get y coordinate of the tile

                # Ensure the tile is empty ('P' not present) before planting
                if 'P' not in self.grid[y][x]:
                    self.grid[y][x].append('P')  # Mark the tile with 'P' for plant
                    # Create a new plant (seed) on the soil, passing in the check_watered function
                    Plant(seed, [self.all_sprites, self.plant_sprites], soil_sprite, self.check_watered)
    
    def update_plants(self):
        # Update all plants' growth
        for plant in self.plant_sprites.sprites():
            plant.grow()  # Call the grow method for each plant, which updates their growth stages


    def create_soil_tiles(self):
        # Rebuild the soil tiles based on the grid configuration
        self.soil_sprites.empty()  # Clear the existing soil sprites
        for index_row, row in enumerate(self.grid):  # Iterate through the grid
            for index_col, cell in enumerate(row):
                if 'X' in cell:  # If the cell is farmable
                    
                    #tile options
                    t = 'X' in self.grid[index_row - 1][index_col]
                    b = 'X' in self.grid[index_row + 1][index_col]
                    r = 'X' in row[index_col + 1]
                    l = 'X' in row[index_col - 1]

                    tile_type = 'o'

					# all sides
                    if all((t,r,b,l)): tile_type = 'x'

                    # horizontal tiles only
                    if l and not any((t,r,b)): tile_type = 'r'
                    if r and not any((t,l,b)): tile_type = 'l'
                    if r and l and not any((t,b)): tile_type = 'lr'

                    # vertical only 
                    if t and not any((r,l,b)): tile_type = 'b'
                    if b and not any((r,l,t)): tile_type = 't'
                    if b and t and not any((r,l)): tile_type = 'tb'

                    # corners 
                    if l and b and not any((t,r)): tile_type = 'tr'
                    if r and b and not any((t,l)): tile_type = 'tl'
                    if l and t and not any((b,r)): tile_type = 'br'
                    if r and t and not any((b,l)): tile_type = 'bl'

                    # T shapes
                    if all((t,b,r)) and not l: tile_type = 'tbr'
                    if all((t,b,l)) and not r: tile_type = 'tbl'
                    if all((l,r,t)) and not b: tile_type = 'lrb'
                    if all((l,r,b)) and not t: tile_type = 'lrt'

                    SoilTile(
                        pos=(index_col * TILE_SIZE, index_row * TILE_SIZE),
                        surf=self.soil_surfs[tile_type],
                        groups=[self.all_sprites, self.soil_sprites]
                    )