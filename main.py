import pygame
import math
import argparse

import sprite_loader

argparse = argparse.ArgumentParser()
argparse.add_argument('--level', type=str, default='assets/level.jpg')
args = argparse.parse_args()

pygame.init()

top_border = 75
bottom_border = 25
left_border = right_border = 10
level_offset = (left_border, top_border)

WALK_SPEED = 3
FALL_SPEED = 4
JUMP_SPEED = 4
JUMP_HEIGHT = 80

COLOR_WALL = (0, 0, 0)
COLOR_KILL = (255, 0, 0)

# load the level image into a surface
# TODO there should be two: one for the display, one for the physics
level_image_name = args.level
level_image = pygame.image.load(f'{level_image_name}')
behaviour_image = pygame.image.load(f'{level_image_name}')

def scale_down_by(surface, factor):
    new_surface = pygame.transform.scale(surface, 
        (int(surface.get_width()/factor), int(surface.get_height()/factor)))
    return new_surface

MAX_WINDOW_WIDTH=1200
MAX_WINDOW_HEIGHT=768
if behaviour_image.get_width() + left_border + right_border > MAX_WINDOW_WIDTH \
        or behaviour_image.get_height() + top_border + bottom_border > MAX_WINDOW_HEIGHT:
    # scale by an integer (so no sampling oddities) to bring it under the max size
    x_scale = math.ceil(behaviour_image.get_width() / (MAX_WINDOW_WIDTH - left_border - right_border))
    y_scale = math.ceil(behaviour_image.get_height() / (MAX_WINDOW_HEIGHT - top_border - bottom_border))
    scale = max(x_scale, y_scale)
    print(f'scaling down by factor of {scale}')
    level_image = scale_down_by(level_image, scale)
    behaviour_image = scale_down_by(behaviour_image, scale)

level_width = behaviour_image.get_width()
level_height = behaviour_image.get_height()

player_sprite_normal_name = 'player-sprite-normal.jpg'
player_sprite_normal = sprite_loader.sprite_from_image(f'assets/{player_sprite_normal_name}', (32, 32))

# Open a new window
size = (level_width + left_border + right_border,
    level_height + top_border + bottom_border)
screen = pygame.display.set_mode(size)
pygame.display.set_caption(f"Picture Platformer: {level_image_name}")

BORDER_COLOR=(200, 180, 180)
FOOTER_TEXT_COLOR=(255, 245, 245)

footer_font = pygame.font.Font('freesansbold.ttf', 12)


class WorldPhysics:
    def __init__(self, behaviour_image):
        self.image = behaviour_image

    def _check_for_colors_in_region(self, rel_rect, colors):
        """checks the region for a pixel of the specified colour, and returns the first
        colour found, or None if none of them are found"""
        seen_colors = {}
        for x_off in range(rel_rect.width):
            for y_off in range(rel_rect.height):
                # heuristic: assume pixels outside the image are all black
                if rel_rect.x + x_off < 0 or rel_rect.x + x_off >= self.image.get_width() \
                    or rel_rect.y + y_off < 0 or rel_rect.y + y_off >= self.image.get_height():
                    color = (0, 0, 0)
                else:
                    color = self.image.get_at((rel_rect.x + x_off, rel_rect.y + y_off))

                # force removal of alpha channel
                color = (color[0], color[1], color[2])

                if color in colors:
                    return color

                seen_colors[color] = 1

        return None

    def collides(self, rect):
        """Checks for collisions between the given sprite and the fixed scene."""
        rel_rect = rect.move(-left_border, -top_border)
        return self._check_for_colors_in_region(rel_rect, [COLOR_WALL]) is not None

    def should_die(self, rect):
        rel_rect = rect.move(-left_border, -top_border)
        return self._check_for_colors_in_region(rel_rect, [COLOR_KILL]) is not None


    def apply_horizontal_move(self, rect, offset):
        new_rect = rect.move(offset, 0)
        if not self.collides(new_rect):
            return new_rect

        # we can go up "shallow" slopes, i.e. max one-pixel steps
        new_rect = new_rect.move(0, -1)
        if not self.collides(new_rect):
            return new_rect

        # nope, no movement possible
        return rect

    def apply_fall(self, rect):
        new_rect = rect.move(0, 1)
        if not self.collides(new_rect):
            return new_rect
        else:
            return rect

    def apply_jump_1px(self, rect):
        new_rect = rect.move(0, -1)
        if not self.collides(new_rect):
            return new_rect
        else:
            return rect

