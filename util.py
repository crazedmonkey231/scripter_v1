import math
import random
import string
from collections import defaultdict
from typing import Sequence
import numpy
import pymunk
from numpy import ndarray
import pygame
from pygame import Surface, Rect, Vector2
from pygame.sprite import Sprite, AbstractGroup
from pymunk import Shape, Vec2d, Space
import pymunk.autogeometry
import pymunk.pygame_util
from pymunk import BB


def log(msg):
    """Default log function"""
    print(msg)


def tree():
    """Tree maker using defaultdict"""
    return defaultdict(tree)


def is_all_of_type(objs, types):
    """Is list of all type"""
    return all([isinstance(t, types) for t in objs])


# Set cursor to image
def set_cursor(img: Surface, offset=(0, 0)):
    """Set mouse cursor with an offset"""
    pygame.mouse.set_cursor(offset, img)


# Check inside widow bounds
def is_within_screen_bounds(pos, screen_size):
    """Check it pos is inside screen"""
    return 0 <= pos[0] <= screen_size[0] and 0 <= pos[1] <= screen_size[1]


def map_range(value, start1, stop1, start2, stop2):
    """Map a range to another"""
    return start2 + (stop2 - start2) * ((value - start1) / (stop1 - start1))


def clamp_value(value, start, stop):
    """Clamp value between range"""
    return min(max(value, start), stop)


# Map range clamped
def map_range_clamped(value, start1, stop1, start2, stop2):
    """Map and clamp value between range"""
    return clamp_value(map_range(value, start1, stop1, start2, stop2), start2, stop2)


def lerp_angle(start, end, t, factor=1):
    """Lerp between two angles, handling wraparound correctly."""
    diff = (end - start + 180) % 360 - 180  # Get shortest rotation direction
    t = min(t * factor, 1)
    return start + diff * t  # Lerp the angle


def angles_equal(angle1, angle2, threshold=0.5):
    """Check if two angles are approximately equal within a small threshold."""
    return abs((angle1 - angle2 + 180) % 360 - 180) < threshold


def get_bounding_rect_from_center(rects):
    """Get bounding rect from list of rects"""
    if not rects:
        return None

    # Find min and max for x and y
    min_x = min(rect.left for rect in rects)
    max_x = max(rect.right for rect in rects)
    min_y = min(rect.top for rect in rects)
    max_y = max(rect.bottom for rect in rects)

    # Width and height of the bounding rectangle
    width = max_x - min_x
    height = max_y - min_y

    # Calculate the center
    center_x = min_x + width // 2
    center_y = min_y + height // 2

    # Create the bounding rect from the center
    bounding_rect = pygame.Rect(0, 0, width, height)
    bounding_rect.center = (center_x, center_y)

    return bounding_rect


def draw_lines_between_rects(rects, surface=None, bounding_rect=None, fill_color=None,
                             line_color=(255, 255, 255), thickness=10):
    """Draw lines between rects returning a surface and the bounding rect"""
    if len(rects) < 2:
        return  # Need at least 2 rectangles to draw lines

    if bounding_rect is None:
        bounding_rect = get_bounding_rect_from_center(rects)

    if surface is None:
        surface = Surface(bounding_rect.size).convert_alpha()

    if fill_color is not None:
        surface.fill(fill_color)
    else:
        surface.fill((0, 0, 0, 0))

    # Offset and draw lines between rectangle centers
    for i in range(len(rects) - 1):
        start = (rects[i].centerx - bounding_rect.left, rects[i].centery - bounding_rect.top)
        end = (rects[i + 1].centerx - bounding_rect.left, rects[i + 1].centery - bounding_rect.top)
        pygame.draw.line(surface, line_color, start, end, thickness)

    return surface, bounding_rect


def get_random_rgb():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return r, g, b, 255


def get_rgba_pixel_array(surface: Surface):
    """Get a ndarray matrix of a surface filled with rgba values of pixels"""
    w, h = surface.get_size()
    s = w * h
    a_matrix: ndarray = numpy.zeros((w, h, 4))
    for i in range(s):
        row = i // h
        col = i % h
        a_matrix[row, col] = tuple(surface.get_at((row, col)))
    return a_matrix


