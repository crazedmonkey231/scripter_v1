import math
import pygame
from pygame import Vector2, Surface
from pygame.sprite import Sprite
import shared
from typing import Callable
from level import level
import util

TT_TASK = 0
TT_DRAW = 1
TT_OVERLAY = 2
TT_SCREEN = 3


class Task(object):
    end = 0
    cont = 1
    wait = 2

    def __init__(self, task_func, params=([], {})):
        self.task_func: Callable[[Task, list, dict], int] = task_func
        self.args: list = params[0]
        self.kwargs: dict = params[1]

    def execute(self):
        return self.task_func(self, *self.args, **self.kwargs)

    def start(self, task_type=TT_TASK):
        _tasks[task_type].append(self)

    def bind(self, binding: int):
        if binding not in _bindings:
            _bindings[binding] = []
        _bindings[binding].append(self)


class CameraUpdate(Task):
    def __init__(self, params=([], {})):
        def update(task):
            if shared.camera_target is None:
                return task.end
            camera_center = shared.camera_topleft + shared.screen_size_half
            dv = shared.camera_target - camera_center
            if dv.length() > 1:
                camera_center += dv.normalize() * (dv.length() * 1 / shared.camera_lag) * shared.delta_time
            shared.camera_topleft = camera_center - shared.screen_size_half
            shared.screen_rect.topleft = shared.camera_topleft
            shared.screen_rect.size = shared.screen_size
            return task.cont

        super().__init__(update, params)


class CameraFollow(Task):
    def __init__(self, sprite: Sprite, camera_lag=0.01, params=([], {})):
        old_lag = shared.camera_lag
        shared.camera_lag = camera_lag

        def update(task):
            if not sprite.alive():
                shared.camera_lag = old_lag
                return task.end
            shared.camera_target = sprite.rect.center
            return task.cont

        super().__init__(update, params)


class LerpPosition(Task):
    def __init__(self, sprite: Sprite, target: Sprite | Vector2, looping: bool = False,
                 move_speed: float = 300, params=([], {})):
        def update(task):
            if not sprite.alive():
                return task.end
            if isinstance(target, Sprite):
                if not target.alive():
                    return task.end
                target_pos = Vector2(target.rect.center)
            elif isinstance(target, Vector2):
                target_pos = target
            else:
                return task.end
            center = Vector2(sprite.rect.center)
            direction = target_pos - center

            if direction.length() < 0.5:
                sprite.rect.center = center
                if looping:
                    return task.cont
                return task.end
            else:
                dvn = direction.normalize()

            dx = dvn * move_speed * shared.delta_time
            dy = dvn * move_speed * shared.delta_time
            dv = Vector2(dx, dy)
            sprite.rect.center = center + dv
            return task.wait

        super().__init__(update, params)


class LerpRotation(Task):
    def __init__(self, sprite: Sprite, target: Sprite | Vector2, looping: bool = False,
                 rotation_speed: float = 10, rotation_lag=1, params=([], {})):

        if not hasattr(sprite, "original_image"):
            sprite.original_image = sprite.image.copy()

        if not hasattr(sprite, "angle"):
            sprite.angle = 0

        def update(task):
            if not sprite.alive():
                return task.end
            if isinstance(target, Sprite):
                if not target.alive():
                    return task.end
                target_pos = Vector2(target.rect.center)
            elif isinstance(target, Vector2):
                target_pos = target
            else:
                return task.end
            center = Vector2(sprite.rect.center)
            direction = target_pos - center
            target_angle = math.degrees(math.atan2(-direction.y, direction.x))
            if not util.angles_equal(target_angle, sprite.angle, 0.5):
                angle = util.lerp_angle(sprite.angle, target_angle, rotation_speed * shared.delta_time, rotation_lag)
                sprite.angle = angle
                sprite.image, sprite.rect = util.rotate_image(sprite.original_image, angle, center)
                return task.wait
            else:
                if looping:
                    return task.cont
                return task.end

        super().__init__(update, params)


