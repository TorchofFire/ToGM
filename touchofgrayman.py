import pygame
import csv
import math
import random
pygame.init()

window = pygame.display.set_mode((1680, 1050), pygame.FULLSCREEN)
window.set_alpha(None)
pygame.display.set_caption("Touch of Gray Man")
pygame.display.set_icon(pygame.transform.scale(pygame.image.load('images/player/player.png'), (32, 32)))

clock = pygame.time.Clock()

pixScale = 8 #the times the scale of image is multiplied

if __name__ == '__main__':
	from classes import Player
	from classes import Tile
	from classes import Rock


#debug vars
truePosDebug = False
showHitboxDebug = False

#global vars
level = 0
tiles = []
rocks = []
groundLines = []
permeableLines = []
backpack = []


def setWorld():
	global groundLines
	global permeableLines
	global tiles
	global rocks
	
	tileRenderOrder = ['dirt', 'dirtrock', 'stone', 'cstone', 'woodPlatform', 'woodPlatformEdgeR', 'woodPlatformEdgeL', 'grass']
	
	#reads ground files
	reader = csv.reader(open('levels/level'+str(level)+'/groundLines.csv', 'r'))
	groundLines = []
	for line in reader:
		groundLines.append([int(line[0])*pixScale, int(line[1])*pixScale, int(line[2])*pixScale, int(line[3])*pixScale])
	#reads permeable files
	reader = csv.reader(open('levels/level'+str(level)+'/permeableLines.csv', 'r'))
	permeableLines = []
	for line in reader:
		permeableLines.append([int(line[0])*pixScale, int(line[1])*pixScale, int(line[2])*pixScale, int(line[3])*pixScale])
	
	#reads tile files
	reader = csv.reader(open('levels/level'+str(level)+'/tiles.csv', 'r'))
	tiles = []
	
	for troIndex, tile in enumerate(tileRenderOrder):
		reader = csv.reader(open('levels/level'+str(level)+'/tiles.csv', 'r'))
		for index, line in enumerate(reader):
			for index2, item in enumerate(line):
				if item == tile:
					tiles.append(Tile(index2, index, item)) #adds tile entity
				elif not item in tileRenderOrder and troIndex == 0:
					if item == 'rock': #adds rock entity
						rocks.append(Rock(index2, index))
					elif not item == '0' and not item == '':
						print("couldn't assign '" +item+ "' to a tile on X " + str(index2) + ", Y " + str(index))




def getKeys():
	global run
	keys = pygame.key.get_pressed()
	if keys[pygame.K_ESCAPE]:
		run = False
	player.up = keys[pygame.K_w]
	player.right = keys[pygame.K_d]
	player.left = keys[pygame.K_a]
	player.down = keys[pygame.K_s]
	player.space = keys[pygame.K_SPACE]
	player.crouch = keys[pygame.K_l]
	player.attack = keys[pygame.K_j]
	player.interact = keys[pygame.K_k]
	player.throw = keys[pygame.K_i]


worldFocus = (6 *pixScale, -16 *pixScale)
worldOffset = (0,  0)
def scrollAll():
	global worldFocus
	global worldOffset
	
	worldFocus = (worldFocus[0] + (((player.x - 400) - worldFocus[0])/ 10), worldFocus[1])
	worldFocus = (worldFocus[0], worldFocus[1] + (((player.y - 400) - worldFocus[1])/ 10))
	
	if worldFocus[0] <= -4: #left screen border
		worldFocus = (-4, worldFocus[1])
	if worldFocus[1] >= 8 * (pixScale*pixScale): #bottom screen border
		worldFocus = (worldFocus[0], 8 * (pixScale*pixScale))
	
	worldOffset = (worldOffset[0] + (0 - round((((worldFocus[0] + worldOffset[0]))/8))), worldOffset[1])
	worldOffset = (worldOffset[0], worldOffset[1] + (0 - round((((worldFocus[1] + worldOffset[1]))/8))))
	if not truePosDebug:
		#vvv aligns to pixscale
		worldOffset = (round(worldOffset[0] / pixScale) * pixScale, round(worldOffset[1] / pixScale) * pixScale)
	
	player.offset = worldOffset
	for rock in rocks:
		rock.offset = worldOffset
	for tile in tiles:
		tile.offset = worldOffset
	
	

