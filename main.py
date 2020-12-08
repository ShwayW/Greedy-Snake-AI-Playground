# Author: Shway Wang
# Date: 2020/12/3
import time
from util import *
from rl_solver import *

class GameWindow(object):
	def __init__(self, w = SCREEN_W, h = SCREEN_H, title = "Snake"):
		random.seed(0)
		# Call this function so the Pygame library can initialize itself
		pygame.init()
		# Create an 800x600 sized screen
		self.screen_width = w
		self.screen_height = h
		self.screen = pygame.display.set_mode([w, h])
		# Set the title of the window
		pygame.display.set_caption(title)
		# Set thickness of wall:
		self.wall_thickness = WALL_THICK
		# Initialize the snake object:
		self.snake = Snake()
		self.food = Food(w, h, self.snake.snake_segments)
		# Initialize Boundary:
		self.boundary = self.draw_boundary()
		# Flag indicates if the loop ends:
		self.done = True
		self.quit = False
		# the food number:
		self.foodnum = FOODNUM
		# Initilize the AI stuff:
		self.rl_solver = RL_Solver(agent_type = 'q_learning')

	def handle_event(self, event):
		if event is None:
			return NOTHING
		if event.type == pygame.QUIT:
			self.done = True
			self.quit = True
		# Set the speed based on the key pressed
		# We want the speed to be enough that we move a full
		# segment, plus the margin.
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_LEFT: return LEFT
			elif event.key == pygame.K_RIGHT: return RIGHT
			elif event.key == pygame.K_UP: return UP
			elif event.key == pygame.K_DOWN: return DOWN

	def draw_boundary(self):
		up_bound = BOUNDMARGIN_Y
		right_bound = self.screen_width - BOUNDMARGIN_X
		down_bound = self.screen_height - BOUNDMARGIN_Y
		left_bound = BOUNDMARGIN_X
		w = self.screen_width - 2 * BOUNDMARGIN_X
		h = self.wall_thickness
		pygame.draw.rect(self.screen, WHITE, pygame.Rect(left_bound, up_bound, w, h))
		w = self.wall_thickness
		h = self.screen_height - 2 * BOUNDMARGIN_Y
		pygame.draw.rect(self.screen, WHITE, pygame.Rect(left_bound, up_bound, w, h))
		w = self.screen_width - 2 * BOUNDMARGIN_X
		h = self.wall_thickness
		pygame.draw.rect(self.screen, WHITE, pygame.Rect(left_bound, down_bound, w, h))
		w = self.wall_thickness
		h = self.screen_height - 2 * BOUNDMARGIN_Y + WALL_THICK
		pygame.draw.rect(self.screen, WHITE, pygame.Rect(right_bound, up_bound, w, h))
		return [up_bound, right_bound, down_bound, left_bound]

	def is_collision(self, snake_pos, snake_segments, boundary):
		if (snake_pos[0] <= boundary[3] or snake_pos[0] >= boundary[1] or snake_pos[1] <= boundary[0] or snake_pos[1] >= boundary[2]):
			return True
		for i in range(1, len(snake_segments)):
			if (snake_segments[i].rect.x == snake_pos[0] and snake_segments[i].rect.y == snake_pos[1]):
				return True
		return False

	def start_game_message(self):
		# Clear screen
		self.screen.fill(BLACK)
		# display GAME OVER:
		x = self.screen_width / 5
		y = self.screen_height / 3
		FONT = pygame.font.SysFont("comicsans", 70)
		message = FONT.render("Greedy Snake Game!", True, (255, 255, 255))
		self.screen.blit(message, (x, y))
		# display press enter:
		FONT = pygame.font.SysFont("comicsans", 30)
		message = FONT.render("press Enter to play...", True, (255, 255, 255))
		self.screen.blit(message, (x + self.screen_width / 5, y + self.screen_height / 10))
		FONT = pygame.font.SysFont("comicsans", 30)
		message = FONT.render("Control using arrow keys", True, (255, 255, 255))
		self.screen.blit(message, (x + self.screen_width / 6, y + self.screen_height / 7))
		# Flip screen
		pygame.display.flip()

	def end_game_message(self):
		# Clear screen
		self.screen.fill(BLACK)
		# display GAME OVER:
		x = self.screen_width / 3
		y = self.screen_height / 3
		FONT = pygame.font.SysFont("comicsans", 70)
		message = FONT.render("GAME OVER", True, (255, 255, 255))
		self.screen.blit(message, (x, y))
		# display press enter:
		FONT = pygame.font.SysFont("comicsans", 30)
		message = FONT.render("press Enter to continue...", True, (255, 255, 255))
		self.screen.blit(message, (x + self.screen_width / 25, y + self.screen_height / 10))
		# Flip screen
		pygame.display.flip()

	def gameLoop(self, game_speed = 5):
		# begin the game loop:
		clock = pygame.time.Clock()
		event_buffer = []
		self.start_game_message()
		new_game = True

		# Modes:
		# Here choose manual game or auto game:
		auto = True
		# Here choose to train or to perform:
		train = False
		for _ in range(1000):
			# For each training fold:
			episode = 0
			#while not self.quit:
			for _ in range(500):
				# game loop:
				# Variables for keeping records:
				episode += 1
				# Want to gradually decrease epsilon:
				if train:
					self.rl_solver.agent.epsilon = 1 / episode
				else:
					self.rl_solver.agent.epsilon = 0
				accum_ret = 0
				self.done = False
				self.foodnum = FOODNUM
				''' initialize the start state: '''
				random.seed(0)
				self.snake = Snake()
				self.food = Food(self.screen_width, self.screen_height, self.snake.snake_segments)
				self.snake.sence(self.food, self.boundary)
				cur_state = State(self.snake.sence_matrix)
				# Want to save training result every k episodes:
				k = 500
				if episode % k == 0:
					print("saving data......")
					self.rl_solver.savt.safe_data()
				''' Loop for each step of the episode: '''
				while not self.done:
					if not auto:
						for e in pygame.event.get():
							if e.type == pygame.KEYDOWN or e.type == pygame.QUIT:
								event_buffer.append(e)
						event = event_buffer.pop(0) if len(event_buffer) > 0 else None

					if not auto:
						print(self.snake.sence_matrix)
					# update the savt if current state is not in savt:
					if cur_state not in self.rl_solver.savt.content:
						cur_action_dict = {UP:0, RIGHT:0, DOWN:0, LEFT:0, NOTHING:0}
						self.rl_solver.savt.addNewStateActionSet(cur_state, cur_action_dict)
					ret = 0
					''' choose current action from current state using epsilon soft: '''
					cur_action = NOTHING
					if auto:
						cur_action = self.rl_solver.agent.selectAction(self.rl_solver.savt.content[cur_state])
					else:
						cur_action = self.handle_event(event) # the snake moves
					''' Take current action and observe return and next state: '''
					if cur_action == UP: self.snake.turn_up()
					elif cur_action == RIGHT: self.snake.turn_right()
					elif cur_action == DOWN: self.snake.turn_down()
					elif cur_action == LEFT: self.snake.turn_left()
					else:
						ret += 1
					# Snake move one more step, this function also is the reward function:
					ret += self.snake.move_and_getRet(self.food)
					# detect collision:
					if self.is_collision(self.snake.get_snake_head_pos(), self.snake.snake_segments, self.boundary):
						ret -= 1000
						self.done = True
					elif self.snake.get_snake_head_pos() == self.food.get_food_pos():
						self.foodnum -= 1
						if self.foodnum == 0:
							ret += 100
							self.done = True
					# Next state:
					self.snake.sence(self.food, self.boundary)
					next_state = State(self.snake.sence_matrix)
					''' Q(s,a) <- Q(s,a) + alpha[ret + gamma * max(Q(s', a')) - Q(s,a)] '''
					# Get the value of max_a(Q(s', a)):
					# update the savt if next state is not in savt:
					if next_state not in self.rl_solver.savt.content:
						if not auto: print('not in')
						next_action_set = {UP:0, RIGHT:0, DOWN:0, LEFT:0, NOTHING:0}
						self.rl_solver.savt.addNewStateActionSet(next_state, next_action_set)
					else:
						if not auto:
							print(self.rl_solver.savt.content[next_state])

					# Next action:
					next_action = self.rl_solver.agent.selectAction(self.rl_solver.savt.content[next_state])
					# Update savt:
					self.rl_solver.agent.updateActionValue(self.rl_solver.savt,
						cur_state, cur_action, next_state, next_action, ret)
					''' S <- S' '''
					cur_state = next_state
					# get the accumulated return:
					accum_ret += ret

					# -- Draw everything
					# Clear screen
					self.screen.fill(BLACK)
					# draw the snake and the food:
					self.snake.draw_snake(self.screen)
					self.food.draw_food(self.screen)
					# draw the boundary again:
					self.draw_boundary()
					# game info:
					FONT = pygame.font.SysFont("comicsans", 20)
					message = FONT.render("Snake length: " + str(self.snake.get_snake_length()),
						True, (255, 255, 255))
					self.screen.blit(message, (10, 10))
					# Flip screen
					pygame.display.flip()
					# Pause
					clock.tick(game_speed)
				if not new_game:
					self.end_game_message()
				print("episode " + str(episode) + " got return: " + str(accum_ret))
		pygame.quit()

def main():
	GameWindow().gameLoop()

if __name__ == '__main__':
	main()
