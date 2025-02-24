# /// script
# dependencies = [
#  "pygame-ce",
#  "cffi",
#  "pymunk",
#  "numpy",
#  "PIL",
# ]
# ///

import asyncio
import pygame
import numpy
import PIL

import util
from binding_manager import do_bindings
import game
from level import level
import shared
from task_manager import task_manager, Task, Sequencer, TimeWait, Transition


if shared.debug:
    util.log([numpy, PIL])

Sequencer(
    TimeWait(.25),
    Transition(time=1),
    TimeWait(0.25),
    Task(game.run_game)
).build(False, False, "loader").start()


async def main():
    while shared.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                shared.running = False
            do_bindings(event)
        if not shared.paused:
            shared.screen.fill("dark gray")
            if level.background is not None:
                shared.canvas.blit(level.background, shared.screen_rect, shared.screen_rect)
            else:
                shared.canvas.fill("black", shared.screen_rect)
            task_manager.run_task_manager()
            level.update()
            level.draw(shared.canvas)
            shared.screen.blit(shared.canvas, (0, 0), shared.screen_rect)
        pygame.display.flip()
        shared.delta_time = shared.clock.tick(shared.fps) / shared.delta_slowdown
        pygame.display.set_caption(f"Fps: {int(shared.clock.get_fps())}")
        await asyncio.sleep(0)
    pygame.quit()
asyncio.run(main())

