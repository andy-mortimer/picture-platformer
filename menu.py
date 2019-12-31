import pygame

grey=(210,210,210)

class Level(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()

pygame.init()

all_levels_group=pygame.sprite.Group()

size=(700,500)
screen=pygame.display.set_mode(size)
pygame.display.set_caption("menu")

levels=["assets/level1.png","assets/level2.png"]
levelnum=0
for item in levels:
	level = Level()
	orignal_image=pygame.image.load(item).convert_alpha()
	small_image=pygame.transform.scale(orignal_image,(200,200))
	level.rect = [25+(225*levelnum),33]
	level.image=small_image
	all_levels_group.add(level)
	levelnum+=1

carryOn = True
clock=pygame.time.Clock()
 
while carryOn:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                carryOn=False
        all_levels_group.update()
        screen.fill(grey)
        all_levels_group.draw(screen)
        pygame.display.flip()
        clock.tick(60)
pygame.quit()