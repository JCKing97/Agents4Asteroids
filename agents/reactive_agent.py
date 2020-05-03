from typing import Type, Tuple
import math

from game.agent import Agent, Action
from game.perception import Perception, VectorPerception
from game.entities import Ship
from game.physics import dist


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
        return Action.NOACTION


    @staticmethod
    def get_perception_type() -> Type[Perception]:
        return VectorPerception
