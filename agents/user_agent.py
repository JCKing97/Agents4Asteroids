from typing import List, Type

from pyglet.window import key

from game.agent import Agent, Action
from game.perception import Perception, NoPerception
from game.entities import Ship


class UserAgent(Agent):
    """
    An agent that is an actual user.
    """

    def __init__(self, ship: Ship, window):
        super().__init__(ship)
        self.actions = []

    @staticmethod
    def get_perception_type() -> Type[Perception]:
        return NoPerception

    def perceive(self, perception: NoPerception):
        pass

    def decide(self) -> List[Action]:
        actions = self.actions
        self.actions = []
        return actions

    def add_action(self, action: Action):
        self.actions.append(action)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.W:
            self.add_action(Action.BOOST)
        elif symbol == key.D:
            self.add_action(Action.TURNRIGHT)
        elif symbol == key.A:
            self.add_action(Action.TURNLEFT)
        elif symbol == key.SPACE:
            self.add_action(Action.FIRE)

    def on_key_release(self, symbol, modifiers):
        if symbol == key.A or symbol == key.D:
            self.add_action(Action.STOPTURN)
        if symbol == key.W:
            self.add_action(Action.STOPBOOST)