def get_rgba_pixel_array_outline(surface: Surface, outline_color=(0, 255, 255, 255), outline_width: int = 3):
    """Get an outline ndarray matrix of a surface filled with rgba values of pixels with a given width"""
    w, h = surface.get_size()
    s = w * h
    a_matrix: ndarray = numpy.zeros((w, h, 4))

    def set_pixel(x, y):
        if not (0 <= x < w and 0 <= y < h):
            return
        if not a_matrix[x, y][3] and tuple(a_matrix[x, y]) != outline_color:
            a_matrix[x, y] = outline_color

    for i in range(s):
        row = i // h
        col = i % h
        color = tuple(surface.get_at((row, col)))
        if color[3]:
            a_matrix[row, col] = tuple(surface.get_at((row, col)))
            for ow in range(outline_width):
                set_pixel(row, col - ow)
                set_pixel(row, col + ow)
                set_pixel(row - ow, col)
                set_pixel(row + ow, col)
    return a_matrix


def write_rgb_pixel_array(surface: Surface, matrix: ndarray):
    """Write a ndarray matrix of colors onto a surface"""
    w, h = surface.get_size()
    s = w * h
    for i in range(s):
        row = i // h
        col = i % h
        surface.set_at((row, col), matrix[row, col])


def get_sprite_collide_by_mask(source: Sprite, group: AbstractGroup, do_kill: bool = False) -> list[Sprite]:
    """Mask based sprite collisions"""
    return pygame.sprite.spritecollide(source, group, do_kill, pygame.sprite.collide_mask)


def rotate_image(original_image: Surface, angle: float, center) -> tuple[Surface, Rect]:
    """Rotate image"""
    rotated_image = pygame.transform.rotate(original_image, angle)
    new_rect = rotated_image.get_rect(center=center)
    return rotated_image, new_rect


def scale_image_basic(original_image: Surface, new_size: tuple, center) -> tuple[Surface, Rect]:
    """Scale image basic"""
    new_image = pygame.transform.scale(original_image, new_size)
    new_rect = new_image.get_rect(center=center)
    return new_image, new_rect


def scale_image_smooth(original_image: Surface, new_size: Sequence[float], center) -> tuple[Surface, Rect]:
    """Scale image smooth"""
    new_image = pygame.transform.smoothscale(original_image, new_size)
    new_rect = new_image.get_rect(center=center)
    return new_image, new_rect


def create_hover_img(surface: Surface, color=(100, 100, 100, 150)):
    """Create a simple hover image"""
    s = surface.copy().convert_alpha()
    s.fill(color)
    s2 = surface.copy()
    s2.blit(s, (0, 0))
    return s2, s2.get_rect()


def create_sized_img(surface: Surface, size=(64, 64), center=(0, 0)):
    """Create a scaled image"""
    s = surface.copy().convert_alpha()
    return scale_image_basic(s, size, center)


def float_movement_sin(amplitude: float = 25, speed: float = 1):
    """Sin curve movement"""
    time = pygame.time.get_ticks()
    delta = amplitude * math.sin(speed * time)
    return delta


def float_movement_cos(amplitude: float = 25, speed: float = 1):
    """Cos curve movement"""
    time = pygame.time.get_ticks()
    delta = amplitude * math.cos(speed * time)
    return delta


def generate_simple_id(size: int = 10):
    """Generate simple id"""
    characters = string.ascii_letters + string.digits
    random_id = ''.join(random.choices(characters, k=size))
    return random_id


