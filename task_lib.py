import os
import pygame
from pygame import Surface
import shared
import util
from level import level


def camera_update_task(task):
    if shared.camera_target is not None:
        camera_center = shared.camera_topleft + shared.screen_size_half
        dv = shared.camera_target - camera_center
        if dv.length() > 1:
            camera_center += dv.normalize() * (dv.length() * 1 / shared.camera_lag) * shared.delta_time
        shared.camera_topleft = camera_center - shared.screen_size_half
    shared.screen_rect.topleft = shared.camera_topleft
    shared.screen_rect.size = shared.screen_size
    return task.cont

