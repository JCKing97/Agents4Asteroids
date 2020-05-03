from typing import Type, Tuple
import math
import pyglet

from game.agent import Agent, Action
from game.perception import Perception, VectorPerception
from game.entities import Ship
from game.physics import dist, line


class ReactiveAgent(Agent):
    """
    A simple reactive agent that looks for the closest asteroid, aims and shoots.
    """

    def __init__(self, ship: Ship):
        """
        Initialise the agents knowledge.
        """
        self.closest_asteroid: Tuple[int, int] = (0, 0)
        super().__init__(ship)

    def perceive(self, perception: VectorPerception):
        shortest_dist = math.inf
        for asteroid in perception.asteroid_data:
            asteroid_dist = dist([asteroid["centre_x"], asteroid["centre_y"]], [self.ship.centre_x, self.ship.centre_y])
            if asteroid_dist < shortest_dist:
                shortest_dist = asteroid_dist
                self.closest_asteroid = (asteroid["centre_x"], asteroid["centre_y"])

    def decide(self) -> Action:
        point_x = int(self.ship.centre_x + (2 * self.ship.height * math.cos(self.ship.facing)))
        point_y = int(self.ship.centre_y + (2 * self.ship.height * math.sin(self.ship.facing)))
        line_points = line([point_x, point_y], [self.ship.centre_x, self.ship.centre_y], 100)
        if dist(line_points[0], self.closest_asteroid) + dist(line_points[1], self.closest_asteroid) == \
            dist(line_points[0], line_points[1]):
            return Action.FIRE
        return Action.TURNRIGHT

    @staticmethod
    def get_perception_type() -> Type[Perception]:
        return VectorPerception
