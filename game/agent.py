from enum import Enum
from game.perception import Perception
from game.entities import Ship
from abc import ABC, abstractmethod
from typing import List


class Action(Enum):
    """ The actions available to an agent at each point in a game """
    BOOST = 1
    STOPBOOST = 2
    TURNRIGHT = 3
    TURNLEFT = 4
    STOPTURN = 5
    FIRE = 6


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

    @abstractmethod
    def perceive(self, perception: Perception):
        """
        Receive a perception of the state of the game and it's entities

        :param perception: The perception received
        :return: None
        """
        raise NotImplementedError

    @abstractmethod
    def decide(self) -> List[Action]:
        """
        Decide an action to take at this point in time.

        :return: The action to take.
        """
        raise NotImplementedError

    def get_ship(self) -> Ship:
        """
        :return: The ship the agent is controlling.
        """
        return self.ship
