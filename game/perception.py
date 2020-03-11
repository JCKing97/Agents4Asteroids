from abc import ABC, abstractmethod
from typing import List

from game.entities import Ship, Particle, Asteroid


class Perception(ABC):
    """
    A base class to describe a perception of the game at a certain point in it's running.
    """

    @abstractmethod
    def __init__(self, ship: Ship=None, particles: List[Particle]=None, asteroids: List[Asteroid]=None,
                 other_ships: List[Ship]=None):
        """
        Initialise relevant data.

        :param ship: The ship this perception is from.
        :param particles: The particles in the game.
        :param asteroids: The asteroids in the game.
        :param other_ships: The other ships in the game.
        """
        pass

    @abstractmethod
    def get_perception_data(self):
        """
        Get the data from the perception.

        :return: The perception data
        """
        raise NotImplementedError


class VectorPerception(Perception):
    """
    A perception of the the state of the ship, asteroids and particles in the game at one point.
    Representation of velocities, position etc. are given as vectors.
    """

    def __init__(self, ship: Ship, particles: List[Particle], asteroids: List[Asteroid], other_ships: List[Ship]):
        """
        Record the state of the ship, asteroid and particle at time of creation in a dictionary.

        :param ship: The ship this perception is from.
        :param particles: The particles in the game.
        :param asteroids: The asteroids in the game.
        :param other_ships: The other ships in the game.
        """
        self.ship_state = {'centre_x': ship.centre_x, 'centre_y': ship.centre_y,
                           'velocity_x': ship.velocity_x, 'velocity_y': ship.velocity_y,
                           'facing': ship.facing, 'thrust': ship.thrust,
                           'turn_speed': ship.turn_speed, 'height': ship.height}
        self.asteroid_data = [{'centre_x': asteroid.centre_x, 'centre_y': asteroid.centre_y,
                               'velocity_x': asteroid.velocity_x, 'velocity_y': asteroid.velocity_y,
                               'radius': asteroid.radius} for asteroid in asteroids]
        self.particle_data = [{'centre_x': particle.centre_x, 'centre_y': particle.centre_y,
                               'velocity_x': particle.velocity_x, 'velocity_y': particle.velocity_y}
                              for particle in particles]
        super().__init__()

    def get_perception_data(self):
        """
        Return the perception data that was recorded at the time of this perceptions initialisation.

        :return: 3 dictionaries: ship state, asteroid data and particle data
           Example:
                {'centre_x': 20, 'centre_y': 30, 'velocity_x': 1, 'velocity_y': -2,
                'facing': 30, 'thrust': 2, 'turn_speed': 0.4, 'height': 1},
                [
                    {'centre_x': 20, 'centre_y': 30, 'velocity_x': 10, 'velocity_y': -3, 'radius': 4},
                    {'centre_x': 6, 'centre_y': 90, 'velocity_x': 3, 'velocity_y': 3, 'radius': 4},
                    {'centre_x': 50, 'centre_y': 50, 'velocity_x': 9, 'velocity_y': 1, 'radius': 4}
                ],
                [
                    {'centre_x': 1, 'centre_y': 2, 'velocity_x': 90, 'velocity_y': 12},
                    {'centre_x': 9, 'centre_y': 18, 'velocity_x': 7, 'velocity_y': -40},
                    {'centre_x': 35, 'centre_y': 82, 'velocity_x': 19, 'velocity_y': -1}
                ]
        """
        return self.ship_state, self.asteroid_data, self.particle_data


class NoPerception(Perception):

    def __init__(self, ship: Ship, particles: List[Particle], asteroids: List[Asteroid], other_ships: List[Ship]):
        """
        Initialise nothing.

        :param ship: The ship this perception is from.
        :param particles: The particles in the game.
        :param asteroids: The asteroids in the game.
        :param other_ships: The other ships in the game.
        """
        super().__init__()

    def get_perception_data(self):
        """
        Give no percepts.

        :return: None
        """
        pass