physics = WorldPhysics(behaviour_image)


class PlayerSprite(pygame.sprite.Sprite):
    def __init__(self, starting_pos, physics):
        super().__init__()

        self.physics = physics

        self.is_jumping = False

        width = 32
        height = 32
        WHITE=(255, 255, 255)
        self.image = player_sprite_normal

        self.rect = self.image.get_rect()
        self.rect.x = starting_pos[0] - (width/2) + left_border
        self.rect.y = starting_pos[1] - (height/2) + top_border

    def update(self, direction, jump):
        new_rect = self.rect.copy()

        if jump and not self.is_jumping:
            # are we OK to jump? Yes, if we are resting on the ground.
            # rather than tracking jumping and falling etc, let's just see
            # whether we would fall later
            fallen_rect = self.rect.move(0, 1)
            if self.physics.collides(fallen_rect):
                # yes, on the ground, we can start the jump
                self.start_jump(height = JUMP_HEIGHT, frames = JUMP_HEIGHT / JUMP_SPEED)

        # 1. apply jump if jumping
        suppress_fall = False
        if self.is_jumping:
            # hacky way to calculate how many frames to move for a junp
            # TODO do this better
            jump_by = int(self.jump_height / self.jump_frames)
            # move up n pixels by moving one pixel n times, so that we get
            # the collisions right
            jump_ended = False
            for n in range(jump_by):
                jumped_rect = self.physics.apply_jump_1px(new_rect)
                if jumped_rect == new_rect:
                    # as soon as we hit the ceiling, stop going up
                    jump_ended = True
                    break
                else:
                    new_rect = jumped_rect
                self.jump_height -= 1
            
            self.jump_frames -= 1
            suppress_fall = True

            if jump_ended or self.jump_frames == 0:
                self.end_jump()
        
        # 1. move left or right if needed
        if direction == 'left':
            for n in range(WALK_SPEED):
                new_rect = self.physics.apply_horizontal_move(new_rect, -1)
        elif direction == 'right':
            for n in range(WALK_SPEED):
                new_rect = self.physics.apply_horizontal_move(new_rect, 1)

        if not suppress_fall:
            for n in range(FALL_SPEED):
                new_rect = self.physics.apply_fall(new_rect)

        self.rect = new_rect

    def start_jump(self, height, frames):
        self.is_jumping = True
        self.jump_frames = frames
        self.jump_height = height

    def end_jump(self):
        self.is_jumping = False
        self.jump_frames = self.jump_height = None

    def debug_text(self):
        text = f'Player @({self.rect.x}, {self.rect.y})'
        if self.is_jumping:
            text += f' JUMP remaining {self.jump_height}px {self.jump_frames} frames'
        return text


player_sprite = None

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
                if player_sprite is not None:
                    player_sprite.kill()
                player_sprite = PlayerSprite(mouse_pos_rel, physics)
 
    # --- Game logic should go here

    keys = pygame.key.get_pressed()  #checking pressed keys
    direction = None
    jump = False
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        direction = 'left'
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        direction = 'right'
    if keys[pygame.K_SPACE]:
        jump = True
    if keys[pygame.K_ESCAPE]:
        carryOn = False

    if player_sprite is not None:
        player_sprite.update(direction, jump)

    # check for death
    # TODO do this inside the update, as here we risk skipping some
    # intermediate frames
    if player_sprite is not None and physics.should_die(player_sprite.rect):
        # TODO kill animation
        player_sprite = None

    # --- Drawing code should go here
    # First, clear the screen to white. 
    screen.fill(BORDER_COLOR)

    # game window
    screen.blit(level_image, (left_border, top_border))

    if player_sprite is not None:
        screen.blit(player_sprite.image, player_sprite.rect)

    # footer
    if player_sprite is not None:
        footer_text = player_sprite.debug_text()
        footer_surface = footer_font.render(footer_text, True, FOOTER_TEXT_COLOR, BORDER_COLOR)
        screen.blit(footer_surface, (left_border, top_border + behaviour_image.get_height()))

    # --- Go ahead and update the screen with what we've drawn.
    pygame.display.flip()

    # --- Limit to 60 frames per second
    clock.tick(60)
 
#Once we have exited the main program loop we can stop the game engine:
pygame.quit()