from typing import List, Type
from game.agent import Agent
import os
from importlib import import_module
import inspect


def load_agents() -> List[Type[Agent]]:
    """
    :return: all available agent types currently in the system.
    """
    agents: List[Type[Agent]] = []
    agent_dir = os.path.dirname(os.path.abspath(__file__))
    for filename in os.listdir(agent_dir):
        filename = str(filename)
        if filename.endswith(".py"):
            module = import_module("agents." + filename.split('.')[0])
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, Agent) and obj is not Agent:
                    agents.append(obj)
    return agents
