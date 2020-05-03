from typing import Type

from game.agent import Agent, Action
from game.perception import Perception, VectorPerception
from game.entities import Ship


class DumbAgent(Agent):
    """
    A simple dumb agent to play the game
    """

    def __init__(self, ship: Ship):
        """
        Initialise the agents knowledge.
        """
        self.actions = [Action.TURNRIGHT, Action.FIRE]
        self.current_action = 0
        super().__init__(ship)

    def decide(self) -> Action:
        self.current_action = (self.current_action + 1) % len(self.actions)
        return self.actions[self.current_action]

    @staticmethod
    def get_perception_type() -> Type[Perception]:
        return VectorPerception
