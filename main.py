# Author: Shway Wang
# Date: 2020/12/3
import time
from util import *
from rl_solver import *

class GameWindow(object):
    def __init__(self, w, h, title):
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
        self.wall_thickness = 3
        # Initialize the snake object:
        self.snake = Snake()
        self.food = Food(w, h, self.snake.snake_segments)
        # Initialize Boundary:
        self.boundary = self.draw_boundary()
        # Flag indicates if the loop ends:
        self.done = True
        self.quit = False
        # Initilize the AI stuff:
        self.rl_solver = RL_Solver(agent_type = 'q_learning')

    def handle_event(self, event):
        if event is None:
            return
        if event.type == pygame.QUIT:
            self.done = True
            self.quit = True
        # Set the speed based on the key pressed
        # We want the speed to be enough that we move a full
        # segment, plus the margin.
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.snake.turn_left()
                return LEFT
            elif event.key == pygame.K_RIGHT:
                self.snake.turn_right()
                return RIGHT
            elif event.key == pygame.K_UP:
                self.snake.turn_up()
                return UP
            elif event.key == pygame.K_DOWN:
                self.snake.turn_down()
                return DOWN

    def draw_boundary(self):
        up_bound = 26
        right_bound = self.screen_width - 30
        down_bound = self.screen_height - 26
        left_bound = 30
        pygame.draw.rect(self.screen, WHITE,
            pygame.Rect(left_bound, up_bound, self.screen_width - 57, self.wall_thickness))
        pygame.draw.rect(self.screen, WHITE,
            pygame.Rect(left_bound, up_bound, self.wall_thickness, self.screen_height - 50))
        pygame.draw.rect(self.screen, WHITE,
            pygame.Rect(left_bound, down_bound, self.screen_width - 60, self.wall_thickness))
        pygame.draw.rect(self.screen, WHITE,
            pygame.Rect(right_bound, up_bound, self.wall_thickness, self.screen_height - 49))
        return [up_bound, right_bound, down_bound, left_bound]

    def is_collision(self, snake_pos, snake_segments, boundary):
        if (snake_pos[0] <= boundary[3] or snake_pos[0] >= boundary[1]
            or snake_pos[1] <= boundary[0] or snake_pos[1] >= boundary[2]):
            return True
        for i in range(1, len(snake_segments)):
            if (snake_segments[i].rect.x == snake_pos[0]
                and snake_segments[i].rect.y == snake_pos[1]):
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

    def snake_actions_and_AI(self, event, episode):
        self.rl_solver.epsilon = 1 / episode
        # Current state:
        self.snake.sence(self.food, self.boundary)
        cur_state = State(self.snake.sence_dist, self.snake.sence_matrix)
        # update the savt if current state is not in savt:
        if cur_state not in self.rl_solver.savt.content:
            cur_action_set = {UP:0, RIGHT:0, DOWN:0, LEFT:0}
            self.rl_solver.savt.addNewStateActionSet(cur_state, cur_action_set)
        #cur_action = self.handle_event(event) # the snake moves
        cur_action = self.rl_solver.agent.selectAction(self.rl_solver.savt.content[cur_state])
        if cur_action == UP: self.snake.turn_up()
        elif cur_action == RIGHT: self.snake.turn_right()
        elif cur_action == DOWN: self.snake.turn_down()
        elif cur_action == LEFT: self.snake.turn_left()
        # Snake move one more step, this function also is the reward function:
        ret = self.snake.move_and_getRet(self.food)
        # detect collision:
        if self.is_collision(self.snake.get_snake_head_pos(),
            self.snake.snake_segments, self.boundary):
            ret -= 1000
            self.done = True
            # reinit the snake and foods:
            self.snake = Snake()
            self.food = Food(self.screen_width, self.screen_height, self.snake.snake_segments)
        # Next state:
        self.snake.sence(self.food, self.boundary)
        next_state = State(self.snake.sence_dist, self.snake.sence_matrix)
        # update the savt if current state is not in savt:
        if next_state not in self.rl_solver.savt.content:
            next_action_set = {UP:0, RIGHT:0, DOWN:0, LEFT:0}
            self.rl_solver.savt.addNewStateActionSet(next_state, next_action_set)
        # Next action:
        next_action = self.rl_solver.agent.selectAction(self.rl_solver.savt.content[next_state])
        # Update savt:
        self.rl_solver.agent.updateActionValue(self.rl_solver.savt,
            cur_state, cur_action, next_state, next_action, ret)
        return ret

    def gameLoop(self, game_speed = 0):
        # begin the game loop:
        clock = pygame.time.Clock()
        event_buffer = []
        self.start_game_message()
        new_game = True
        # FIXME
        episode = 0
        while not self.quit:
            '''
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        # no longer a new game:
                        new_game = False
                        # restart a game:
                        self.done = False
                        # re-empty the event-buffer:
                        event_buffer = []
                        # initialize the snake:
                        self.snake = Snake()
                        self.food = Food(self.snake.snake_segments)
                        '''
            # game loop:
            episode += 1
            accum_ret = 0
            self.done = False
            while not self.done:
                for e in pygame.event.get():
                    if e.type == pygame.KEYDOWN or e.type == pygame.QUIT:
                        event_buffer.append(e)
                event = event_buffer.pop(0) if len(event_buffer) > 0 else None

                # This is where the AI come into play:
                accum_ret += self.snake_actions_and_AI(event, episode)

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
    GameWindow(400, 300, 'Snake').gameLoop()

if __name__ == '__main__':
    main()
