import random
import pygame
from pygame import Vector2

import shared
from level import level
from playercontroller import PlayerController
from task_manager import Task, Sequencer, TT_DRAW

WIDTH = int(shared.canvas_size.x)
HEIGHT = int(shared.canvas_size.y)

GRID_SIZE = 10

GRID_HEIGHT = HEIGHT // GRID_SIZE
GRID_WIDTH = WIDTH // GRID_SIZE

# Particle types
BOUND = -1
EMPTY = 0
SAND = 1
WATER = 2
GAS = 3
ROCK = 4
AIR = 5

# Colors for visualization
COLORS = {
    BOUND: (255, 255, 255),
    EMPTY: (0, 0, 0),
    SAND: (194, 178, 128),
    WATER: (0, 150, 255),
    GAS: (255, 0, 255),
    ROCK: (175, 175, 175),
    AIR: (255, 255, 255)
}


class Cell(object):
    def __init__(self, cell_type=EMPTY):
        self.cell_type = cell_type

    def __getitem__(self, item):
        return super().__getattribute__(item)


grid_map: dict[tuple[int, int], Cell] = dict()


class ParticleData(object):
    def __getitem__(self, item):
        return super().__getattribute__(item)


def sand(new_grid_map, new_active: set, pd: ParticleData):
    if pd.move_down:
        del new_grid_map[pd.pos]
        new_grid_map[pd.down] = pd.cell
        new_active.add(pd.down)
    elif pd.neighbors[pd.down].cell_type == WATER:
        new_grid_map[pd.pos] = new_grid_map[pd.down]
        new_grid_map[pd.down] = pd.cell
        new_active.add(pd.pos)
        new_active.add(pd.down)
    elif pd.move_right and pd.move_left:
        del new_grid_map[pd.pos]
        choice = random.choice([pd.right, pd.left])
        new_grid_map[choice] = pd.cell
        new_active.add(choice)
    elif pd.move_b_right and pd.move_b_left:
        del new_grid_map[pd.pos]
        choice = random.choice([pd.b_left, pd.b_right])
        new_grid_map[choice] = pd.cell
        new_active.add(choice)
    elif pd.move_b_left:
        del new_grid_map[pd.pos]
        new_grid_map[pd.b_left] = pd.cell
        new_active.add(pd.b_left)
    elif pd.move_b_right:
        del new_grid_map[pd.pos]
        new_grid_map[pd.b_right] = pd.cell
        new_active.add(pd.b_right)
    else:
        new_grid_map[pd.pos] = pd.cell


def water(new_grid_map, new_active: set, pd: ParticleData):
    if pd.move_down:
        del new_grid_map[pd.pos]
        new_grid_map[pd.down] = pd.cell
        new_active.add(pd.down)
    elif pd.move_right and pd.move_left:
        del new_grid_map[pd.pos]
        choice = random.choice([pd.right, pd.left])
        new_grid_map[choice] = pd.cell
        new_active.add(choice)
    elif pd.move_b_right and pd.move_b_left:
        del new_grid_map[pd.pos]
        choice = random.choice([pd.b_left, pd.b_right])
        new_grid_map[choice] = pd.cell
        new_active.add(choice)
    elif pd.move_left and random.choice([True, False]):
        del new_grid_map[pd.pos]
        new_grid_map[pd.left] = pd.cell
        new_active.add(pd.left)
    elif pd.move_right and random.choice([True, False]):
        del new_grid_map[pd.pos]
        new_grid_map[pd.right] = pd.cell
        new_active.add(pd.right)
    else:
        new_grid_map[pd.pos] = pd.cell
        new_active.add(pd.pos)


def gas(new_grid_map, new_active: set, pd: ParticleData):
    if pd.move_up:
        del new_grid_map[pd.pos]
        new_grid_map[pd.up] = pd.cell
        new_active.add(pd.up)
    elif pd.move_right and pd.move_left:
        del new_grid_map[pd.pos]
        choice = random.choice([pd.right, pd.left])
        new_grid_map[choice] = pd.cell
        new_active.add(choice)
    elif pd.move_left and random.choice([True, False]):
        del new_grid_map[pd.pos]
        new_grid_map[pd.left] = pd.cell
        new_active.add(pd.left)
    elif pd.move_right and random.choice([True, False]):
        del new_grid_map[pd.pos]
        new_grid_map[pd.right] = pd.cell
        new_active.add(pd.right)
    else:
        new_grid_map[pd.pos] = pd.cell
        new_active.add(pd.pos)


def rock(new_grid_map, pd: ParticleData):
    new_grid_map[pd.pos] = pd.cell