class SimpleRotate(Task):
    def __init__(self, sprite: Sprite, rotation_speed=100, params=([], {})):

        if not hasattr(sprite, "original_image"):
            sprite.original_image = sprite.image.copy()

        if not hasattr(sprite, "angle"):
            sprite.angle = 0

        def update(task):
            if not sprite.alive():
                return task.end
            sprite.angle += rotation_speed * shared.delta_time
            sprite.angle %= 360
            sprite.image, sprite.rect = util.rotate_image(sprite.original_image, sprite.angle, sprite.rect.center)
            return task.cont

        super().__init__(update, params)


class SimpleFloat(Task):
    def __init__(self, sprite: Sprite, cos_amp=25, cos_speed=0.01, sin_amp=25, sin_speed=0.01, params=([], {})):

        start_pos = Vector2(sprite.rect.center)

        def update(task):
            if not sprite.alive():
                return task.end
            dx = util.float_movement_cos(cos_amp, cos_speed)
            dy = util.float_movement_sin(sin_amp, sin_speed)
            sprite.rect.center = start_pos + Vector2(dx, dy)
            return task.cont

        super().__init__(update, params)


class DestroySprite(Task):
    def __init__(self, sprite: Sprite, params=([], {})):
        def destroy(task):
            if sprite.alive():
                sprite.visible = 0
                sprite.kill()
            return task.end
        super().__init__(destroy, params)


class DestroySpritePosition(Task):
    def __init__(self, sprite: Sprite, target: Sprite | Vector2, threshold: float = 0.5, params=([], {})):
        def destroy(task):
            if not sprite.alive():
                return task.end
            if isinstance(target, Sprite):
                if not target.alive():
                    return task.end
                target_pos = Vector2(target.rect.center)
            elif isinstance(target, Vector2):
                target_pos = target
            else:
                return task.end
            center = Vector2(sprite.rect.center)
            direction = target_pos - center
            if direction.length() < threshold:
                if sprite.alive():
                    sprite.visible = 0
                    sprite.kill()
                return task.end
            return task.cont
        super().__init__(destroy, params)


class CountTask(Task):
    def __init__(self, task_func, params=([], {})):
        self.counter = 0
        super().__init__(task_func, params)


class DelayTask(CountTask):
    def __init__(self, task_func, params=([], {})):
        super().__init__(task_func, params)


class TickWait(DelayTask):
    def __init__(self, ticks: int, params=([], {})):
        def tick(task):
            self.counter += 1
            if self.counter == ticks:
                self.counter = 0
                return task.cont
            return task.wait
        super().__init__(tick, params)


class TimeWait(DelayTask):
    def __init__(self, time: float, params=([], {})):
        def update(task):
            self.counter += shared.delta_time
            if time <= self.counter:
                self.counter = 0
                return task.cont
            return task.wait
        super().__init__(update, params)


class PlaySound(CountTask):
    def __init__(self, sound_name: str, looping: bool = False, params=([], {})):
        s_data = [True, shared.get_sound(sound_name)]

        def play_sound(task):
            if s_data[0]:
                shared.play_sound(s_data[1])
                self.counter = s_data[1].get_length()
                s_data[0] = False
                return task.cont
            else:
                if looping:
                    self.counter -= shared.delta_time
                    if self.counter < 0:
                        self.counter = 0
                        s_data[0] = True
                    return task.wait
                return task.end
        super().__init__(play_sound, params)


class GifAnimation(CountTask):
    def __init__(self, sprite: Sprite, gif: str | list[Surface], gif_speed: float = 1, looping: bool = True,
                 params=([], {})):
        g = None
        if isinstance(gif, str):
            g = shared.get_gif(gif)
        elif isinstance(gif, list) and util.is_all_of_type(gif, Surface):
            g = gif

        def update(task):
            if not sprite.alive() or g is None:
                return task.end
            if gif_speed < 0 and self.counter == 0:
                self.counter = len(g)
            self.counter += gif_speed * shared.delta_time
            if 0 <= self.counter < len(g):
                sprite.original_image = g[int(self.counter)]
                sprite.image = sprite.original_image
                sprite.rect = sprite.image.get_rect(center=sprite.rect.center)
                return task.cont
            else:
                if not looping:
                    return task.end
                self.counter %= len(g)
                return task.cont
        super().__init__(update, params)


