from pygame import Surface
from pygame.sprite import LayeredUpdates
from pymunk import Space
import shared


def update_space(callback, *sprites):
    for sprite in sprites:
        if hasattr(sprite, "body") and sprite.body is not None:
            try:
                callback(sprite.body)
            except AssertionError:
                pass
        if hasattr(sprite, "shapes") and sprite.shapes:
            try:
                callback(*sprite.shapes)
            except AssertionError:
                pass
        if hasattr(sprite, "constraints") and sprite .constraints:
            try:
                callback(*sprite.constraints)
            except AssertionError:
                pass


class Level(LayeredUpdates):
    def __init__(self, background=None, gravity=(0, -500)):
        self.background: Surface = background
        self.space: Space = Space()
        self.space.gravity = gravity
        super().__init__()

    def add(self, *sprites, **kwargs):
        super().add(*sprites, **kwargs)
        update_space(self.space.add, *sprites)

    def remove(self, *sprites):
        super().remove(*sprites)
        update_space(self.space.remove, *sprites)

    def unload(self):
        for s in self.sprites():
            s.kill()
        self.space.remove(*self.space.bodies, *self.space.shapes, *self.space.constraints)

    def update(self, *args, **kwargs):
        self.space.step(shared.space_delta_time)
        super().update(*args, **kwargs)

    def draw_bg(self, surface: Surface):
        if self.background:
            surface.blit(self.background, (0, 0))
        else:
            surface.fill("black")

    def draw(self, surface):
        surface.fblits([(i.image, i.rect) for i in filter(lambda x: shared.screen_rect.colliderect(x.rect),
                                                          self.sprites())])
        if shared.debug_physics:
            self.space.debug_draw(shared.draw_options)


level: Level = Level()


def add_collision_handler(collision_type_a, collision_type_b, begin, separate=None):
    handler = level.space.add_collision_handler(collision_type_a, collision_type_b)
    handler.begin = begin
    if separate is not None:
        handler.separate = separate
    return handler
