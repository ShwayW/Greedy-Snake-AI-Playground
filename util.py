# Author: Shway Wang
# Date: 2020/12/5
import pygame
import random
from rl_solver import *
# --- Globals ---
# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
# Game Objects:
SPACE = 0
WALL = 1
FOOD = 2
BODY = 3

class Food(object):
	''' Class to represent a unit of food. '''
	# Construction function:
	def __init__(self, screen_w, screen_h, snake_segments = [], w = 18, h = 18):
		# record the screen width and height:
		self.screen_w = screen_w
		self.screen_h = screen_h
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
			self.food.rect.x = random.randint(0, int(self.screen_w / 21) - 4) * 21 + 35
			self.food.rect.y = random.randint(0, int(self.screen_h / 21) - 4) * 21 + 30
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
	def __init__(self, snake_len = 5, seg_w = 18, seg_h = 18, seg_m = 3, sence_dist = 10):
		# initialize the drawable:
		self.allspriteslist = pygame.sprite.Group()
		# Set the width and height of each snake segment
		self.seg_w = seg_w
		self.seg_h = seg_h
		# Margin between each segment
		self.seg_m = seg_m
		# Get the initial sence distance:
		self.sence_dist = sence_dist
		# Create an initial snake
		self.snake_segments = []
		# Set initial speed
		self.x_change = self.seg_w + self.seg_m
		self.y_change = 0
		# Set initial direction:
		self.direction = RIGHT
		# Construct the snake body:
		for i in range(snake_len):
			x = 245 - (self.seg_w + self.seg_m) * i
			y = 30
			segment = Segment(x, y, self.seg_w, self.seg_h)
			self.snake_segments.append(segment)
			self.allspriteslist.add(segment)
		# Construct the sence matrix:
		self.sence_matrix = np.zeros((self.sence_dist, self.sence_dist))

	def sence(self, food, boundary):
		''' Can sence an area of the snake's surroundings
		according to the sence matrix and sence distance.
		Here each unit of pygame display is 21 pixles. '''
		# First, clear the last sence:
		self.sence_matrix = np.zeros((self.sence_dist, self.sence_dist))
		# Then get the position of the head of the snake:
		head_pos = (self.snake_segments[0].rect.x, self.snake_segments[0].rect.y)
		# See if food is in sencing range:
		food_pos = food.get_food_pos()
		food_hor_displ = int((food_pos[0] - head_pos[0]) / 21)
		food_ver_displ = int((food_pos[1] - head_pos[1]) / 21)
		if (abs(food_hor_displ) <= self.sence_dist / 2 and abs(food_ver_displ) <= self.sence_dist / 2):
			x = int(food_hor_displ - self.sence_dist / 2)
			y = int(food_ver_displ - self.sence_dist / 2)
			self.sence_matrix[y, x] = FOOD
		# See if wall is in sencing range:
		wall_up_displ = int((boundary[0] - head_pos[1]) / 21)
		wall_right_displ = int((boundary[1] - head_pos[0]) / 21)
		wall_down_displ = int((boundary[2] - head_pos[1]) / 21)
		wall_left_displ = int((boundary[3] - head_pos[0]) / 21)
		sence_up = abs(wall_up_displ) <= self.sence_dist / 2
		sence_right = abs(wall_right_displ) <= self.sence_dist / 2
		sence_down = abs(wall_down_displ) <= self.sence_dist / 2
		sence_left = abs(wall_left_displ) <= self.sence_dist / 2
		up_y, right_x, down_y, left_x = (0, 0, 0, 0)
		if sence_up:
			up_y = int(wall_up_displ - self.sence_dist / 2)
			self.sence_matrix[up_y, :] = WALL
		if sence_right:
			right_x = int(wall_right_displ - self.sence_dist / 2)
			self.sence_matrix[:, right_x] = WALL
		if sence_down:
			down_y = int(wall_down_displ - self.sence_dist / 2)
			self.sence_matrix[down_y, :] = WALL
		if sence_left:
			left_x = int(wall_left_displ - self.sence_dist / 2)
			self.sence_matrix[:, left_x] = WALL
		# Handle the 4 corner cases:
		if sence_up and sence_right:
			self.sence_matrix[:up_y, :] = SPACE
			self.sence_matrix[:, right_x + 1:] = SPACE
		if sence_right and sence_down:
			self.sence_matrix[:, right_x + 1:] = SPACE
			self.sence_matrix[down_y + 1:, :] = SPACE
		if sence_down and sence_left:
			self.sence_matrix[down_y + 1:, :] = SPACE
			self.sence_matrix[:, :left_x] = SPACE
		if sence_left and sence_up:
			self.sence_matrix[:, :left_x] = SPACE
			self.sence_matrix[:up_y, :] = SPACE
		# See if body is in sencing range:
		for s in self.snake_segments:
			seg_pos = (s.rect.x, s.rect.y)
			seg_hor_displ = int((seg_pos[0] - head_pos[0]) / 21)
			seg_ver_displ = int((seg_pos[1] - head_pos[1]) / 21)
			if (abs(seg_hor_displ) <= self.sence_dist / 2 and abs(seg_ver_displ) <= self.sence_dist / 2):
				x = int(seg_hor_displ - self.sence_dist / 2)
				y = int(seg_ver_displ - self.sence_dist / 2)
				self.sence_matrix[y, x] = BODY

	def get_snake_head_pos(self):
		return (self.snake_segments[0].rect.x, self.snake_segments[0].rect.y)

	def get_snake_length(self):
		return len(self.snake_segments)

	def move_and_getRet(self, food):
		# returns True if this step cause a food to be consumed
		# or else returns False
		# Figure out where new segment will be
		x = self.snake_segments[0].rect.x + self.x_change
		y = self.snake_segments[0].rect.y + self.y_change
		segment = Segment(x, y, self.seg_w, self.seg_h)
		is_food_consumed = self.if_ate_food(food)
		# Insert new segment into the list
		self.snake_segments.insert(0, segment)
		self.allspriteslist.add(segment)
		# return the possible rewards:
		if is_food_consumed:
			return 100
		return -1

	def if_ate_food(self, food):
		# returns True if a food is ate
		# or else returns False
		# see if the food is ate:
		if self.get_snake_head_pos() == food.get_food_pos(): # if ate, keep the last segment
			# generate new food
			food.generate_food(self.snake_segments, True)
			return True
		else: # if not ate, delete the last segment
			# Get rid of last segment of the snake
			# .pop() command removes last item in list
			old_segment = self.snake_segments.pop()
			self.allspriteslist.remove(old_segment)
			return False

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
