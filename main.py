import pygame
import math

pygame.init()

top_border = bottom_border = 25
left_border = right_border = 10

# load the level image into a surface
# TODO there should be two: one for the display, one for the physics
level_image_name = 'level.jpg'
level_image = pygame.image.load(f'assets/{level_image_name}')
behaviour_image = pygame.image.load(f'assets/{level_image_name}')

def scale_down_by(surface, factor):
	new_surface = pygame.transform.scale(surface, 
		(int(surface.get_width()/factor), int(surface.get_height()/factor)))
	return new_surface

MAX_WINDOW_WIDTH=1200
MAX_WINDOW_HEIGHT=768
if behaviour_image.get_width() + left_border + right_border > MAX_WINDOW_WIDTH \
		or behaviour_image.get_height + top_border + bottom_border > MAX_WINDOW_HEIGHT:
	# scale by an integer (so no sampling oddities) to bring it under the max size
	x_scale = math.ceil(behaviour_image.get_width() / (MAX_WINDOW_WIDTH - left_border - right_border))
	y_scale = math.ceil(behaviour_image.get_height() / (MAX_WINDOW_HEIGHT - top_border - bottom_border))
	scale = max(x_scale, y_scale)
	print(f'scaling down by factor of {scale}')
	level_image = scale_down_by(level_image, scale)
	behaviour_image = scale_down_by(behaviour_image, scale)

print(f'image size: {behaviour_image.get_size()}')

# Open a new window
size = (behaviour_image.get_width() + left_border + right_border,
	behaviour_image.get_height() + top_border + bottom_border)
screen = pygame.display.set_mode(size)
pygame.display.set_caption(f"Picture Platformer: {level_image_name}")

BORDER=(200, 180, 180)

# The loop will carry on until the user exit the game (e.g. clicks the close button).
carryOn = True
 
# The clock will be used to control how fast the screen updates
clock = pygame.time.Clock()
 
# -------- Main Program Loop -----------
while carryOn:
    # --- Main event loop
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
              carryOn = False # Flag that we are done so we exit this loop
 
    # --- Game logic should go here

    # --- Drawing code should go here
    # First, clear the screen to white. 
    screen.fill(BORDER)
    screen.blit(level_image, (left_border, top_border))

    # --- Go ahead and update the screen with what we've drawn.
    pygame.display.flip()

    # --- Limit to 60 frames per second
    clock.tick(60)
 
#Once we have exited the main program loop we can stop the game engine:
pygame.quit()