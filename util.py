# Author: Shway Wang
# Date: 2020/12/5
import pygame
import random
from rl_solver import *
# --- Globals ---
# Drawable metrics:
BOUNDMARGIN_X = 30
BOUNDMARGIN_Y = 25
WALL_THICK = 3
SEGSIDE_LEN = 17
SEGMARGIN = 3
# Sence Matrix metrics:
SMATRIX_ROWNUM = 9
SMATRIX_COLNUM = 12
# Screen sizes:
# Small screen: sence matrix would be of 4x3 size
SCREEN_W = 2 * (BOUNDMARGIN_X + WALL_THICK) + SMATRIX_COLNUM * (SEGMARGIN + SEGSIDE_LEN)
SCREEN_H = 2 * (BOUNDMARGIN_Y + WALL_THICK) + SMATRIX_ROWNUM * (SEGMARGIN + SEGSIDE_LEN)

# Snake length:
SNAKELEN = 3
# Snake start position:
SSTART_HPOS = 4
SSTART_VPOS = 0
# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
# Game Objects:
SPACE = 0
WALL = 1
FOOD = 2
BODY = 3
# Total number of foods:
FOODNUM = 700

class Food(object):
	''' Class to represent a unit of food. '''
	# Construction function:
	def __init__(self, screen_w = SCREEN_W, screen_h = SCREEN_H, snake_segments = [],
		w = SEGSIDE_LEN, h = SEGSIDE_LEN):
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
			chunk_unit_len = SEGSIDE_LEN + SEGMARGIN
			margin_total_x = WALL_THICK + BOUNDMARGIN_X
			margin_total_y = WALL_THICK + BOUNDMARGIN_Y
			x_uplimit = int((self.screen_w - 2 * margin_total_x) / chunk_unit_len - 1)
			self.food.rect.x = random.randint(0, x_uplimit) * chunk_unit_len + margin_total_x + SEGMARGIN
			y_uplimit = int((self.screen_h - 2 * margin_total_y) / chunk_unit_len - 1)
			self.food.rect.y = random.randint(0, y_uplimit) * chunk_unit_len + margin_total_y + SEGMARGIN
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
	def __init__(self, snake_len = SNAKELEN, seg_w = SEGSIDE_LEN, seg_h = SEGSIDE_LEN, seg_m = SEGMARGIN):
		# initialize the drawable:
		self.allspriteslist = pygame.sprite.Group()
		# Set the width and height of each snake segment
		self.seg_w = seg_w
		self.seg_h = seg_h
		# Margin between each segment
		self.seg_m = seg_m
		# Create an initial snake
		self.snake_segments = []
		# Set initial speed
		self.x_change = self.seg_w + self.seg_m
		self.y_change = 0
		# Set initial direction:
		self.direction = RIGHT
		# Construct the snake body:
		start_x = BOUNDMARGIN_X + WALL_THICK + SEGMARGIN + SSTART_HPOS * (SEGSIDE_LEN + SEGMARGIN)
		start_y = BOUNDMARGIN_Y + WALL_THICK + SEGMARGIN + SSTART_VPOS * (SEGSIDE_LEN + SEGMARGIN)
		for i in range(snake_len):
			x = start_x - (self.seg_w + self.seg_m) * i
			y = start_y
			segment = Segment(x, y, self.seg_w, self.seg_h)
			self.snake_segments.append(segment)
			self.allspriteslist.add(segment)
		# Construct the sence matrix:
		self.sence_matrix = np.zeros((SMATRIX_ROWNUM + 2, SMATRIX_COLNUM + 2))

	def sence(self, food, boundary):
		''' Matrixize the game board into a internal representation of a matrix. '''
		# First, clear the last sence:
		chunk_unit_len = SEGSIDE_LEN + SEGMARGIN
		self.sence_matrix = np.zeros((SMATRIX_ROWNUM + 2, SMATRIX_COLNUM + 2)) # needs padding
		# Food loaction:
		food_pos = food.get_food_pos()
		m_food_x = int((food_pos[0] - BOUNDMARGIN_X - WALL_THICK - SEGMARGIN) / chunk_unit_len) + 1
		m_food_y = int((food_pos[1] - BOUNDMARGIN_Y - WALL_THICK - SEGMARGIN) / chunk_unit_len) + 1
		self.sence_matrix[m_food_y][m_food_x] = FOOD
		# Body location:
		for s in self.snake_segments:
			m_seg_x = int((s.rect.x - BOUNDMARGIN_X - WALL_THICK - SEGMARGIN) / chunk_unit_len) + 1
			m_seg_y = int((s.rect.y - BOUNDMARGIN_Y - WALL_THICK - SEGMARGIN) / chunk_unit_len) + 1
			self.sence_matrix[m_seg_y][m_seg_x] = BODY

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
			return 10
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
	def __init__(self, x = 0, y = 0, w = SEGSIDE_LEN, h = SEGSIDE_LEN, color = WHITE):
		# Call the parent's constructor
		super().__init__()
		# Set height, width
		self.image = pygame.Surface([w, h])
		self.image.fill(color)
		# Make our top-left corner the passed-in location.
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
