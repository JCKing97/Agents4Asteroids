import math

from game.physics import line_point, dist, is_left
from game.control import Action


def attack_nearest_asteroid(ship, closest_asteroid, asteroid_radius) -> Action:
    point_x = int(ship.centre_x + (2 * ship.height * math.cos(ship.facing)))
    point_y = int(ship.centre_y + (2 * ship.height * math.sin(ship.facing)))
    line_vector_facing = line_point([point_x, point_y], [ship.centre_x, ship.centre_y], 100)
    line_vector_behind = line_point([point_x, point_y], [ship.centre_x, ship.centre_y], -100)
    dist_from_ship_to_asteroid_to_point_facing = dist([point_x, point_y], closest_asteroid) + \
                                                 dist(line_vector_facing, closest_asteroid)
    dist_from_ship_to_point_facing = dist([point_x, point_y], line_vector_facing)
    if dist_from_ship_to_point_facing - asteroid_radius <= dist_from_ship_to_asteroid_to_point_facing <= \
            dist_from_ship_to_point_facing + asteroid_radius:
        return Action.FIRE
    if is_left(line_vector_behind, line_vector_facing, closest_asteroid):
        return Action.TURNLEFT
    else:
        return Action.TURNRIGHT

