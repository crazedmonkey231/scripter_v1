import os
from collections import defaultdict
from typing import AnyStr, LiteralString
from PIL import Image
from PIL.GifImagePlugin import GifImageFile
import pygame
import pymunk
from pygame.mixer import Sound
from pygame import Vector2, Surface, Rect, RLEACCEL, Channel
from pygame.sprite import Sprite
from pymunk import pygame_util
import definitions

main_dir: AnyStr = os.path.split(os.path.abspath(__file__))[0]
image_dir: LiteralString = os.path.join(main_dir, 'assets', 'images')
audio_dir: LiteralString = os.path.join(main_dir, 'assets', 'audio')
gif_dir: LiteralString = os.path.join(main_dir, 'assets', 'gif')

pymunk.pygame_util.positive_y_is_up = True
debug = False
debug_physics = False
volume = 0.5
screen_size = Vector2(640, 480)
screen_size_half = screen_size / 2
canvas_size = Vector2(640, 480)
canvas_size_half = canvas_size / 2
running = True
paused = False
fps = 120
delta_time = 0
delta_slowdown = 1000
camera_lag = 2
space_delta_time = 1 / fps
clock = pygame.time.Clock()

pygame.init()

image_registry: defaultdict[str, tuple[Surface, Rect]] = defaultdict()
sound_registry: defaultdict[str, Sound] = defaultdict()
gif_registry: defaultdict[str, list[Surface]] = defaultdict()
definition_registry: defaultdict[str, dict] = defaultdict()

screen = pygame.display.set_mode(screen_size)
canvas = Surface(canvas_size).convert()
draw_options = pymunk.pygame_util.DrawOptions(canvas)

camera_topleft = Vector2(0, 0)
screen_rect: Rect = Rect(*camera_topleft, *screen_size)
camera_target: Vector2 = Vector2(canvas_size_half)


def set_canvas(surface: Surface):
    global canvas, canvas_size, canvas_size_half
    canvas = surface
    canvas_size = Vector2(surface.get_rect().size)
    canvas_size_half = canvas_size / 2


def local_to_world_pos(pos):
    return Vector2(pos) + camera_topleft


def get_mouse_pos():
    return local_to_world_pos(pygame.mouse.get_pos())


def load_image(img: str | list[str], color_key=None, scale=1):
    n = None
    if isinstance(img, str):
        n = [img]
    elif isinstance(img, list) and all([isinstance(i, str) for i in img]):
        n = img
    if n:
        for name in n:
            name_key = name.split('.')[0]
            img = pygame.image.load(os.path.join(image_dir, name)).convert_alpha()
            size = img.get_size()
            img = pygame.transform.scale(img, (size[0] * scale, size[1] * scale))
            if color_key is not None:
                if color_key == -1:
                    color_key = img.get_at((0, 0))
                img.set_colorkey(color_key, RLEACCEL)
            image_registry[name_key] = (img, img.get_rect())


load_image([i for i in os.listdir(image_dir) if not i.__contains__("__")])


def get_image(i_name: str, **kwargs) -> tuple[Surface, Rect]:
    if i := image_registry.get(i_name, None):
        s, r = i
        return s.copy(), r.copy()
    else:
        s = Surface(kwargs.get("image_size", (64, 64))).convert_alpha()
        s.fill(kwargs.get("image_color", (255, 0, 255, 255)))
        return s, s.get_rect()


def load_sound(sound: str | list[str]):
    s = None
    if isinstance(sound, str):
        s = [sound]
    elif isinstance(sound, list) and all([isinstance(i, str) for i in sound]):
        s = sound
    if s:
        for name in s:
            name_key = name.split('.')[0]
            if not pygame.mixer:
                s = None
            else:
                s = pygame.mixer.Sound(os.path.join(audio_dir, name))
            sound_registry[name_key] = s


load_sound([i for i in os.listdir(audio_dir) if not i.__contains__("__")])


def get_sound(name: str) -> Sound:
    sound = sound_registry.get(name, None)
    if sound:
        sound.fadeout(0)
        sound.set_volume(volume)
    return sound


def play_sound(name: str | Sound) -> Channel:
    if isinstance(name, str):
        sound = get_sound(name)
    elif isinstance(name, Sound):
        sound = name
    else:
        return None
    channel = None
    if sound:
        sound.fadeout(0)
        sound.set_volume(volume)
        channel = sound.play()
    return channel


def load_gif(gif: str | list[str]):
    g = None
    if isinstance(gif, str):
        g = [gif]
    elif isinstance(gif, list) and all([isinstance(i, str) for i in gif]):
        g = gif
    if g:
        for name in g:
            name_key = name.split('.')[0]
            surfaces = []
            loaded_gif: GifImageFile = Image.open(os.path.join(gif_dir, name))
            for frame_index in range(loaded_gif.n_frames):
                loaded_gif.seek(frame_index)
                frame_rgba = loaded_gif.convert("RGBA")
                pygame_image = pygame.image.frombytes(
                    frame_rgba.tobytes(), frame_rgba.size, frame_rgba.mode
                )
                pygame_image.set_colorkey((255, 255, 255, 255))
                surfaces.append(pygame_image)
            gif_registry[name_key] = surfaces


def get_gif(name: str) -> list[Surface]:
    return [surf.copy() for surf in gif_registry.get(name, [])]


load_gif([i for i in os.listdir(gif_dir) if not i.__contains__("__")])


def load_definitions():
    vd = vars(definitions)
    def_list = [(i, vd[i]) for i in vd if "__" not in i and isinstance(vd, dict)]
    for k, v in def_list:
        definition_registry[k] = v


def get_definition(name: str):
    return definition_registry.get(name, None)


load_definitions()


def get_plain_sprite(img: str) -> Sprite:
    sprite: Sprite = Sprite()
    sprite.image, sprite.rect = get_image(img)
    return sprite
