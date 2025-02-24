from collections import defaultdict
from typing import Callable
from pygame.sprite import Sprite
import util


class BindingManager(object):
    def __init__(self):
        self.bindings: defaultdict[int, defaultdict[Sprite, Callable]] = util.tree()


binding_manager: BindingManager = BindingManager()


def add_binding(binding: int, obj: Sprite, callback: Callable):
    if obj is not None and callback is not None:
        binding_manager.bindings[binding][obj] = callback


def remove_binding(binding: int, obj: Sprite):
    if binding in binding_manager.bindings and obj is not None and obj in binding_manager.bindings[binding]:
        del binding_manager.bindings[binding][obj]


def do_bindings(event):
    filtered_data = {k: v for k, v in binding_manager.bindings.get(event.type, {}).items()
                     if k.alive() and v is not None}
    binding_manager.bindings[event.type] = filtered_data
    for k, v in list(filtered_data.items()):
        v(event)
