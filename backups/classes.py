import pygame
import csv
import math
import random
from touchofgrayman import pixScale
from touchofgrayman import showHitboxDebug

class Player(object):
	idleImage = pygame.transform.scale(pygame.image.load('images/player/player.png'), (16 * pixScale, 16 * pixScale))
	jumpImage = pygame.transform.scale(pygame.image.load('images/player/jump.png'), (16 * pixScale, 16 * pixScale))
	fallImage = pygame.transform.scale(pygame.image.load('images/player/fall.png'), (16 * pixScale, 16 * pixScale))
	slideImage = pygame.transform.scale(pygame.image.load('images/player/slide.png'), (16 * pixScale, 16 * pixScale))
	crouchImage = pygame.transform.scale(pygame.image.load('images/player/crouch.png'), (16 * pixScale, 16 * pixScale))
	walkImage = []
	count = 0
	while count <= 7:
		walkImage.append(pygame.transform.scale(pygame.image.load('images/player/walk'+ str(count) +'.png'), (16 * pixScale, 16 * pixScale)))
		count += 1
	walk = 0
	lookright = True
	
	sideattackImage = []
	count = 0
	while count <= 3:
		sideattackImage.append(pygame.transform.scale(pygame.image.load('images/player/sideattack'+ str(count) +'.png'), (16 * pixScale, 16 * pixScale)))
		count += 1
	circleattackImage = []
	count = 0
	while count <= 3:
		circleattackImage.append(pygame.transform.scale(pygame.image.load('images/player/circleattack'+ str(count) +'.png'), (16 * pixScale, 16 * pixScale)))
		count += 1
	
	attacking = 0
	
	playerImage = idleImage
	
	
	
	def __init__(self, x, y):
		self.offset = (0, 0)
		
		self.up = False
		self.right = False
		self.left = False
		self.down = False
		self.space = False
		self.crouch = False
		self.attack = False
		self.attackType = 'side'
		self.interact = False
		self.throw = False
		
		self.x = x
		self.y = y
		self.x = self.x * (pixScale*pixScale)
		self.y = self.y * (pixScale*pixScale)
		self.width = 3 * pixScale
		self.height = 13 * pixScale
		self.xSpeed = 0
		self.ySpeed = 0
		self.hitbox = (self.x + (5 * pixScale), self.y + (2 * pixScale), self.width, self.height)#defines hitbox
		self.attackhitbox = (0, 0, 0, 0)
		self.onGround = 50
		self.passing = False
		self.hit = False
		self.jumped = False
		self.jumpkey = 0



	def draw(self, window, debug):
		if self.crouch:
			self.playerImage = self.crouchImage
		else:
			if self.attacking <= 0:
				if self.ySpeed == 0:
					if not (self.left or self.right):
						if abs(round(self.xSpeed)) > 0:
							self.playerImage = self.slideImage
						else:
							self.playerImage = self.idleImage
					else:
						self.playerImage = self.walkImage[round(self.walk / 4)]
				elif self.ySpeed > 0:
					if self.ySpeed > 16:
						self.playerImage = self.fallImage
					else:
						self.playerImage = self.idleImage
				else:
					self.playerImage = self.jumpImage
			else:
				if self.attackType == 'side':
					self.playerImage = self.sideattackImage[round(self.attacking / 4)]
				elif self.attackType == 'circle':
					self.playerImage = self.circleattackImage[round(self.attacking / 4)]
				
		if self.crouch:
			if self.right:
				self.lookright = True
			elif self.left:
				self.lookright = False
		else:	
			if not self.xSpeed == 0:
				if self.right:
					self.lookright = True
				elif self.left:
					self.lookright = False
				if self.right and self.left:
					if self.xSpeed > 0:
						self.lookright = True
					else:
						self.lookright = False
			
		if not self.lookright:
			self.playerImage = pygame.transform.flip(self.playerImage, 1, 0)
		
		
		self.x += self.offset[0] #adds offset for scrolling
		self.y += self.offset[1] #adds offset for scrolling
		if self.lookright:
			if debug:
				window.blit(self.playerImage, (self.x -pixScale, self.y +1))
			else:
				window.blit(self.playerImage, (round((self.x -pixScale) / pixScale) * pixScale, (round((self.y +0) / pixScale) * pixScale)))
		else: #offset needed because of image flip
			if debug:
				window.blit(self.playerImage, (self.x -pixScale*2, self.y +1))
			else:
				window.blit(self.playerImage, (round((self.x -pixScale*2) / pixScale) * pixScale, (round((self.y +0) / pixScale) * pixScale)))
		self.x -= self.offset[0] #removes the added offset
		self.y -= self.offset[1] #removes the added offset
		
		
		self.updateHitbox()
		if showHitboxDebug:
			pygame.draw.rect(window, (255,0,0), self.hitbox, 1)
		
		#dealing with attack hitbox now
		self.x += self.offset[0] #adds offset for scrolling
		self.y += self.offset[1] #adds offset for scrolling
		if self.attacking > 0:
			if self.lookright:
				self.attackhitbox = (self.x + (10 * pixScale), self.y + (4 * pixScale), 6 * pixScale, 8 * pixScale)
			else:
				self.attackhitbox = (self.x - (3 * pixScale), self.y + (4 * pixScale), 6 * pixScale, 8 * pixScale)
		else:
			self.attackhitbox = (0, 0, 0, 0)
		
		if showHitboxDebug:
			pygame.draw.rect(window, (0,0,200), self.attackhitbox, 1)
			
		self.x -= self.offset[0] #removes the added offset
		self.y -= self.offset[1] #removes the added offset
	
	def updateHitbox(self):
		self.hitbox = ((self.x + self.offset[0]) + (5 * pixScale), (self.y + self.offset[1]) + (2 * pixScale), self.width, self.height)#defines hitbox
		
	

