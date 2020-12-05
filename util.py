# Author: Shway Wang
# Date: 2020/12/5
import pygame
import random
# --- Globals ---
# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
# Directions of snake:
UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3

class Food(object):
	''' Class to represent a unit of food. '''
	# Construction function:
	def __init__(self, snake_segments = [], w = 18, h = 18):
		# initialize the drawable:
		self.allspriteslist = pygame.sprite.Group()
		# construct food body:
		self.food = Segment(color = RED)
		self.generate_food(snake_segments)

	def draw_food(self, screen):
		self.allspriteslist.draw(screen)

	def get_food_pos(self):
		return (self.food.rect.x, self.food.rect.y)

	def generate_food(self, snake_segments, regenerate = False):
		if regenerate:
			self.allspriteslist.remove(self.food)
		# food should not over lap with snake:
		while True:
			self.food.rect.x = random.randint(0, 33) * 21 + 35
			self.food.rect.y = random.randint(0, 24) * 21 + 30
			bad_food = False
			for s in snake_segments:
				if s.rect.x == self.food.rect.x and s.rect.y == self.food.rect.y:
					bad_food = True
					break
			if bad_food:
				continue
			self.allspriteslist.add(self.food)
			break

class Snake(object):
	""" Class to represent the snake. """
	# -- Methods
	# Constructor function
	def __init__(self, snake_len = 5, seg_w = 18, seg_h = 18, seg_m = 3):
		# initialize the drawable:
		self.allspriteslist = pygame.sprite.Group()
		# Set the width and height of each snake segment
		self.seg_w = seg_w
		self.seg_h = seg_h
		# Create an initial snake
		self.snake_len = snake_len
		self.snake_segments = []
		# Margin between each segment
		self.seg_m = seg_m
		# Set initial speed
		self.x_change = self.seg_w + self.seg_m
		self.y_change = 0
		# Set initial direction:
		self.direction = RIGHT
		for i in range(self.snake_len):
			x = 245 - (self.seg_w + self.seg_m) * i
			y = 30
			segment = Segment(x, y, self.seg_w, self.seg_h)
			self.snake_segments.append(segment)
			self.allspriteslist.add(segment)

	def get_snake_head_pos(self):
		return [self.snake_segments[0].rect.x, self.snake_segments[0].rect.y]

	def get_snake_length(self):
		return len(self.snake_segments)

	def take_one_step(self, food):
		# Figure out where new segment will be
		x = self.snake_segments[0].rect.x + self.x_change
		y = self.snake_segments[0].rect.y + self.y_change
		segment = Segment(x, y, self.seg_w, self.seg_h)
		self.eat_food((x, y), food) # the food is only consumed if the positions align
		# Insert new segment into the list
		self.snake_segments.insert(0, segment)
		self.allspriteslist.add(segment)

	def eat_food(self, snake_pos, food):
		# see if the food is ate:
		if snake_pos == food.get_food_pos(): # if ate, keep the last segment
			# generate new food
			food.generate_food(self.snake_segments, True)
		else: # if not ate, delete the last segment
			# Get rid of last segment of the snake
			# .pop() command removes last item in list
			old_segment = self.snake_segments.pop()
			self.allspriteslist.remove(old_segment)

	def draw_snake(self, screen):
		self.allspriteslist.draw(screen)

	def turn_up(self):
		if self.direction != DOWN and self.direction != UP:
			self.direction = UP
			self.x_change = 0
			self.y_change = (self.seg_h + self.seg_m) * -1

	def turn_right(self):
		if self.direction != LEFT and self.direction != RIGHT:
			self.direction = RIGHT
			self.x_change = (self.seg_w + self.seg_m)
			self.y_change = 0

	def turn_down(self):
		if self.direction != UP and self.direction != DOWN:
			self.direction = DOWN
			self.x_change = 0
			self.y_change = (self.seg_h + self.seg_m)

	def turn_left(self):
		if self.direction != RIGHT and self.direction != LEFT:
			self.direction = LEFT
			self.x_change = (self.seg_w + self.seg_m) * -1
			self.y_change = 0

class Segment(pygame.sprite.Sprite):
	""" Class to represent one segment of the snake. """
	# -- Methods
	# Constructor function
	def __init__(self, x = 0, y = 0, w = 18, h = 18, color = WHITE):
		# Call the parent's constructor
		super().__init__()
		# Set height, width
		self.image = pygame.Surface([w, h])
		self.image.fill(color)
		# Make our top-left corner the passed-in location.
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
