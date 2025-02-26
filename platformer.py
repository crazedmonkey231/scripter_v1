import random
import numpy as np
import pygame
from pygame import Surface, Vector2
from pygame.sprite import Sprite
import shared
import util
from level import level
from playercontroller import PlayerController

WIDTH = 17
HEIGHT = 12
CELL_SIZE = 40

bg = Surface((WIDTH * CELL_SIZE, HEIGHT * CELL_SIZE)).convert()
surf = Surface((CELL_SIZE, CELL_SIZE)).convert_alpha()

EMPTY = 0
WALL = 1


class Cell(object):
    def __init__(self, cell_type=EMPTY):
        super().__init__()
        self.cell_type = cell_type
        self.image = surf.copy()
        self.rect = None

    def __getitem__(self, item):
        return super().__getattribute__(item)


grid = np.empty((WIDTH, HEIGHT), dtype=Cell)

cell_colors = {
    EMPTY: "black",
    WALL: "white"
}


def generate_column():
    new_column = np.empty(HEIGHT, dtype=Cell)
    new_column[:] = Cell(EMPTY)

    # Random chance to add a floating platform (but not too low)
    if random.random() < 0.3:
        platform_y = random.randint(4, HEIGHT - 5)
        new_column[platform_y] = Cell(WALL)

    # Ensure ground is always present
    new_column[0] = Cell(WALL)
    new_column[HEIGHT - 1] = Cell(WALL)
    return new_column


def init():
    mouse = PlayerController()
    level.add(mouse)
    for i in range(WIDTH * HEIGHT):
        x = i // HEIGHT
        y = i % HEIGHT
        i = WALL if x == 0 or x == WIDTH or y == 0 or y == HEIGHT - 1 else EMPTY
        grid[x, y] = Cell(i)
    level.background = bg
    shared.set_canvas(bg)


scroll_offset = 0
SCROLL_SPEED = 50


def game_loop(task):
    global grid, scroll_offset
    scroll_offset += SCROLL_SPEED * shared.delta_time
    if scroll_offset >= CELL_SIZE:  # If moved a full tile, shift the grid
        scroll_offset -= CELL_SIZE
        grid = np.roll(grid, -1, axis=0)  # Shift everything left
        grid[-1, :] = generate_column()   # Add new platforms at the right
    bg.fill((0, 0, 0))
    for i in range(WIDTH * HEIGHT):
        x = i // HEIGHT
        y = i % HEIGHT
        cell = grid[x, y]
        cell.image.fill(cell_colors[cell.cell_type])
        cell.rect = bg.blit(cell.image, (x * CELL_SIZE - scroll_offset, y * CELL_SIZE))
    level.background = bg
    return task.cont