class Rock(object):
	
	def __init__(self, x, y):
		self.offset = (0,0)
		
		self.inBackpack = False
		
		self.image = pygame.transform.scale(pygame.image.load('images/rock.png'), (16 * pixScale, 16 * pixScale))
		self.x = x
		self.y = y
		self.x = self.x * (pixScale*pixScale) - (pixScale * 4)
		self.y = self.y * (pixScale*pixScale) - (pixScale * 4)
		self.width = 4 * pixScale
		self.height = 4 * pixScale
		self.xSpeed = 0
		self.ySpeed = 0
		self.hitbox = (self.x + (6 * pixScale), self.y + (6 * pixScale), self.width, self.height)#defines hitbox
		self.hit = False
		
		
	def draw(self, window, debug):
		
		
		w, h = pygame.display.get_surface().get_size()
		if self.x + self.offset[0] < w and self.y + self.offset[1] < h:
			self.x += self.offset[0]
			self.y += self.offset[1]
			if debug:
				window.blit(self.image, (self.x, self.y))
			else:
				window.blit(self.image, (round(self.x / pixScale) * pixScale, round(self.y / pixScale) * pixScale))
			
			self.updateHitbox()
			
			if showHitboxDebug:
				pygame.draw.rect(window, (0,0,170), self.hitbox, 1)
			
			
			self.x -= self.offset[0]
			self.y -= self.offset[1]
			
		
	def updateHitbox(self):
		self.hitbox = (self.x + (6 * pixScale), self.y + (6 * pixScale), self.width, self.height)
	
	

class Tile(object):
	
	def __init__(self, x, y, gType):
		self.offset = (0,0)
		
		self.groundImage = pygame.transform.scale(pygame.image.load('images/tiles/' + gType + '.png'), (16 * pixScale, 16 * pixScale))
		flipTypes = ['grass', 'dirt', 'stone', 'cstone', 'woodPlatform']
		for tile in flipTypes:
			if gType == tile:
				if random.randint(1,2) == 2:
					self.groundImage = pygame.transform.flip(self.groundImage, 1, 0)
				if random.randint(1,2) == 2 and gType == 'dirt':
					self.groundImage = pygame.transform.flip(self.groundImage, 0, 1)
		self.x = x
		self.y = y
		self.x = self.x * (pixScale*pixScale) - (pixScale * 4)
		self.y = self.y * (pixScale*pixScale) - (pixScale * 4)
		self.width = 8 * pixScale
		self.height = 8 * pixScale
	def draw(self, window, debug):
		
		
		w, h = pygame.display.get_surface().get_size()
		if self.x + self.offset[0] < w and self.y + self.offset[1] < h:
			self.x += self.offset[0]
			self.y += self.offset[1]
			if debug:
				window.blit(self.groundImage, (self.x, self.y))
			else:
				window.blit(self.groundImage, (round(self.x / pixScale) * pixScale, round(self.y / pixScale) * pixScale))
				#print(self.x)
			self.x -= self.offset[0]
			self.y -= self.offset[1]
