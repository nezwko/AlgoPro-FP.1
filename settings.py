from pygame.math import Vector2
# screen
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TILE_SIZE = 64
NEW_TILE_SIZE = 16
UPSCALE_FACTOR = 4
NEW_TILE_SIZE_UPSCALED = NEW_TILE_SIZE * UPSCALE_FACTOR
GROWTH_TIME = 10
FPS = 60
NUM_STAGES = 4

# overlay positions 
OVERLAY_POSITIONS = {
	'tool' : (40, SCREEN_HEIGHT - 15), 
	'seed': (70, SCREEN_HEIGHT - 5)}

PLAYER_TOOL_OFFSET = {
	'left': Vector2(-50,40),
	'right': Vector2(50,40),
	'up': Vector2(0,-10),
	'down': Vector2(0,50)
}

LAYERS = {
	'Water': 0,
    'Land': 1,
    'Soil': 2,
    'Watered Soil': 3,
    'Flower': 4,
    'Plant': 5,
    'Rock': 6,
    'Grass': 7,
    'Tree': 8,
    'Bridge': 9,
    'Logs': 10,
    'Death': 11,
    'Main': 12,
}

SALE_PRICES = {
	'Wood': 4,
	'Stone': 2,
	'Wheat': 10,
}
PURCHASE_PRICES = {
	'Seed': 4,
}
