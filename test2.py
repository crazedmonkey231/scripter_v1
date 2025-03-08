import pygame

# Constants
TILE_SIZE = 32
GRID_WIDTH, GRID_HEIGHT = 10, 10
SCREEN_WIDTH, SCREEN_HEIGHT = GRID_WIDTH * TILE_SIZE, GRID_HEIGHT * TILE_SIZE

# Buildings
buildings = {}  # { (x, y): {"id": X, "size": (w, h), "rotated": False} }
grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# Dragging
dragging_building = None


def can_place_building(grid_x, grid_y, width, height):
    """Check if a building can be placed at the given grid position."""
    if grid_x + width > GRID_WIDTH or grid_y + height > GRID_HEIGHT:
        return False  # Out of bounds
    for y in range(grid_y, grid_y + height):
        for x in range(grid_x, grid_x + width):
            if grid[y][x] is not None:
                return False  # Space is occupied
    return True


def place_building(grid_x, grid_y, width, height, building_id):
    """Place a building in the grid."""
    if can_place_building(grid_x, grid_y, width, height):
        for y in range(grid_y, grid_y + height):
            for x in range(grid_x, grid_x + width):
                grid[y][x] = {"id": building_id, "size": (width, height), "anchor": (grid_x, grid_y)}
        buildings[(grid_x, grid_y)] = {"id": building_id, "size": (width, height), "rotated": False}
        return True
    return False


def remove_building(grid_x, grid_y):
    """Remove a building from the grid."""
    if grid[grid_y][grid_x] and (grid_x, grid_y) in buildings:
        width, height = buildings[(grid_x, grid_y)]["size"]
        b = buildings[(grid_x, grid_y)]
        for y in range(grid_y, grid_y + height):
            for x in range(grid_x, grid_x + width):
                grid[y][x] = None
        del buildings[(grid_x, grid_y)]
        return b


def get_building_at(mouse_x, mouse_y):
    """Find the building at a given screen position."""
    grid_x = mouse_x // TILE_SIZE
    grid_y = mouse_y // TILE_SIZE
    if grid[grid_y][grid_x]:
        return grid[grid_y][grid_x]["anchor"]  # Return anchor position
    return None


def rotate_building(grid_x, grid_y):
    """ Rotate a building if possible """
    if (grid_x, grid_y) in buildings:
        building = buildings[(grid_x, grid_y)]
        old_width, old_height = building["size"]
        new_width, new_height = old_height, old_width  # Swap dimensions

        # Remove old placement
        remove_building(grid_x, grid_y)

        # Try to place rotated version
        if place_building(grid_x, grid_y, new_width, new_height, building["id"]):
            buildings[(grid_x, grid_y)]["rotated"] = not building["rotated"]
        else:
            # If rotation fails, put the old version back
            place_building(grid_x, grid_y, old_width, old_height, building["id"])


# Test placements
place_building(2, 2, 3, 2, "House")
place_building(5, 5, 2, 3, "Factory")

running = True

while running:
    screen.fill((50, 50, 50))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click to select & drag
                selected_building = remove_building(*get_building_at(*event.pos))
                if selected_building:
                    dragging_building = selected_building
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and dragging_building:  # Release to place
                new_x, new_y = event.pos[0] // TILE_SIZE, event.pos[1] // TILE_SIZE
                width, height = dragging_building["size"]

                if not place_building(new_x, new_y, width, height, dragging_building["id"]):
                    place_building(*dragging_building, width, height, dragging_building["id"])  # Snap back
                dragging_building = None  # Stop dragging
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                if dragging_building:
                    size = dragging_building["size"]
                    dragging_building["size"] = (size[1], size[0])

    # Get mouse position if dragging
    if dragging_building:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        grid_x, grid_y = mouse_x // TILE_SIZE, mouse_y // TILE_SIZE

    # Draw Grid
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, (100, 100, 100), rect, 1)

            # Draw Buildings
            if grid[y][x]:
                anchor_x, anchor_y = grid[y][x]["anchor"]
                color = (255, 255, 0) if dragging_building == (anchor_x, anchor_y) else (0, 255, 0)
                pygame.draw.rect(screen, color, rect)

    # Draw Dragging Preview
    if dragging_building:
        width, height = dragging_building["size"]
        for dy in range(height):
            for dx in range(width):
                rect = pygame.Rect((grid_x + dx) * TILE_SIZE, (grid_y + dy) * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(screen, (255, 255, 255), rect, 2)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
