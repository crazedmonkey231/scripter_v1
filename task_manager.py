import math
import pygame
from pygame import Vector2, Surface
from pygame.sprite import Sprite
import shared
from typing import Callable, Sequence
from level import level
import util


class Task(object):
    end = 0
    cont = 1
    wait = 2

    def __init__(self, task_func, name: str = "", params=([], {})):
        self.name: str = name if name else f"{self}-{util.generate_simple_id()}"
        self.task_func: Callable[[Task, list, dict], int] = task_func
        self.args: list = params[0]
        self.kwargs: dict = params[1]

    def execute(self):
        return self.task_func(self, *self.args, **self.kwargs)

    def start(self):
        task_manager.tasks[self.name] = self

    def done(self):
        if self.name in task_manager.tasks:
            del task_manager.tasks[self.name]


class LerpPosition(Task):
    def __init__(self, sprite: Sprite, target: Sprite | Vector2, looping: bool = False, move_speed: float = 300,
                 name: str = "", params=([], {})):
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

        super().__init__(update, name, params)


class LerpRotation(Task):
    def __init__(self, sprite: Sprite, target: Sprite | Vector2, looping: bool = False, rotation_speed: float = 10,
                 rotation_lag=1, name: str = "", params=([], {})):

        if hasattr(sprite, "original_image"):
            original_image = sprite.original_image.copy()
        else:
            original_image = sprite.image.copy()

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
                sprite.image, sprite.rect = util.rotate_image(original_image, angle, center)
                return task.wait
            else:
                if looping:
                    return task.cont
                return task.end

        super().__init__(update, name, params)


class DestroySprite(Task):
    def __init__(self, sprite: Sprite, name: str = "", params=([], {})):
        def destroy(task):
            if sprite.alive():
                sprite.kill()
            return task.end
        super().__init__(destroy, name, params)


class DestroySpritePosition(Task):
    def __init__(self, sprite: Sprite, target: Sprite | Vector2, threshold: float = 0.5, name: str = "",
                 params=([], {})):
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
                    sprite.kill()
                return task.end
            return task.cont
        super().__init__(destroy, name, params)


class CountTask(Task):
    def __init__(self, task_func, name: str = "", params=([], {})):
        self.counter = 0
        super().__init__(task_func, name, params)


class DelayTask(CountTask):
    def __init__(self, task_func, name: str = "", params=([], {})):
        super().__init__(task_func, name, params)


class TickWait(DelayTask):
    def __init__(self, ticks: int, name: str = "", params=([], {})):
        def tick(task):
            self.counter += 1
            if self.counter == ticks:
                self.counter = 0
                return task.cont
            return task.wait
        super().__init__(tick, name, params)


class TimeWait(DelayTask):
    def __init__(self, time: float, name: str = "", params=([], {})):
        def update(task):
            self.counter += shared.delta_time
            if time <= self.counter:
                self.counter = 0
                return task.cont
            return task.wait
        super().__init__(update, name, params)


class LerpLineTask(CountTask):
    def __init__(self, sprite: Sprite, line: list[Vector2], move_speed: float = 300, looping: bool = False,
                 name: str = "", params=([], {})):
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
        super().__init__(update, name, params)


class LerpPositionLine(LerpLineTask):
    def __init__(self, sprite: Sprite, start: Vector2, destination: Vector2, move_speed: float = 300,
                 looping: bool = False, name: str = "", params=([], {})):
        line = util.generate_line(start, destination)
        super().__init__(sprite, line, move_speed, looping, name, params)


class LerpPositionArch(LerpLineTask):
    def __init__(self, sprite: Sprite, start: Vector2, destination: Vector2, move_speed: float = 300,
                 looping: bool = False, max_arch_height: float = 100, max_arch_delta: float = 10, inverse: bool = False,
                 name: str = "", params=([], {})):
        line = util.generate_arch(start, destination, max_arch_height, max_arch_delta, inverse)
        super().__init__(sprite, line, move_speed, looping, name, params)


class LerpPositionCircle(LerpLineTask):
    def __init__(self, sprite: Sprite, center: Vector2, move_speed: float = 300, looping: bool = False,
                 radius: float = 100, name: str = "", params=([], {})):
        line = util.generate_circle(center, radius)
        super().__init__(sprite, line, move_speed, looping, name, params)


class Transition(CountTask):
    def __init__(self, image: str | Surface = "intro", center=Vector2(shared.screen_size_half), time=3, name: str = "",
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

        super().__init__(update, name, params)
        self.counter = time
        self.timer_reset = self.counter
        self.timer_h = self.counter / 2


class Sequencer(object):
    def __init__(self, *task_list):
        self.task_list: list[Task] = list(task_list)
        self.current_idx: int = 0

    def build(self, looping: bool = False, parallel: bool = False, name: str = "", params=([], {})):
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
                return task.end

        name = name if name else f"{self}-{util.generate_simple_id()}"
        return Task(sequence, name, params)


class TaskManager(object):
    def __init__(self):
        self.tasks: dict[str, Task] = {}

    def run_task_manager(self):
        for name, task in list(self.tasks.items()):
            if task is None:
                del self.tasks[name]
            else:
                return_code = task.execute()
                if return_code == Task.end:
                    task.done()


task_manager: TaskManager = TaskManager()
