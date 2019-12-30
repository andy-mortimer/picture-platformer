import pygame

def sprite_from_image(file, size):
	image = pygame.image.load(file)

	# set the transparent colour to the colour of the top left pixel
	# (this is ignored if the image has a transparent channel already)
	image.set_colorkey(image.get_at((0,0)))

	image = autocrop_by_colorkey(image)

	image = pygame.transform.scale(image, size)

	return image

def autocrop_by_colorkey(image):
	"""Crops an image using its colour key so the non-transparent 
	parts are touching the edge, and returns the cropped image"""

	# find the edges
	minx = miny = 0
	maxx = image.get_width() - 1
	maxy = image.get_height() - 1

	while minx < maxx and not column_contains_nontransparent_pixels(image, minx):
		minx += 1
	while maxx > minx and not column_contains_nontransparent_pixels(image, maxx):
		maxx -= 1
	while miny < maxy and not row_contains_nontransparent_pixels(image, miny):
		miny += 1
	while maxy > miny and not row_contains_nontransparent_pixels(image, maxy):
		maxy -= 1

	cropped = pygame.Surface((maxx - minx, maxy - miny))
	cropped.blit(image, (minx, miny), (minx, miny, maxx - minx, maxy - miny))
	cropped.set_colorkey(image.get_colorkey())
	return cropped

def column_contains_nontransparent_pixels(image, x):
	transparent = image.get_colorkey()
	for y in range(0, image.get_height()):
		if image.get_at((x, y)) != transparent:
			return True
	return False

def row_contains_nontransparent_pixels(image, y):
	transparent = image.get_colorkey()
	for x in range(0, image.get_width()):
		if image.get_at((x, y)) != transparent:
			return True
	return False