funcs = {
    SAND: sand,
    WATER: water,
    GAS: gas,
    ROCK: rock,
}

active_cells = set()


def update_particles(task):
    global grid_map
    global active_cells

    new_active = set()
    new_grid_map: dict[tuple[int, int], Cell] = grid_map.copy()

    for pos in active_cells:
        x, y = pos
        cell = new_grid_map.get(pos, None)

        if cell is not None:
            x_valid = 0 <= x < GRID_WIDTH
            y_valid = 0 < y < GRID_HEIGHT - 1

            pd = ParticleData()
            pd.cell = cell
            pd.pos = pos
            pd.up = (x, y - 1)
            pd.down = (x, y + 1)
            pd.left = (x - 1, y)
            pd.right = (x + 1, y)
            pd.b_left = (x - 1, y + 1)
            pd.b_right = (x + 1, y + 1)
            pd.move_up = pd.up not in new_grid_map and y_valid
            pd.move_down = pd.down not in new_grid_map and y_valid
            pd.move_left = pd.left not in new_grid_map and x_valid
            pd.move_right = pd.right not in new_grid_map and x_valid
            pd.move_b_left = pd.b_left not in new_grid_map and x_valid and y_valid
            pd.move_b_right = pd.b_right not in new_grid_map and x_valid and y_valid
            pd.neighbors = {
                pd.up: new_grid_map.get(pd.up, Cell(EMPTY)),
                pd.down: new_grid_map.get(pd.down, Cell(EMPTY)),
                pd.left: new_grid_map.get(pd.left, Cell(EMPTY)),
                pd.right: new_grid_map.get(pd.right, Cell(EMPTY))
            }

            funcs[cell.cell_type](new_grid_map, new_active, pd)

    grid_map = new_grid_map
    active_cells = new_active


def draw_grid(task):
    """ Draws the grid using pygame. """
    for i in range(GRID_WIDTH * GRID_HEIGHT):
        x = i // GRID_HEIGHT
        y = i % GRID_HEIGHT
        color = (0, 0, 0)
        if (x, y) in grid_map:
            g_pos = grid_map[(x, y)]
            color = COLORS[g_pos.cell_type]
        pygame.draw.rect(shared.canvas, color, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
    return task.cont


def spawn_particle(x, y, particle_type):
    if 0 <= x < GRID_WIDTH and 0 < y < GRID_HEIGHT and (x, y) not in grid_map:
        grid_map[(x, y)] = Cell(particle_type)
        active_cells.add((x, y))


def init():
    mouse = PlayerController()
    level.add(mouse)
    can_click = [True]

    def mouse_clicks(task):
        if mouse.alive():
            if can_click[0]:
                mx, my = shared.get_mouse_pos()
                if pygame.mouse.get_pressed()[0]:  # Left click = sand
                    spawn_particle(mx // GRID_SIZE, my // GRID_SIZE, SAND)
                if pygame.mouse.get_pressed()[1]:  # Middle click = water
                    spawn_particle(mx // GRID_SIZE, my // GRID_SIZE, WATER)
                if pygame.mouse.get_pressed()[2]:  # Right click = gas
                    spawn_particle(mx // GRID_SIZE, my // GRID_SIZE, GAS)
            can_click[0] = not can_click[0]
            return task.cont
        else:
            return task.end

    Sequencer(
        Task(mouse_clicks),
        Task(update_particles)
    ).build(True, True).start()

    LAYERS = 3  # Number of parallax layers
    SPEED_MULTIPLIERS = [0.2, 0.4, 0.6]  # How much each layer moves with the player
    stars = []
    num_stars = 100

    v = (0, 1)
    r = shared.canvas.get_rect()

    for _ in range(LAYERS):
        layer_stars = []
        for _ in range(num_stars // LAYERS):
            x = random.randint(0, r.width)
            y = random.randint(0, r.height)
            layer_stars.append([x, y])  # Store (x, y) position
        stars.append(layer_stars)

    def parallax_effect(task):
        for layer in range(LAYERS):
            for star in stars[layer]:
                star[0] -= v[0] * SPEED_MULTIPLIERS[layer]
                star[0] %= r.width

                star[1] += v[1] * SPEED_MULTIPLIERS[layer]
                star[1] %= r.height

                # Draw star with different brightness for depth effect
                brightness = 100 + layer * 50
                color = (brightness, brightness, brightness)
                center = Vector2(star) + Vector2(r.center) - Vector2(r.size) // 2
                radius = 2 - layer // 2
                pygame.draw.circle(shared.canvas, color, center, radius)
        return task.cont

    Sequencer(
        Task(draw_grid),
        Task(parallax_effect)
    ).build(True, True).start(TT_DRAW)

