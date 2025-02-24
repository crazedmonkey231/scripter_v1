import collisions
import util

# Definitions for game objects.
# These are auto loaded into the definition registry and can be spawned via their name.
# game_object.spawn_game_object("simple_effect")

simple_effect = {
    "class": "PhysicsBox",
    "layer": 0,
    "image_size": (20, 20),
    "image_color": "yellow",
    "time_alive": 10,
    "mass": 1,
    "density": 200,
    "elasticity": 0.3,
    "friction": 1,
    "dampening": 10,
    "body_type": util.BODY_TYPE_DYNAMIC,
    "collision_type": collisions.CT_DEFAULT,
    "tags": []
}