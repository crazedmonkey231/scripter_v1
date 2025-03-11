import pygame

WIDTH = 640
HEIGHT = 480

TILE_SIZE = 32
GRID_WIDTH, GRID_HEIGHT = 20, 15

ITEM_TYPES = {
    "Single": {
        "shape": [(0, 0)],
        "anchor_offset": (0, 0)
    },
    "Line": {
        "shape": [(0, 0), (0, 1), (0, -1), (0, -2)],
        "anchor_offset": (0, 0)
    },
    "Square": {
        "shape": [(0, 0), (1, 0), (0, 1), (1, 1)],
        "anchor_offset": (1, 1)
    },
    "T": {
        "shape": [(0, 0), (1, 0), (-1, 0), (0, -1)],
        "anchor_offset": (0, 0)
    },
    "Cross": {
        "shape": [(0, 0), (0, 1), (1, 0), (-1, 0), (0, -1)],
        "anchor_offset": (0, 0)
    },
    "L": {
        "shape": [(0, 0), (1, 0), (0, -1), (0, -2)],
        "anchor_offset": (0, 0)
    },
    "Z": {
        "shape": [(0, 0), (-1, 0), (0, -1), (1, -1)],
        "anchor_offset": (0, 0)
    }
}


class Item(object):
    def __init__(self, shape, anchor_offset):
        self.shape = [*shape]
        self.anchor_offset = (anchor_offset[0], anchor_offset[1])


grid_items: dict[tuple[int, int], Item] = {}
grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]


def get_grid_pos(pos):
    return pos[0] // TILE_SIZE, pos[1] // TILE_SIZE


def get_item_at(pos):
    x, y = pos
    key = grid[y][x]
    item: Item = grid_items[key] if key else None
    return item


def spawn_item(grid_pos, item_id):
    i = ITEM_TYPES[item_id]
    item = Item(i["shape"], i["anchor_offset"])
    place_item(grid_pos, item)


def is_invalid_tile(pos):
    x, y = pos
    not_in_grid = not (0 <= x < GRID_WIDTH) or not (0 <= y < GRID_HEIGHT)
    return not_in_grid or grid[y][x]


def can_place(grid_pos, item: Item):
    if not item:
        return False
    can = True
    offset = item.anchor_offset
    x = grid_pos[0] - offset[0]
    y = grid_pos[1] - offset[1]
    for point in item.shape:
        dx = point[0] + x
        dy = point[1] + y
        if is_invalid_tile((dx, dy)):
            can = False
            break
    return can


def place_item(grid_pos, item: Item):
    can = can_place(grid_pos, item)
    if can:
        offset = item.anchor_offset
        x = grid_pos[0] - offset[0]
        y = grid_pos[1] - offset[1]
        for point in item.shape:
            dx = point[0] + x
            dy = point[1] + y
            grid[dy][dx] = (x, y)
        grid_items[(x, y)] = item
    return can


def remove_item(pos, item):
    anchor = grid[pos[1]][pos[0]]
    for point in item.shape:
        dx = point[0] + anchor[0]
        dy = point[1] + anchor[1]
        grid[dy][dx] = None
    del grid_items[anchor]


def rotate_item(item: Item):
    if not item:
        return
    shape = item.shape
    offset = item.anchor_offset
    for i, point in enumerate(shape):
        x = point[0] + offset[1] - offset[0]
        y = -point[1] + offset[0] + offset[1]
        item.shape[i] = (y, x)


def draw_drag(item: Item):
    m_pos = pygame.mouse.get_pos()
    mx = m_pos[0] // TILE_SIZE
    my = m_pos[1] // TILE_SIZE
    offset = item.anchor_offset
    x = mx - offset[0]
    y = my - offset[1]
    for point in item.shape:
        dx = point[0] + x
        dy = point[1] + y
        color = "red" if is_invalid_tile((dx, dy)) else "yellow"
        rect = pygame.Rect(dx * TILE_SIZE, dy * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, color, rect, 4)


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


spawn_item((3, 5), "Square")
spawn_item((2, 1), "T")
spawn_item((8, 4), "Single")
spawn_item((5, 7), "Cross")
spawn_item((10, 4), "L")
spawn_item((10, 9), "Z")
spawn_item((2, 11), "Line")
spawn_item((4, 11), "Line")


def main():
    original_item = None
    dragging_item = None

    running = True
    while running:
        screen.fill((30, 30, 30))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    p = get_grid_pos(event.pos)
                    if i := get_item_at(p):
                        original_item = (p, i)
                        dragging_item = Item(i.shape, i.anchor_offset)
                        remove_item(*original_item)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    p = get_grid_pos(event.pos)
                    if dragging_item:
                        if not place_item(p, dragging_item):
                            if not place_item(*original_item):
                                print("err", dragging_item, original_item)
                                offset = original_item[1].anchor_offset
                                x = original_item[0][0] - offset[0]
                                y = original_item[0][1] - offset[1]
                                for point in original_item[1].shape:
                                    dx = point[0] + x
                                    dy = point[1] + y
                                    grid[dy][dx] = (x, y)
                                grid_items[(x, y)] = original_item[1]
                    original_item = None
                    dragging_item = None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    rotate_item(dragging_item)

        draw_grid()
        if dragging_item:
            draw_drag(dragging_item)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


main()
