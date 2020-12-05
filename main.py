# Author: Shway Wang
# Date: 2020/12/3
import numpy as np
import time
from util import *

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
        self.food = Food(self.snake.snake_segments)
        # Flag indicates if the loop ends:
        self.done = True
        self.quit = False

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
            if event.key == pygame.K_RIGHT:
                self.snake.turn_right()
            if event.key == pygame.K_UP:
                self.snake.turn_up()
            if event.key == pygame.K_DOWN:
                self.snake.turn_down()

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

    def gameLoop(self, game_speed = 7):
        # begin the game loop:
        clock = pygame.time.Clock()
        event_buffer = []
        self.start_game_message()
        new_game = True
        while not self.quit:
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
            # game loop:
            while not self.done:
                for e in pygame.event.get():
                    if e.type == pygame.KEYDOWN or e.type == pygame.QUIT:
                        event_buffer.append(e)
                event = event_buffer.pop(0) if len(event_buffer) > 0 else None
                self.handle_event(event)
                # Snake take a step, this function also checks if a food is ate:
                self.snake.take_one_step(self.food)
                # -- Draw everything
                # Clear screen
                self.screen.fill(BLACK)
                # draw the boundary:
                boundary = self.draw_boundary()
                # draw the snake and the food:
                self.snake.draw_snake(self.screen)
                self.food.draw_food(self.screen)
                # game info:
                FONT = pygame.font.SysFont("comicsans", 20)
                message = FONT.render("Snake length: " + str(self.snake.get_snake_length()),
                    True, (255, 255, 255))
                self.screen.blit(message, (10, 10))
                # Flip screen
                pygame.display.flip()
                # detect collision:
                if self.is_collision(self.snake.get_snake_head_pos(),
                    self.snake.snake_segments, boundary):
                    self.done = True
                # Pause
                clock.tick(game_speed)
            if not new_game:
                self.end_game_message()
        pygame.quit()

def main():
    GameWindow(800, 600, 'Snake').gameLoop()

if __name__ == '__main__':
    main()
