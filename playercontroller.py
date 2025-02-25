import pygame
from pygame import Surface, Vector2, Rect
from pygame.sprite import Sprite, GroupSingle
import shared
import util
from binding_manager import add_binding
from level import level
from task_manager import Task, LerpPosition, LerpPositionArch, LerpPositionCircle, Sequencer, TickWait, DestroySprite, \
    LerpRotation, DestroySpritePosition, GifAnimation, PlaySound


class PlayerController(Sprite):
    def __init__(self):
        super().__init__()
        self.image = Surface((1, 1)).convert_alpha()
        self.image.fill((0, 0, 0, 0))
        self.rect = self.image.get_rect(center=shared.screen_size_half)

        def toggle_pause(event):
            if event.key == pygame.K_SPACE:
                shared.paused = not shared.paused
        add_binding(pygame.KEYDOWN, self, toggle_pause)

        # body, shape = util.create_physics_box((64, 64), body_type=pymunk.Body.DYNAMIC)
        # self.body = body
        # self.shapes = [shape]
        # self.body.position = util.flip_y(shared.screen_size_half)

        count = [0, True]

        def click(event):
            if event.button == 1:
                pass

                # gif = shared.get_gif("ball")
                sprite = shared.get_plain_sprite("fsh")
                sprite.rect.center = event.pos
                sprite.layer = 1
                level.add(sprite)
                # i = 1 if count[1] else -1
                # pos = shared.screen_size_half + Vector2(8 * count[0] * i, 0)
                # count[0] += 1
                # count[1] = not count[1]

                Sequencer(
                    # GifAnimation(sprite, gif, 125),
                    # LerpPosition(sprite, pos),
                    PlaySound("chime_bell"),
                    TickWait(50),
                    Sequencer(
                        LerpPosition(sprite, self, True),
                        LerpRotation(sprite, self, True),
                        DestroySpritePosition(sprite, self),
                    ).on_end(
                        PlaySound("chime_bell")
                    ).build(True, True),
                ).build(True).start()

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
            self.rect.center = event.pos

        add_binding(pygame.MOUSEMOTION, self, mv)