class CircleFollow(CountTask):
    def __init__(self, sprite: Sprite, target_sprite: Sprite, radius: float = 100, move_speed: float = 300,
                 clockwise=True, step_size: int = 10, looping: bool = False, params=([], {})):
        move_speed = abs(move_speed)
        i = 1 if clockwise else -1
        sprite.rect.center = Vector2(target_sprite.rect.center[0] + math.cos(0) * radius,
                                     target_sprite.rect.center[1] + math.sin(0) * radius)

        def update(task):
            if not sprite.alive() or not target_sprite.alive():
                return task.end
            center = Vector2(target_sprite.rect.center)
            self.counter += move_speed * shared.delta_time
            if self.counter < 360:
                r_angle = math.radians(self.counter * i) * step_size
                x = center.x + math.cos(r_angle) * radius
                y = center.y + math.sin(r_angle) * radius
                sprite.rect.center = Vector2(x, y)
            else:
                if looping:
                    self.counter %= 360
                    return task.wait
                return task.end
            return task.cont
        super().__init__(update, params)


class LerpLineTask(CountTask):
    def __init__(self, sprite: Sprite, line: list[Vector2], move_speed: float = 300, looping: bool = False,
                 params=([], {})):
        def update(task):
            if not sprite.alive():
                return task.end
            if move_speed < 0 and self.counter == 0:
                self.counter = len(line)
            self.counter += move_speed * shared.delta_time
            if 0 <= self.counter < len(line):
                sprite.rect.center = line[int(self.counter)]
                return task.wait
            else:
                if not looping:
                    return task.end
                self.counter %= len(line)
                return task.cont
        super().__init__(update, params)


class LerpPositionLine(LerpLineTask):
    def __init__(self, sprite: Sprite, start: Vector2, destination: Vector2, move_speed: float = 300,
                 looping: bool = False, params=([], {})):
        line = util.generate_line(start, destination)
        super().__init__(sprite, line, move_speed, looping, params)


class LerpPositionArch(LerpLineTask):
    def __init__(self, sprite: Sprite, start: Vector2, destination: Vector2, move_speed: float = 300,
                 looping: bool = False, max_arch_height: float = 100, max_arch_delta: float = 10, inverse: bool = False,
                 params=([], {})):
        line = util.generate_arch(start, destination, max_arch_height, max_arch_delta, inverse)
        super().__init__(sprite, line, move_speed, looping, params)


class LerpPositionCircle(LerpLineTask):
    def __init__(self, sprite: Sprite, center: Vector2, radius: float = 100, move_speed: float = 300,
                 clockwise=True, looping: bool = False, params=([], {})):
        line = util.generate_circle(center, radius, clockwise)
        super().__init__(sprite, line, move_speed, looping, params)


class ScrollingText(CountTask):
    def __init__(self, sprite: Sprite, text: str, speed=100, text_task: Task = None, params=([], {}), **kwargs):
        gif = [0, []]

        t = ""
        for c in text:
            t += c
            s, r = util.make_simple_text(**{"text": t, **kwargs})
            r.center = sprite.rect.center
            gif[1].append((s, r))

        def update(task):
            if not sprite.alive():
                return task.end
            if gif[0] < len(gif[1]):
                sprite.image = gif[1][gif[0]][0]
                sprite.rect = gif[1][gif[0]][1]
                self.counter += speed * shared.delta_time
                if 1 < self.counter:
                    self.counter = 0
                    gif[0] += 1
                    if text_task:
                        text_task.execute()
                return task.wait
            return task.cont

        super().__init__(update, params)


