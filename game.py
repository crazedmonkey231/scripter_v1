from task_manager import Task, Sequencer
import cellular_automata

game = cellular_automata


def run_game(task):
    game.start()
    Task(game.run, "game_loop").start()
    return task.end