def rockCheckGroundCol(hitbox, rNum):
	rocks[rNum].hit = False
	xline = []
	yline = []
	x = hitbox[0]
	y = hitbox[1]
	width = hitbox[2]
	height = hitbox[3]
	
	
	#checks for groundLines
	for line in groundLines:
		if (x <= line[0]*pixScale or x <= line[2]*pixScale) and (x + width >= line[0]*pixScale or x + width >= line[2]*pixScale):
			xline.append(True)
		else:
			xline.append(False)
	for line in groundLines:
		if (y <= line[1]*pixScale or y <= line[3]*pixScale) and (y + height >= line[1]*pixScale or y + height >= line[3]*pixScale):
			yline.append(True)
		else:
			yline.append(False)
	for index, result in enumerate(xline):
		if result == True and yline[index] == True:
			rocks[rNum].hit = True
	
	#checks for permeable lines
	for line in permeableLines:
		if (x <= line[0]*pixScale or x <= line[2]*pixScale) and (x + width >= line[0]*pixScale or x + width >= line[2]*pixScale):
			xline.append(True)
		else:
			xline.append(False)
	for line in permeableLines:
		if (y <= line[1]*pixScale or y <= line[3]*pixScale) and (y + height >= line[1]*pixScale or y + height >= line[3]*pixScale):
			yline.append(True)
		else:
			yline.append(False)
	for index, result in enumerate(xline):
		if result == True and yline[index] == True:
			if rocks[rNum].ySpeed < 0:
				rocks[rNum].passing = True
			elif rocks[rNum].passing == False:
				rocks[rNum].hit = True
		else:
			rocks[rNum].passing = False

def checkGroundCol(hitbox):
	player.hit = False
	xline = []
	yline = []
	x = hitbox[0] - worldOffset[0]
	y = hitbox[1] - worldOffset[1]
	width = hitbox[2]
	height = hitbox[3]
	
	#checks for groundLines
	for line in groundLines:
		if (x <= line[0]*pixScale or x <= line[2]*pixScale) and (x + width >= line[0]*pixScale or x + width >= line[2]*pixScale):
			xline.append(True)
		else:
			xline.append(False)
	for line in groundLines:
		if (y <= line[1]*pixScale or y <= line[3]*pixScale) and (y + height >= line[1]*pixScale or y + height >= line[3]*pixScale):
			yline.append(True)
		else:
			yline.append(False)
	for index,  result in enumerate(xline):
		if result and yline[index]:
			player.hit = True
	
	#checks for permeableLines
	
	for line in permeableLines:
		if (x <= line[0]*pixScale or x <= line[2]*pixScale) and (x + width >= line[0]*pixScale or x + width >= line[2]*pixScale):
			xline.append(True)
		else:
			xline.append(False)
	for line in permeableLines:
		if (y <= line[1]*pixScale or y <= line[3]*pixScale) and (y + height >= line[1]*pixScale or y + height >= line[3]*pixScale):
			yline.append(True)
		else:
			yline.append(False)
	
	
	permHit = False
	for index, result in enumerate(xline):
		if result and yline[index]:
			permHit = True
	if permHit:
		if player.ySpeed <  0:
			player.passing = True
		if player.down:
			player.passing = True
		if not player.passing:
			player.hit = True
	else:
		if not player.down:
			player.passing = False



def rockLogic():
	if player.throw == False:
		player.throwing = False
	
	for index, rock in enumerate(rocks): #physics
		if rock.inBackpack:
			if player.throw and not player.throwing:
				player.throwing = True
				rock.stopped = 0
				rock.inBackpack = False
				backpack.remove("rock")
				rock.x = player.x - (1.5 * pixScale)
				rock.y = player.y
				if player.right:
					rock.xSpeed = 20
					rock.ySpeed = -10
				if player.left:
					rock.xSpeed = -20
					rock.ySpeed = -10
				if player.up:
					rock.ySpeed = -30
				if player.down:
					rock.ySpeed = 10
		else:
			if rock.moving: #self.moving is for proccessing efficiency
				#dealing with Y
				if rock.ySpeed < 32:
					rock.ySpeed += 1
				rock.y += round(rock.ySpeed)
				
				rock.updateHitbox()
				rockCheckGroundCol(rock.hitbox, index)
				friction = False
				bounce = False
				while rock.hit:
					if rock.ySpeed < 0:
						bounce = True
						rock.y += 1
						rock.updateHitbox()
						rockCheckGroundCol(rock.hitbox, index)
					else:
						bounce = True
						friction = True
						rock.y -= 1
						rock.updateHitbox()
						rockCheckGroundCol(rock.hitbox, index)
				if bounce:
					rock.ySpeed = 0 - round(rock.ySpeed / 3)
				#dealing with X
				if not rock.xSpeed == 0:
					if rock.xSpeed > 0:
						if friction:
							rock.xSpeed += -0.5
						else:
							rock.xSpeed += -0.2
					else:
						if friction:
							rock.xSpeed += 0.5
						else:
							rock.xSpeed += 0.2
				rock.x += round(rock.xSpeed)
				
				rock.updateHitbox()
				rockCheckGroundCol(rock.hitbox, index)
				bounce = False
				while rock.hit:
					bounce = True
					if rock.xSpeed > 0:
						rock.x += -1
					else:
						rock.x += 1
					rock.updateHitbox()
					rockCheckGroundCol(rock.hitbox, index)
				if bounce:
					rock.xSpeed = 0 - round(rock.xSpeed / 1.5)
				
				#VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV
				#
				#gotta add a way to detect if the rocks aren't moving to make proccessing efficient
				#
				#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
	
	if player.interact: #interact logic
		playerX = player.x + pixScale * 5
		playerY = player.y
		playerWidth = player.hitbox[2]
		playerHeight = player.hitbox[3]
		for rock in rocks:
			if not rock.inBackpack:
				rock.updateHitbox()
				rockX = rock.hitbox[0]
				rockY = rock.hitbox[1]
				rockWidth = rock.hitbox[2]
				rockHeight = rock.hitbox[3]
				if (rockX <= playerX + playerWidth and rockX + rockWidth >= playerX) and (rockY <= playerY + playerHeight and rockY + rockHeight >= playerY): #checks for intersection between rock and player
					rock.inBackpack = True
					backpack.append("rock")
					
				

