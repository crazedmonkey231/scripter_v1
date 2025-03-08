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
import numpy
import PIL

import game
from task_manager import *

""" Debug print numpy/pil """
if shared.debug:
    util.log([numpy, PIL])

""" Startup sequence """
Sequencer(
    TimeWait(0.25),
    ImageTransition(time=0.1),
    TimeWait(0.25),
    Task(game.run_game)
).build(False, False).start()

""" Level update """
Task(level.update).start()


async def main():
    """ Main loop """
    while shared.running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                shared.running = False
                break
            exec_binding(event)
        if not shared.paused:
            shared.screen.fill("gray")
            exec_tasks(TT_TASK)
            level.draw_bg(shared.canvas)
            exec_tasks(TT_DRAW)
            level.draw(shared.canvas)
            exec_tasks(TT_OVERLAY)
            shared.screen.blit(shared.canvas, (0, 0), shared.screen_rect)
            exec_tasks(TT_SCREEN)
        pygame.display.flip()
        shared.delta_time = shared.clock.tick(shared.fps) / shared.delta_slowdown
        pygame.display.set_caption(f"Fps: {int(shared.clock.get_fps())}")
        await asyncio.sleep(0)
    pygame.quit()
asyncio.run(main())

