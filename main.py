import pygame
import math

pygame.init()

top_border = 75
bottom_border = 25
left_border = right_border = 10
level_offset = (left_border, top_border)

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

level_width = behaviour_image.get_width()
level_height = behaviour_image.get_height()

# Open a new window
size = (level_width + left_border + right_border,
	level_height + top_border + bottom_border)
screen = pygame.display.set_mode(size)
pygame.display.set_caption(f"Picture Platformer: {level_image_name}")

BORDER_COLOR=(200, 180, 180)
FOOTER_TEXT_COLOR=(255, 245, 245)

footer_font = pygame.font.Font('freesansbold.ttf', 12)


player_sprites = pygame.sprite.Group()


class Player(pygame.sprite.Sprite):
	def __init__(self, starting_pos):
		super().__init__()

		width = 32
		height = 32
		WHITE=(255, 255, 255)
		self.image = pygame.Surface([width, height])
		self.image.fill(WHITE)
		self.image.set_colorkey(WHITE)

		# Draw the car (a rectangle!)
		pygame.draw.rect(self.image, (255, 120, 120), [0, 0, width, height])

		self.rect = self.image.get_rect()
		self.rect.x = starting_pos[0] - (width/2) + left_border
		self.rect.y = starting_pos[1] - (height/2) + top_border

	def update(self):
		self.rect.y = self.rect.y + 1

# The loop will carry on until the user exit the game (e.g. clicks the close button).
carryOn = True
 
# The clock will be used to control how fast the screen updates
clock = pygame.time.Clock()

# -------- Main Program Loop -----------
while carryOn:
    # --- Main event loop

    # check whether the mouse is inside the actual level
    mouse_pos_rel = (pygame.mouse.get_pos()[0] - left_border,
    	pygame.mouse.get_pos()[1] - top_border)
    mouse_in_level = (mouse_pos_rel[0] >= 0 and mouse_pos_rel[0] < level_width
    	and mouse_pos_rel[1] >= 0 and mouse_pos_rel[1] < level_height)

    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
              carryOn = False # Flag that we are done so we exit this loop
        elif event.type == pygame.MOUSEBUTTONDOWN:
        	if mouse_in_level:
        		new_player_sprite = Player(mouse_pos_rel)
        		player_sprites.add(new_player_sprite)
 
    # --- Game logic should go here

    player_sprites.update()

    # --- Drawing code should go here
    # First, clear the screen to white. 
    screen.fill(BORDER_COLOR)

    # game window
    screen.blit(level_image, (left_border, top_border))

    player_sprites.draw(screen)

    # footer
    if mouse_in_level:
	    mouse_pos_text = footer_font.render(f'Mouse: {mouse_pos_rel}', True, FOOTER_TEXT_COLOR, BORDER_COLOR)
	    screen.blit(mouse_pos_text, (left_border, top_border + behaviour_image.get_height()))

    # --- Go ahead and update the screen with what we've drawn.
    pygame.display.flip()

    # --- Limit to 60 frames per second
    clock.tick(60)
 
#Once we have exited the main program loop we can stop the game engine:
pygame.quit()