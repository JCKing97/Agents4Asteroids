from abc import ABC, abstractmethod

from game.control import Game


class Perception(ABC):
    """
    A base class to describe a perception of the game at a certain point in it's running.
    """

    @abstractmethod
    def __init__(self, game: Game=None):
        """
        Record the perception data from the game.

        :param game: The game to record the perception data from.
        :type game: Game
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

    def __init__(self, game: Game):
        """
        Record the state of the ship, asteroid and particle at time of creation in a dictionary.

        :param game: The game to record the perception data from.
        :type game: Game
        """
        self.ship_state = {'centre_x': game.ship.centre_x, 'centre_y': game.ship.centre_y,
                           'velocity_x': game.ship.velocity_x, 'velocity_y': game.ship.velocity_y,
                           'facing': game.ship.facing, 'thrust': game.ship.thrust,
                           'turn_speed': game.ship.turn_speed, 'height': game.ship.height}
        self.asteroid_data = [{'centre_x': asteroid.centre_x, 'centre_y': asteroid.centre_y,
                               'velocity_x': asteroid.velocity_x, 'velocity_y': asteroid.velocity_y,
                               'radius': asteroid.radius} for asteroid in game.asteroids]
        self.particle_data = [{'centre_x': particle.centre_x, 'centre_y': particle.centre_y,
                               'velocity_x': particle.velocity_x, 'velocity_y': particle.velocity_y}
                              for particle in game.particles]
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
