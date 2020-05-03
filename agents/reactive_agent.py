from typing import Type, List
import math

from game.agent import Agent, Action
from game.perception import Perception, VectorPerception
from game.entities import Ship
from game.physics import dist, line_point, is_left
import pyglet


class ReactiveAgent(Agent):
    """
    A simple reactive agent that looks for the closest asteroid, aims and shoots.
    """

    def __init__(self, ship: Ship):
        """
        Initialise the agents knowledge.
        """
        self.closest_asteroid: List[int, int] = [0, 0]
        self.asteroid_radius = 0
        super().__init__(ship)

    def perceive(self, perception: VectorPerception):
        shortest_dist = math.inf
        for asteroid in perception.asteroid_data:
            asteroid_dist = dist(
                [asteroid["centre_x"], asteroid["centre_y"]],
                [self.ship.centre_x, self.ship.centre_y]
            )
            if asteroid_dist < shortest_dist:
                shortest_dist = asteroid_dist
                self.closest_asteroid = [asteroid["centre_x"], asteroid["centre_y"]]
                self.asteroid_radius = asteroid["radius"]

    def decide(self) -> Action:
        point_x = int(self.ship.centre_x + (2 * self.ship.height * math.cos(self.ship.facing)))
        point_y = int(self.ship.centre_y + (2 * self.ship.height * math.sin(self.ship.facing)))
        line_vector_facing = line_point([point_x, point_y], [self.ship.centre_x, self.ship.centre_y], 100)
        line_vector_behind = line_point([point_x, point_y], [self.ship.centre_x, self.ship.centre_y], -100)
        dist_from_ship_to_asteroid_to_point_facing = dist([point_x, point_y], self.closest_asteroid) + \
                                                     dist(line_vector_facing, self.closest_asteroid)
        dist_from_ship_to_point_facing = dist([point_x, point_y], line_vector_facing)
        if dist_from_ship_to_point_facing - self.asteroid_radius <= dist_from_ship_to_asteroid_to_point_facing <= \
                dist_from_ship_to_point_facing + self.asteroid_radius:
            return Action.FIRE
        if is_left(line_vector_behind, line_vector_facing, self.closest_asteroid):
            return Action.TURNLEFT
        else:
            return Action.TURNRIGHT

    @staticmethod
    def get_perception_type() -> Type[Perception]:
        return VectorPerception
