#!/usr/bin/env python3

from curtsies import FullscreenWindow, Input, FSArray
from curtsies.fmtfuncs import invert, plain, on_green, on_red, red
from enum import Enum, auto
from random import randrange
import time

FPS = 8

VIEWPORT_X_ORIGIN = 0
VIEWPORT_Y_ORIGIN = VIEWPORT_X_ORIGIN // 2
VIEWPORT_WIDTH = 50
VIEWPORT_HEIGHT = VIEWPORT_WIDTH // 2

SNAKE_INITIAL_X = 1
SNAKE_INITIAL_Y = 2

SNAKE_DEFAULT_SIZE = 3

class Direction(Enum):
    LEFT = 1
    RIGHT = auto()
    UP = auto()
    DOWN = auto()

class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Snake:
    def __init__(self, direction = Direction.RIGHT, initial_size  = SNAKE_DEFAULT_SIZE):
        self.direction = direction
        self.head_position = Position(SNAKE_INITIAL_X, SNAKE_INITIAL_Y)

        self.body = [
            Position(SNAKE_INITIAL_X - i, SNAKE_INITIAL_Y)
            for i in range(initial_size)
        ]

        self.size = len(self.body)

    def set_direction(self, new_direction):
        opposites = {
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT,
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP
        }

        if opposites[new_direction] != self.direction:
            self.direction = new_direction

    def update(self):
        head = self.body[0]
        
        paths = {
            Direction.LEFT: Position(head.x - 1, head.y),
            Direction.RIGHT: Position(head.x + 1, head.y),
            Direction.UP: Position(head.x, head.y - 1),
            Direction.DOWN: Position(head.x, head.y + 1)
        }

        self.head_position = paths[self.direction]
        self.body.insert(0, self.head_position)

        if len(self.body) > self.size:
            self.body.pop()

    def check_fruit(self, fruit):
        if self.head_position.x == fruit.position.x and self.head_position.y == fruit.position.y:
            self.size += 1
            return True
        return False

    def is_alive(self):
        is_inside_viewport = (
                    VIEWPORT_X_ORIGIN <= self.head_position.x < VIEWPORT_X_ORIGIN + VIEWPORT_WIDTH
                    and
                    VIEWPORT_Y_ORIGIN <= self.head_position.y < VIEWPORT_Y_ORIGIN + VIEWPORT_HEIGHT
                )
        
        auto_collision = any(
            self.head_position.x == part.x and self.head_position.y == part.y
            for part in self.body[1:]
        )

        return is_inside_viewport and not auto_collision

    def render(self, table):
        for part in self.body:
            table[
                part.y:part.y+1,
                part.x:part.x+1,
            ] = [on_green(' ')]

class Fruit():
    def __init__(self, x, y):
        self.position = Position(x, y)

    def render(self, table):
        table[
            self.position.y:self.position.y+1,
            self.position.x:self.position.x+1,
        ] = [on_red(' ')]

def snkloop():
    with FullscreenWindow() as window:
        table = FSArray(window.width, window.height)
        
        def clear_viewport():
            table[
                VIEWPORT_Y_ORIGIN:VIEWPORT_Y_ORIGIN + VIEWPORT_HEIGHT, 
                VIEWPORT_X_ORIGIN:VIEWPORT_X_ORIGIN + VIEWPORT_WIDTH, 
            ] = [
                invert(plain(' ' *  VIEWPORT_WIDTH))
                for _ in range(VIEWPORT_HEIGHT)
            ]
        
        def new_fruit():
            return Fruit(
                randrange(VIEWPORT_X_ORIGIN, VIEWPORT_X_ORIGIN + VIEWPORT_WIDTH),
                randrange(VIEWPORT_Y_ORIGIN, VIEWPORT_Y_ORIGIN + VIEWPORT_HEIGHT)
            )

        put_fruit = True
        fruit = None

        clear_viewport()

        snake = Snake(Direction.RIGHT)

        with Input() as input_generator:
            while True:
                c = input_generator.send(0.01)

                clear_viewport()

                if c == '<ESC>':
                    break
                
                snake.update()

                if snake.is_alive():
                    if c in ('d', 'D', '<RIGHT>'):
                        snake.set_direction(Direction.RIGHT)
                    if c in ('a', 'A', '<LEFT>'):
                        snake.set_direction(Direction.LEFT)
                    if c in ('w', 'W', '<UP>'):
                        snake.set_direction(Direction.UP)
                    if c in ('s', 'S', '<DOWN>'):
                        snake.set_direction(Direction.DOWN)

                    snake.render(table)

                    if put_fruit:
                        fruit = new_fruit()
                        put_fruit = False
                    
                    fruit.render(table)

                    if snake.check_fruit(fruit):
                        put_fruit = True
                else:
                    game_over_message = invert(red("GAME OVER"))
                    Y = VIEWPORT_Y_ORIGIN + (VIEWPORT_HEIGHT // 2)
                    X = VIEWPORT_X_ORIGIN + ((VIEWPORT_WIDTH // 2) - game_over_message.width // 2)

                    table[Y:Y+1, X:X+game_over_message.width] = [game_over_message]

                    if c in ('r', 'R'):
                        snake = Snake(Direction.RIGHT)
                
                time.sleep(1/FPS)

                window.render_to_terminal(table)

if __name__ == '__main__':
    snkloop()
