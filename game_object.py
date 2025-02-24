import math
from typing import Callable, Sequence
import pygame
import pymunk
from pymunk import Body, Shape, Constraint
import shared
from pygame import Surface, Vector2, Rect
from pygame.sprite import Sprite
import util
from level import level


def spawn_bounds():
    walls = [
        {
            "position": (shared.canvas_size.x / 2, shared.canvas_size.y + 50),
            "image_size": (shared.canvas_size.x, 100),
            "image_color": "white",
            "body_type": util.BODY_TYPE_STATIC
        },
        {
            "position": (shared.canvas_size.x / 2, -50),
            "image_size": (shared.canvas_size.x, 100),
            "image_color": "white",
            "body_type": util.BODY_TYPE_STATIC
        },
        {
            "position": (-50, shared.canvas_size.y / 2),
            "image_size": (100, shared.canvas_size.y),
            "image_color": "white",
            "body_type": util.BODY_TYPE_STATIC
        },
        {
            "position": (shared.canvas_size.x + 50, shared.canvas_size.y / 2),
            "image_size": (100, shared.canvas_size.y),
            "image_color": "white",
            "body_type": util.BODY_TYPE_STATIC
        }
    ]
    for w in walls:
        level.add(PhysicsBox(**w))


class GameObject(Sprite):
    def __init__(self, **kwargs):
        self._layer = kwargs.get("layer", 0)
        super().__init__(*kwargs.get("groups", []))
        self.name = kwargs.get("name", "")
        self.display_name = kwargs.get("display_name", "")
        img = kwargs.get("image", "")
        if isinstance(img, str):
            self.image, self.rect = shared.get_image(img, **kwargs)
        elif isinstance(img, Surface):
            self.image, self.rect = img, img.get_rect()
        elif isinstance(img, Rect):
            self.image, self.rect = shared.get_image("", image_size=img.size)
        else:
            self.image, self.rect = shared.get_image("", **kwargs)
        self.rect.center = kwargs.get("position", (0, 0))
        self.original_image = self.image.copy()
        self.body: Body = None
        self.shapes: list[Shape] = []
        self.constraints: list[Constraint] = []
        self.tags: list[str] = kwargs.get("tags", [])
        self.hovered_func: Callable[[GameObject], None] = None
        self.clicked_func: Callable[[GameObject], None] = None
        body, shape = self.create_body(**kwargs)
        if body is not None:
            self.body = body
            self.body.game_object = self
        if shape is not None:
            self.shapes.append(shape)

    def create_body(self, **kwargs) -> tuple[Body, Shape]:
        return None, None

    def hovered(self):
        if self.hovered_func is not None:
            self.hovered_func(self)

    def clicked(self):
        if self.clicked_func is not None:
            self.clicked_func(self)

    def get_tooltip(self, **kwargs):
        pass

    def kill(self):
        super().kill()
        level.remove(self)
        self.image = None
        self.rect = None
        self.original_image = None
        if self.body is not None and hasattr(self.body, "game_object"):
            self.body.game_object = None
        self.body = None
        self.shapes = None
        self.constraints = None
        self.tags = None


def spawn_game_object(name: str, position: Sequence[float] = (0, 0)) -> GameObject:
    params = shared.get_definition(name)
    o = None
    if params is not None:
        kc = params.get("class", GameObject.__name__)
        if isinstance(kc, type) and issubclass(kc, GameObject):
            kc = kc.__name__
        c = globals()[kc]
        p = {
            "position": position,
            **params
        }
        o = c(**p)
        level.add(o)
    return o


class SimplePhysicsObject(GameObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dampening = kwargs.get("dampening", 0.9)

    def create_body(self, **kwargs):
        return super().create_body(**kwargs)
    
    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        center = util.flip_y(self.body.position)
        self.image = pygame.transform.rotate(self.original_image, math.degrees(self.body.angle))
        self.rect = self.image.get_rect(center=center)


class PhysicsBox(SimplePhysicsObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def create_body(self, **kwargs):
        return util.create_physics_box(self.rect.size, **kwargs)


class PhysicsCircle(SimplePhysicsObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def create_body(self, **kwargs):
        return util.create_physics_circle(self.rect.size[0] / 2, **kwargs)


class PhysicsAuto(SimplePhysicsObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def create_body(self, **kwargs):
        return util.create_physics_poly(**{
            "points": util.auto_geometry(self.original_image),
            **kwargs
        })


class PhysicsAutoSmooth(SimplePhysicsObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def create_body(self, **kwargs):
        return util.create_physics_poly(**{
            "points": util.auto_geometry_smooth(self.original_image),
            **kwargs
        })


class PhysicsThruster(SimplePhysicsObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.thrust_max = kwargs.get("thrust_max", 500)
        self.acceleration = kwargs.get("acceleration", 5) * 10 ** 5
        self.max_speed = kwargs.get("max_speed", 500)
        self.thrust = 0

    def create_body(self, **kwargs):
        b, s = util.create_physics_box(self.rect.size, **kwargs)

        def v_func(body, gravity, dampening, dt):
            d = dampening * self.dampening if not math.isnan(dampening) else 0
            return pymunk.Body.update_velocity(body, gravity, d, dt)

        b.velocity_func = v_func
        return b, s

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        if self.body and self.body.velocity.length < self.max_speed:
            dx = math.cos(self.body.angle) * self.thrust
            dy = math.sin(self.body.angle) * self.thrust
            df = Vector2(dx, dy) * self.acceleration
            self.body.apply_force_at_local_point((df.x, df.y), (0, 0))


class PhysicsEffect(SimplePhysicsObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.time_alive = kwargs.get("time_alive", 1)

    def create_body(self, **kwargs):
        return util.create_physics_box(self.rect.size, **kwargs)

    def create_physics_objects(self, **kwargs):
        b, s = util.create_physics_box(self.rect.size, **kwargs)

        def v_func(body, gravity, dampening, dt):
            d = dampening * self.dampening if not math.isnan(dampening) else 0
            return pymunk.Body.update_velocity(body, gravity, d, dt)

        b.velocity_func = v_func
        return b, s

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.time_alive -= shared.delta_time
        if self.time_alive < 0:
            self.kill()
