from game.agent import Agent, Action
from game.perception import VectorPerception
from game.entities import Ship


class DumbAgent(Agent):
    """
    A simple dumb agent to play the game
    """

    def __init__(self, ship: Ship):
        """
        Initialise the agents knowledge.
        """
        self.last_action = []
        self.points = 0
        super().__init__(ship)

    def perceive(self, perception: VectorPerception):
        """
        Receive a perception of the state of the game and it's entities

        :param perception: The perception received
        :return: None
        """
        self.ship_state, self.asteroid_data, self.particle_data = perception.get_perception_data()

    def receive_reward(self, reward: int) -> None:
        """
        Receive feedback in terms of an integer.

        :param reward: The reward the agent is receiving.
        :return: None
        """
        self.points += reward

    def decide(self):
        action = [Action.TURNRIGHT, Action.FIRE]
        self.last_action = [Action.TURNRIGHT, Action.FIRE]
        return action
