import pygame
from pygame import Surface, Vector2, Rect
from pygame.sprite import Sprite, GroupSingle

import collisions
import game_object
import shared
import util
from binding_manager import add_binding
from level import level, add_collision_handler
from task_manager import Task, LerpPosition, LerpPositionArch, LerpPositionCircle, Sequencer, TickWait, DestroySprite, \
    LerpRotation, DestroySpritePosition, GifAnimation, PlaySound, CircleFollow, CameraUpdate


class PlayerController(Sprite):
    def __init__(self):
        super().__init__()
        size = (1, 1)
        self.image = Surface(size).convert_alpha()
        self.image.fill((0, 0, 0, 0))
        self.rect = self.image.get_rect(center=shared.screen_size_half)

        # CameraUpdate().start()

        def toggle_pause(event):
            if event.key == pygame.K_SPACE:
                shared.paused = not shared.paused
        add_binding(pygame.KEYDOWN, self, toggle_pause)

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

        count = [0, True]

        def click(event):
            if event.button == 1:
                pass

                # gif = shared.get_gif("ball")
                sprite = shared.get_plain_sprite("fsh")
                sprite.rect.center = event.pos
                sprite.layer = 1
                level.add(sprite)

                Sequencer(
                    CircleFollow(sprite, self, 50, 100, True, 1, True),
                    LerpRotation(sprite, shared.screen_size_half,
                                 looping=True),
                ).build(True, True).start()

                # Sequencer(
                #     # GifAnimation(sprite, gif, 125),
                #     # LerpPosition(sprite, pos),
                #     PlaySound("chime_bell"),
                #     TickWait(50),
                #     Sequencer(
                #         LerpPosition(sprite, self, True),
                #         LerpRotation(sprite, self, True),
                #         DestroySpritePosition(sprite, self),
                #     ).on_end(
                #         PlaySound("chime_bell")
                #     ).build(True, True),
                # ).build(True).start()

                # Sequencer(
                #     LerpRotation(sprite, shared.screen_size_half),
                #     TickWait(15),
                #     LerpPosition(sprite, shared.screen_size_half),
                #     TickWait(15),
                #     Sequencer(
                #         LerpPosition(sprite, self, True),
                #         LerpRotation(sprite, self, True),
                #         DestroySpritePosition(sprite, self)
                #     ).build(True, True),
                # ).build(True).start()

                # Sequencer(
                #     LerpPosition(sprite, self),
                #     LerpRotation(sprite, self),
                # ).build(True, True).start()

                # LerpRotation(sprite, self).start()
                # LerpPosition(sprite, self).start()

                # Sequencer(
                #     TickWait(5),
                #     # LerpPositionArch(sprite, Vector2(event.pos), shared.screen_size_half, 500, True),
                #     # TickWait(5),
                #     # LerpPosition(sprite, shared.screen_size_half, Vector2(event.pos), 500, True),
                #     # TickWait(5),
                #     LerpRotation(sprite, self),
                #     TickWait(5),
                #     DestroySprite(sprite)
                # ).build(True).start()

        add_binding(pygame.MOUSEBUTTONDOWN, self, click)

        def mv(event):
            self.rect.center = shared.local_to_world_pos(event.pos)
            # self.body.position = util.flip_y(self.rect.center)
            # shared.camera_target = self.rect.center

        add_binding(pygame.MOUSEMOTION, self, mv)
