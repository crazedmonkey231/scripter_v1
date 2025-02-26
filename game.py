from task_manager import Task

# import cellular_automata as game
import platformer as game


def run_game(task):
    game.init()
    Task(game.game_loop, "game_loop").start()
    return task.end