def playerLogic():
	
	if player.crouch:
		player.attacking = 0
		player.height = 9 * pixScale
	else:
		player.height = 13 * pixScale
	
	if not (player.left or player.right):
		player.walk = 0
	player.walk += 1
	if player.walk >= 4 * 7:
		player.walk = 0
	
	#player attack scripts
	if player.attacking > 0:
		player.attacking += 1
	if player.attack and player.attacking == 0:
		player.attacking = 1
		if random.randint(1,2) == 2:
			player.attackType = 'side'
		else:
			player.attackType = 'circle'
			
	if player.attacking >= 4 * 3 or player.attacking == -1:
		if player.attack:
			player.attacking = -1
		else:
			player.attacking = 0
	
	#dealing with Y
	if player.ySpeed < 27:
		player.ySpeed += 1
	player.y += round(player.ySpeed)
	
	player.onGround += 1
	player.updateHitbox()
	checkGroundCol(player.hitbox)
	while player.hit:
		if player.ySpeed < 0:
			player.onGround = -1
			player.y += 1
			player.updateHitbox()
			checkGroundCol(player.hitbox)
		else:
			player.onGround = 0
			player.ySpeed = 0
			player.y += -1
			player.updateHitbox()
			checkGroundCol(player.hitbox)
	if player.onGround == -1:
		player.ySpeed = 0
		player.onGround = 50
	
	if player.onGround <= 10 and not player.crouch:
		if player.space and not player.jumped:
			player.ySpeed = -12.6
		elif not player.space and not player.onGround == 0:
			player.jumped = True
		elif player.onGround == 0:
			player.jumped = False
		
			
	
	#dealing with X
	if player.left and not player.crouch:
		if player.xSpeed >= -8:
			player.xSpeed += -0.7
	if player.right and not player.crouch:
		if player.xSpeed <= 8:
			player.xSpeed += 0.7
	if not (player.left or player.right) or (player.crouch and player.onGround <= 10):
		if not round(player.xSpeed) == 0:
			if player.xSpeed > 0:
				player.xSpeed += -0.7
			else:
				player.xSpeed += 0.7
	player.x += round(player.xSpeed)
	
	player.updateHitbox()
	checkGroundCol(player.hitbox)
	xspdset0 = False
	while player.hit:
		xspdset0 = True
		if player.xSpeed > 0:
			player.x += -1
			player.updateHitbox()
			checkGroundCol(player.hitbox)
		else:
			player.x += 1
			player.updateHitbox()
			checkGroundCol(player.hitbox)
	if xspdset0:
		player.xSpeed = 0
			
	
	#pit death
	if player.y > 25 * (pixScale * pixScale):
		player.x = 3 * (pixScale * pixScale)
		player.y = 18 * (pixScale * pixScale)
		player.xSpeed = 0
		player.ySpeed = 0

def render():
	window.fill((145, 216, 245))
	
	
	
	for tile in tiles:
		tile.draw(window, truePosDebug)
	for rock in rocks:
		if not rock.inBackpack:
			rock.draw(window, truePosDebug)
	
	player.draw(window, truePosDebug)
	
	for line in groundLines:
			if showHitboxDebug:
				pygame.draw.line(window, (255,0,0), ((line[0]*pixScale)+ worldOffset[0], (line[1]*pixScale)+ worldOffset[1]), ((line[2]*pixScale)+ worldOffset[0], (line[3]*pixScale)+ worldOffset[1]), 1)
	for line in permeableLines:
			if showHitboxDebug:
				pygame.draw.line(window, (200,0,255), ((line[0]*pixScale)+ worldOffset[0], (line[1]*pixScale)+ worldOffset[1]), ((line[2]*pixScale)+ worldOffset[0], (line[3]*pixScale)+ worldOffset[1]), 1)
	
	
	pygame.display.update()

if __name__ == '__main__':
	player = Player(3, 18)
	


	setWorld()

	#MAIN LOOP vvv
	run = True
	while run:
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
		
		getKeys()
		
		
		rockLogic()
		
		playerLogic()
		
		
		scrollAll()
		
		
		render()
		
		
		
		
		clock.tick(40)
		
	pygame.quit()
