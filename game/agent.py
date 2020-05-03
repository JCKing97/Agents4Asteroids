from enum import Enum
from game.perception import Perception, NoPerception
from game.entities import Ship
from abc import ABC, abstractmethod
from typing import Type
from math import cos, sin
import pyglet
from game.physics import line


class Action(Enum):
    """ The actions available to an agent at each point in a game """
    BOOST = 1
    STOPBOOST = 2
    TURNRIGHT = 3
    TURNLEFT = 4
    STOPTURN = 5
    FIRE = 6
    NOACTION = 7


class Agent(ABC):
    """
    An interface for agent that is capable of perceiving it's environment,
     storing details of the environment and making decisions of how to act upon that knowledge.
    The actions committed to by the agent are it's way of interacting with the environment.
    """

    def __init__(self, ship: Ship):
        """
        Initialise the agents knowledge and associate it with a ship.
        """
        self.ship = ship

    def perceive(self, perception: Perception):
        """
        Receive a perception of the state of the game and it's entities

        :param perception: The perception received
        :return: None
        """
        pass

    def draw(self):
        """
        Draw the agent
        """
        self.ship.draw()

    @abstractmethod
    def decide(self) -> Action:
        """
        Decide an action to take at this point in time.

        :return: The action to take.
        """
        raise NotImplementedError

    @staticmethod
    def get_perception_type() -> Type[Perception]:
        """
        Return the type of perception that this agent can handle.

        :return: The type of perception this agent can handle.
        """
        return NoPerception

    def get_ship(self) -> Ship:
        """
        :return: The ship the agent is controlling.
        """
        return self.ship

    def on_key_press(self, symbol, modifiers):
        """
        Handle key press.

        :param symbol: The key pressed.
        :param modifiers: ?
        """
        pass

    def on_key_release(self, symbol, modifiers):
        """
        Handle key press.

        :param symbol: The key pressed.
        :param modifiers: ?
        """
        pass
