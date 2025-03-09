import pygame

WIDTH = 640
HEIGHT = 480

# Constants
TILE_SIZE = 32
GRID_WIDTH, GRID_HEIGHT = 10, 10

grid_items = {}
grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]


def item_types():
    return {
        "House": {"shape": [(0, 0), (1, 0), (0, 1), (1, 1)], "anchor_offset": (1, 1)},
        "T": {"shape": [(0, 0), (1, 0), (2, 0), (1, 1)], "anchor_offset": (1, 0)}
    }


def get_grid_pos(pos):
    return pos[0] // TILE_SIZE, pos[1] // TILE_SIZE


def get_item_at(pos):
    x, y = pos
    key = grid[y][x]
    return grid_items[key] if key else None


def spawn_item(grid_pos, item_id):
    item = item_types()[item_id]
    place_item(grid_pos, item)


def is_invalid_tile(pos):
    x, y = pos
    return not 0 <= x < GRID_WIDTH or not 0 <= y < GRID_HEIGHT or grid[y][x]


def can_place(grid_pos, item):
    if not item:
        return False
    can = True
    offset = item["anchor_offset"]
    x = grid_pos[0] - offset[0]
    y = grid_pos[1] - offset[1]
    for point in item["shape"]:
        dx = point[0] + x
        dy = point[1] + y
        if is_invalid_tile((dx, dy)):
            can = False
            break
    return can


def place_item(grid_pos, item):
    can = can_place(grid_pos, item)
    if can:
        offset = item["anchor_offset"]
        x = grid_pos[0] - offset[0]
        y = grid_pos[1] - offset[1]
        for point in item["shape"]:
            dx = point[0] + x
            dy = point[1] + y
            grid[dy][dx] = (x, y)
        grid_items[(x, y)] = item
    return can


def remove_item(pos):
    item = get_item_at(pos)
    if item:
        anchor = grid[pos[1]][pos[0]]
        for point in item["shape"]:
            dx = point[0] + anchor[0]
            dy = point[1] + anchor[1]
            grid[dy][dx] = None
        del grid_items[anchor]
    return item


def rotate_item(item):
    if not item:
        return
    shape = item["shape"]
    offset = item["anchor_offset"]
    for i, point in enumerate(shape):
        x = point[0] + offset[1] - offset[0]
        y = -point[1] + offset[0] + offset[1]
        item["shape"][i] = (y, x)


def draw_drag(item):
    m_pos = pygame.mouse.get_pos()
    mx = m_pos[0] // TILE_SIZE
    my = m_pos[1] // TILE_SIZE
    offset = item["anchor_offset"]
    x = mx - offset[0]
    y = my - offset[1]
    for point in item["shape"]:
        dx = point[0] + x
        dy = point[1] + y
        color = "red" if is_invalid_tile((dx, dy)) else "yellow"
        rect = pygame.Rect(dx * TILE_SIZE, dy * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, color, rect, 3)


def draw_grid():
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if grid[y][x]:
                pygame.draw.rect(screen, "green", rect, 3)
            else:
                pygame.draw.rect(screen, (100, 100, 100), rect, 3)


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Dragging
original_item = None
dragging_item = None

# spawn_item((3, 3), "House")
spawn_item((1, 0), "T")
spawn_item((4, 0), "T")
spawn_item((7, 0), "T")

running = True
while running:
    screen.fill((30, 30, 30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                pos = get_grid_pos(event.pos)
                original_item = (pos, get_item_at(pos))
                dragging_item = remove_item(pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                pos = get_grid_pos(event.pos)
                if not place_item(pos, dragging_item):
                    place_item(*original_item)
                dragging_item = None
                original_item = None
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                rotate_item(dragging_item)

    draw_grid()
    if dragging_item:
        draw_drag(dragging_item)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()