def generate_grid(grid_size: Sequence[int], grid_tile_size: Sequence[int], grid_tile_padding: Sequence[int] = (0, 0),
                  grid_tile_offset: Sequence[int] = (0, 0)):
    """Generate grid"""
    width = grid_size[0]
    height = grid_size[1]
    s = width * height
    points = []
    for i in range(s):
        row_dist = grid_tile_size[0] + grid_tile_padding[0]
        col_dist = grid_tile_size[1] + grid_tile_padding[1]
        row = ((i // height) * row_dist) + grid_tile_offset[0]
        col = ((i % height) * col_dist) + grid_tile_offset[1]
        point = (row, col)
        points.append(point)
    return points


def generate_line(start_pos: Vector2, target_pos: Vector2):
    """Generate line"""
    points = []
    dist_target = target_pos - start_pos
    dist_target_len = dist_target.length()
    if dist_target_len > 0:
        dist_target_norm = dist_target.normalize()
        rect_x = start_pos.x
        rect_y = start_pos.y
        for _ in range(int(dist_target_len)):
            rect_x += dist_target_norm.x
            rect_y += dist_target_norm.y
            points.append(Vector2(rect_x, rect_y))
    return points


def generate_arch(start_pos: Vector2, target_pos: Vector2, max_arch_height: float = 100, max_arch_delta: float = 10,
                  inverse: bool = False):
    """Generate arch"""
    points = []
    inverse = -1 if inverse else 1
    dist_target = target_pos - start_pos
    dist_target_len = dist_target.length()
    if dist_target_len > 0:
        dist_target_norm = dist_target.normalize()
        dist_target_abs = Vector2(abs(dist_target.x), abs(dist_target.y))
        dist_target_delta = int(dist_target_len)
        rect_x = start_pos.x
        arch_height_max = max_arch_height
        arch_height = clamp_value(dist_target_abs.x, 0, arch_height_max)
        delta_arch = map_range_clamped(dist_target_len, 0, 1000, 1, max_arch_delta)
        epsilon = 1e-6
        for _ in range(dist_target_delta):
            rect_x += dist_target_norm.x
            norm_position = abs((rect_x - start_pos.x) / (dist_target_abs.x + epsilon))
            rect_y = ((1 - norm_position) * start_pos.y + norm_position * target_pos.y -
                      arch_height * inverse * delta_arch * norm_position * (1 - norm_position))
            points.append(Vector2(rect_x, rect_y))
    return points


def generate_circle(center_pos: Vector2, radius: float = 5, clockwise=True, step_size: int = 10):
    """Generate circle"""
    points = []
    start_x = center_pos[0]
    start_y = center_pos[1]
    r = range(0, 360, step_size) if clockwise else range(360, 0, -step_size)
    for angle in r:
        r_angle = math.radians(angle)
        rect_x = start_x + math.cos(r_angle) * radius
        rect_y = start_y + math.sin(r_angle) * radius
        points.append(Vector2(rect_x, rect_y))
    return points


def interpolate_color_rgb(color1, color2, factor) -> tuple[int, int, int]:
    """Interpolates between color1 and color2 using a factor."""
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    r = clamp_value(int(r1 + (r2 - r1) * factor), 0, 255)
    g = clamp_value(int(g1 + (g2 - g1) * factor), 0, 255)
    b = clamp_value(int(b1 + (b2 - b1) * factor), 0, 255)
    return r, g, b


def interpolate_color_rgba(color1, color2, factor) -> tuple[int, int, int, int]:
    """Interpolates between color1 and color2 using a factor."""
    r1, g1, b1, a1 = color1
    r2, g2, b2, a2 = color2
    r = clamp_value(int(r1 + (r2 - r1) * factor), 0, 255)
    g = clamp_value(int(g1 + (g2 - g1) * factor), 0, 255)
    b = clamp_value(int(b1 + (b2 - b1) * factor), 0, 255)
    a = clamp_value(int(a1 + (a2 - a1) * factor), 0, 255)
    return r, g, b, a


# Simple text maker rgba
def make_simple_text(**kwargs) -> tuple[Surface, Rect]:
    """Text maker"""
    text = kwargs.get("text")
    text_size = kwargs.get("size", 64)
    anti_alias = kwargs.get("anti_alias", True)
    f_color = kwargs.get("color", (255, 255, 255, 255))
    bg_color = kwargs.get("bg_color", (0, 0, 0, 255))
    wrap_length = kwargs.get("wrap_length", 300)
    font = pygame.font.Font(None, text_size)
    text = font.render(text, anti_alias, f_color, bg_color, wrap_length)
    text_rect = text.get_rect(**kwargs.get("rect_kwargs", {}))
    if ck := kwargs.get("color_key"):
        text.set_colorkey(ck)
    return text, text_rect


def make_scroll_text(text: str, **kwargs):
    t = ""
    gif = []
    for c in text:
        t += c
        s, r = make_simple_text(**{"text": t, **kwargs})
        gif.append((s, r))
    return gif


TREND_NEUTRAL = "Neutral"
TREND_DECREASING = "Decreasing"
TREND_INCREASING = "Increasing"


def get_data_trend(data: list[tuple], idx: int = 0, length: int = 7) -> tuple[str, float]:
    """Gets a trend value along with associated text using a data list with specified index"""
    if not data or len(data) < 2 or length <= 0:
        return TREND_NEUTRAL, 0
    f_data = data[-length:]
    changes = []
    for i in range(len(f_data) - 1):
        f_data_idx = f_data[i][idx]
        if f_data[i][idx] == 0:
            changes.append(0)
        else:
            changes.append((f_data[i + 1][idx] - f_data_idx) / f_data_idx)
    avg_change = round(sum(changes) / len(changes), 4)
    if avg_change > 0:
        trend_text = TREND_INCREASING
    elif avg_change < 0:
        trend_text = TREND_DECREASING
    else:
        trend_text = TREND_NEUTRAL
    return trend_text, avg_change


M_TXT_HIGH = "High"
M_TXT_LOW = "Low"
M_TXT_NEUTRAL = "Neutral"


def get_multiplier_text(amount: float) -> str:
    """Simple getter for text for a multiplier"""
    if amount > 1:
        return M_TXT_HIGH
    elif amount < 1:
        return M_TXT_LOW
    elif amount == 1:
        return M_TXT_NEUTRAL


def get_graph_points(size: Sequence[int], data_list: list[float]) -> list[tuple[int, int]]:
    """Get graph points. Output can be directly used with pygame.draw.lines"""
    draw_points = []
    if len(data_list) > 0:
        data_list = [0, *data_list]
        width = size[0]
        height = size[1]

        data_max = max(data_list)
        data_min = min(data_list)

        def normalize(data):
            return height - int((data - data_min) / (data_max - data_min) * height)

        data_len = len(data_list)
        if data_len > 1:
            x_step = width // (data_len - 1)
        else:
            x_step = 0

        for i in range(data_len - 1):
            # Calculate x positions
            x1 = i * x_step
            x2 = (i + 1) * x_step

            # Normalize y positions
            y1 = normalize(data_list[i])
            y2 = normalize(data_list[i + 1])

            draw_points.append((x1, y1))
            draw_points.append((x2, y2))
    else:
        draw_points.append((0, 0))
        draw_points.append((0, 0))
    return draw_points


def get_sprite_distance(from_pos: Sequence[float], to_sprite: Sprite):
    """Get Sprite distance from pos"""
    center = to_sprite.rect.center
    distance = (from_pos[0] - center[0]) ** 2 + (from_pos[1] - center[1]) ** 2
    return distance


def get_sprite_distance_sqrt(from_pos: Sequence[float], to_sprite: Sprite):
    """Get Sprite distance from pos, sqrt"""
    center = to_sprite.rect.center
    distance = math.sqrt(from_pos[0] - center[0] ** 2 + (from_pos[1] - center[1]) ** 2)
    return distance


def mouse_grab(mouse_grabbed):
    """Hide mouse and grab screen"""
    pygame.event.set_grab(mouse_grabbed)
    pygame.mouse.set_visible(not mouse_grabbed)


#
# Begin Particle functions
# Needs particle list and custom draw surface set up that gets blit onto the screen as either an overlay or underlay.
# Using screen surface for creating or updating will cause unwanted overwriting of sprite images.
# If being used in sprite update method, run update first then create new or the color on creation will be overridden.
#

# Create initial rect particle
def create_rect_particle(draw_surface: Surface, particles: list, color, center: Vector2, size: tuple, width: float):
    s_width, s_height = size
    width_h = s_width // 2
    height_h = s_height // 2
    left = center.x - width_h
    right = center.y - height_h
    particles.append(pygame.draw.rect(draw_surface, color, (left, right, s_width, s_height), width))


# Update rect particles
def update_rect_particles(draw_surface: Surface, particles: list, time_alive: float, decay_factor: float = 2.0,
                          color=(255, 255, 255, 255)):
    n_trails = [t for t in particles if t.size[0] != 0 and t.size[1] != 0]
    clear_rect_particles(draw_surface, n_trails)
    for trail in n_trails:
        r: Rect = trail
        if time_alive % decay_factor == 0:
            r = trail.scale_by(.99, .99)
            r.center = trail.center
        trail[:] = pygame.draw.rect(draw_surface, color, r, r.width)
    particles[:] = n_trails


# Clear rect particles
def clear_rect_particles(draw_surface: Surface, particles: list):
    n_trails = [t for t in particles if t.size[0] != 0 and t.size[1] != 0]
    for trail in n_trails:
        pygame.draw.rect(draw_surface, (0, 0, 0, 0), trail, trail.width)


# Create initial circle particle
def create_circle_particle(draw_surface: Surface, particles: list, color, center: Vector2, radius: tuple, width: float):
    particles.append(pygame.draw.circle(draw_surface, color, center, radius, width))


# Update circle particles
def update_circle_particles(draw_surface: Surface, particles: list, time_alive: float, decay_factor: float = 2.0,
                            color=(255, 255, 255, 255)):
    n_trails = [t for t in particles if t.size[0] != 0 and t.size[1] != 0]
    for trail in n_trails:
        pygame.draw.rect(draw_surface, (0, 0, 0, 0), trail, trail.width)
        r = trail
        if time_alive % decay_factor == 0:
            r = trail.scale_by(.99, .99)
        trail[:] = pygame.draw.circle(draw_surface, color, trail.center, r.width // 2)
    particles[:] = n_trails


# Todo clear circle particles
def clear_circle_particles(draw_surface: Surface, particles: list):
    n_trails = [t for t in particles if t.size[0] != 0 and t.size[1] != 0]
    for trail in n_trails:
        pygame.draw.rect(draw_surface, (0, 0, 0, 0), trail, trail.width)


#
# End particle utils
#

BODY_TYPE_STATIC = pymunk.Body.STATIC
BODY_TYPE_DYNAMIC = pymunk.Body.DYNAMIC
BODY_TYPE_KINEMATIC = pymunk.Body.KINEMATIC


def flip_y(point):
    """flip_y for physics objects in pymunk space"""
    from shared import canvas_size
    return point[0], -point[1] + canvas_size.y


def create_body(params, **kwargs):
    """Create a simple physics body"""
    body = pymunk.Body(*params)
    body.position = flip_y(kwargs.get("position", (0, 0)))
    body.velocity = kwargs.get("velocity", (0, 0))
    return body


def create_physics_box(size: Sequence[float], **kwargs):
    """Create a physics box"""
    w = size[0] * 0.5
    h = size[1] * 0.5
    p = {
        "points": [(-w, -h), (-w, h), (w, h), (w, -h)],
        **kwargs
    }
    return create_physics_poly(**p)


def create_physics_circle(radius: float, **kwargs):
    """Create a physics circle"""
    mass = kwargs.get("mass", 1)
    body_type = kwargs.get("body_type", BODY_TYPE_STATIC)
    moment = pymunk.moment_for_circle(mass, 0, radius)

    body = create_body((mass, moment, body_type), **kwargs)

    shape: Shape = pymunk.Circle(body, radius)
    shape.density = kwargs.get("density", 1)
    shape.elasticity = kwargs.get("elasticity", 1)
    shape.friction = kwargs.get("friction", 1)
    shape.collision_type = kwargs.get("collision_type", 0)
    return body, shape


def create_physics_poly(**kwargs):
    """Create a physics poly"""
    points = kwargs.get("points", [])
    mass = kwargs.get("mass", 1)
    body_type = kwargs.get("body_type", BODY_TYPE_STATIC)
    moment = pymunk.moment_for_poly(mass, points, (0, 0))

    body = create_body((mass, moment, body_type), **kwargs)

    shape = pymunk.Poly(body, points)
    shape.density = kwargs.get("density", 1)
    shape.elasticity = kwargs.get("elasticity", 1)
    shape.friction = kwargs.get("friction", 1)
    shape.collision_type = kwargs.get("collision_type", 0)
    return body, shape


def rotate_body_toward_position(body, target_pos, rotation_speed=5):
    """Rotate a body toward a position"""
    dx = target_pos[0] - body.position.x
    dy = target_pos[1] - body.position.y
    angle_to_center = math.atan2(dy, dx)

    # Calculate the shortest angular distance
    angle_diff = angle_to_center - body.angle
    angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi  # Normalize between -π and π

    # Apply torque based on angle difference
    torque = angle_diff * rotation_speed * 10 ** 5
    body.torque = torque


def get_overlapping_bodies(space, pos):
    """Gets all bodies at a point in space"""
    point_query = space.point_query(pos, 0, pymunk.ShapeFilter())
    bodies = [result.shape.body for result in point_query]
    return bodies


def hover_physics_obj(space: Space, mouse_pos):
    """Call the hover func on any physics body based game object at mouse location"""
    p = Vec2d(*flip_y(mouse_pos))
    # hit = space.point_query_nearest(p, 5, pymunk.ShapeFilter())
    bodies = get_overlapping_bodies(space, p)
    if not bodies:
        return None
    hit = max(bodies, key=lambda body: body.game_object.layer)
    go = hit.game_object
    go.hovered()
    return go


def grab_physics_obj(space, mouse_pos, force=25):
    """Grabs a physics object at mouse position"""
    p = Vec2d(*flip_y(mouse_pos))
    # hit = space.point_query_nearest(p, 5, pymunk.ShapeFilter())

    point_query = space.point_query(p, 0, pymunk.ShapeFilter())
    bodies = [result for result in point_query if result.shape.body.body_type == pymunk.Body.DYNAMIC]

    if bodies:
        hit = max(bodies, key=lambda b: b.shape.body.game_object.layer)
        shape = hit.shape
        body = shape.body
        if hit.distance > 0:
            nearest = hit.point
        else:
            nearest = p
        mouse_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        mouse_joint = pymunk.PivotJoint(
            mouse_body,
            body,
            (0, 0),
            body.world_to_local(nearest),
            # (0, 0)
        )
        mouse_rot_spring = pymunk.DampedRotarySpring(mouse_body, body, 0, 3000000, 1)
        mouse_joint.max_force = force * 10 ** 5
        mouse_joint.error_bias = (1 - 0.15) ** 60
        space.add(mouse_body, mouse_joint, mouse_rot_spring)
        return [mouse_body, mouse_joint, mouse_rot_spring]
    else:
        return []


def click_physics_obj(space, mouse_pos):
    """Call the clicked func on any physics body based game object at mouse location"""
    i = hover_physics_obj(space, mouse_pos)
    if i is not None:
        i.clicked()


def auto_geometry(surface: Surface):
    """Create simple auto geometry lines from a surface, output can be used in create_physics_poly"""
    r = surface.get_rect()
    w = r.width
    h = r.height

    def sample_func(point):
        try:
            p = int(point[0]), int(point[1])
            color = surface.get_at(p)
            return color[3]
        except IndexError:
            return 0

    line_set = pymunk.autogeometry.march_hard(
        BB(0, h-1, w-1, 0), w, h, 0, sample_func
    )
    lines = []
    for polyline in line_set:
        line = pymunk.autogeometry.simplify_vertexes(polyline, 1)
        for i in range(len(line)):
            p1 = line[i]
            lines.append((p1.x - w / 2, h / 2 - p1.y))

    return lines


def auto_geometry_smooth(surface: Surface):
    """Create simple auto geometry lines from a surface with smoothing, output can be used in create_physics_poly"""
    r = surface.get_rect()
    w = r.width
    h = r.height

    def sample_func(point):
        try:
            p = int(point[0]), int(point[1])
            color = surface.get_at(p)
            return color[3]
        except IndexError:
            return 0

    line_set = pymunk.autogeometry.march_soft(
        BB(0, h-1, w-1, 0), w, h, 0, sample_func
    )
    lines = []
    for polyline in line_set:
        line = pymunk.autogeometry.simplify_curves(polyline, 1)
        for i in range(len(line)):
            p1 = line[i]
            lines.append((p1.x - w / 2, h / 2 - p1.y))

    return lines