class ImageTransition(CountTask):
    def __init__(self, image: str | Surface = "intro", center=Vector2(shared.screen_size_half), time=3,
                 params=([], {})):
        surf = pygame.Surface(shared.screen_size).convert_alpha()
        surf.fill((0, 0, 0, 255))
        if isinstance(image, str) or image is None:
            img = shared.get_image(image)
            surf.blit(img[0], center - Vector2(img[1].size) / 2)
        elif isinstance(image, Surface):
            surf.blit(image, center - Vector2(image.get_rect().size) / 2)

        def update(task):
            if 0 < self.counter:
                self.counter -= shared.delta_time
                i = surf.copy()
                if self.counter > self.timer_h:
                    a = util.map_range_clamped(self.counter, self.timer_h, self.timer_reset, 0, 255)
                    i.fill((0, 0, 0, a))
                else:
                    i.fill((0, 0, 0, util.map_range_clamped(self.counter, self.timer_h, 0, 0, 255)))
                j = surf.copy()
                j.blit(i, (0, 0))
                level.background = j
                return task.wait
            elif self.counter < 0:
                self.counter = 0
                return task.cont

        super().__init__(update, params)
        self.counter = time
        self.timer_reset = self.counter
        self.timer_h = self.counter / 2


class FadeTransition(CountTask):
    def __init__(self, color=(255, 255, 255), fade_in=1, fade_out=2, total_time=3, params=([], {})):
        surf = pygame.Surface(shared.screen_size).convert_alpha()
        surf.fill((0, 0, 0, 0))

        def update(task):
            if total_time < self.counter:
                return task.end
            self.counter += shared.delta_time
            i = surf.copy()
            if self.counter < fade_in:
                a = util.map_range_clamped(self.counter, 0, fade_in, 0, 255)
            elif fade_in <= self.counter < fade_out:
                a = 255
            else:
                a = util.map_range_clamped(self.counter, total_time, fade_out, 0, 255)
            i.fill((*color, a))
            shared.screen.blit(i, (0, 0))
            return task.wait

        super().__init__(update, params)


class Sequencer(object):
    def __init__(self, *seq_tasks):
        """Sequencer for game actions"""
        self.task_list: list[Task] = list(seq_tasks)
        self.current_idx: int = 0
        self.end_tasks: list[Task] = None

    def on_end(self, *end_tasks):
        """Single execution end tasks"""
        self.end_tasks = list(end_tasks)
        return self

    def build(self, looping: bool = False, parallel: bool = False, params=([], {})):
        """Build the sequencer into a Task"""
        def sequence(task):
            if self.task_list and not util.is_all_of_type(self.task_list, DelayTask):
                if not parallel:
                    if self.current_idx == -1:
                        self.current_idx = 0
                    elif len(self.task_list) <= self.current_idx:
                        if not looping:
                            return Task.end
                        self.current_idx = 0
                    return_code = self.task_list[self.current_idx].execute()
                    if return_code == Task.cont:
                        self.current_idx += 1
                    elif return_code == Task.end:
                        del self.task_list[self.current_idx]
                        self.current_idx -= 1
                    return task.cont
                else:
                    for i, task in enumerate(self.task_list):
                        return_code = task.execute()
                        if return_code == Task.end:
                            del self.task_list[i]
                    if not looping:
                        return task.end
                    return task.wait
            else:
                if self.end_tasks:
                    for task in self.end_tasks:
                        task.execute()
                    self.end_tasks = None
                self.task_list = None
                return task.end

        return Task(sequence, params)


_bindings: dict[int, list[Task]] = {}
_tasks: dict[int, list[Task]] = {
    TT_TASK: [],
    TT_DRAW: [],
    TT_OVERLAY: [],
    TT_SCREEN: []
}


def exec_binding(event):
    for i, task in enumerate(_bindings.get(event.type, [])):
        return_code = task.execute()
        if return_code == Task.end:
            del _bindings[event.type][i]


def exec_tasks(task_type=TT_TASK):
    for i, task in enumerate(_tasks[task_type]):
        return_code = task.execute()
        if return_code == Task.end:
            del _tasks[task_type][i]
