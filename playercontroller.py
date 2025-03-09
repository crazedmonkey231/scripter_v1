import shared
from task_manager import *


def click(task, *args, **kwargs):
    if pygame.mouse.get_pressed()[0]:

        sprite = shared.get_plain_sprite(None)
        sprite.rect.center = shared.get_mouse_pos()
        sprite.layer = 0

        def s(task):
            shared.play_sound("chime_bell")
            return task.cont

        ScrollingText(sprite, "Testing out scrolling text", speed=5, text_task=Task(s),
                      rect_kwargs={"topleft": shared.get_mouse_pos()}).start()

        level.add(sprite)

    return task.cont


class PlayerController(Sprite):
    def __init__(self):
        super().__init__()
        size = (1, 1)
        self.image = Surface(size).convert_alpha()
        self.image.fill((0, 0, 0, 0))
        self.rect = self.image.get_rect(center=shared.screen_size_half)

        CameraUpdate().start()

        def toggle_pause(task):
            if not self.alive():
                return task.end
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                shared.paused = not shared.paused
            return task.cont

        Task(toggle_pause).bind(pygame.KEYDOWN)

        # body, shape = util.create_physics_box(size, density=1000, mass=100, friction=10,
        #                                       body_type=util.BODY_TYPE_KINEMATIC,
        #                                       collision_type=collisions.CT_DEFAULT)
        # self.body = body
        # self.shapes = [shape]
        #
        # game_object.spawn_bounds()
        #
        # game_object.spawn_game_object("simple_effect", shared.screen_size_half)

        # add_collision_handler(collisions.CT_DEFAULT, collisions.CT_DEFAULT, lambda i, j, k: True)

        params = ([], {"target": self})
        Task(click, params).bind(pygame.MOUSEBUTTONDOWN)

        def mv(task):
            if not self.alive():
                return task.end
            self.rect.center = shared.get_mouse_pos()
            return task.cont

        # Task(mv).bind(pygame.MOUSEMOTION)
        Task(mv).start()
        #
        # LAYERS = 3  # Number of parallax layers
        # SPEED_MULTIPLIERS = [0.2, 0.4, 0.6]  # How much each layer moves with the player
        # stars = []
        # num_stars = 100
        #
        # v = (0, 1)
        # r = shared.canvas.get_rect()
        #
        # for _ in range(LAYERS):
        #     layer_stars = []
        #     for _ in range(num_stars // LAYERS):
        #         x = random.randint(0, r.width)
        #         y = random.randint(0, r.height)
        #         layer_stars.append([x, y])  # Store (x, y) position
        #     stars.append(layer_stars)
        #
        # def parallax_effect(task):
        #     if not self.alive():
        #         return task.end
        #
        #     for layer in range(LAYERS):
        #         for star in stars[layer]:
        #             star[0] -= v[0] * SPEED_MULTIPLIERS[layer]
        #             star[0] %= r.width
        #
        #             star[1] += v[1] * SPEED_MULTIPLIERS[layer]
        #             star[1] %= r.height
        #
        #             # Draw star with different brightness for depth effect
        #             brightness = 100 + layer * 50
        #             color = (brightness, brightness, brightness)
        #             center = Vector2(star) + Vector2(r.center) - Vector2(r.size) // 2
        #             radius = 2 - layer // 2
        #             pygame.draw.circle(shared.canvas, color, center, radius)
        #     return task.cont
        #
        # Task(parallax_effect).start(1)