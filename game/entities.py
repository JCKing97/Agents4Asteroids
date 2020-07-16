import pyglet
import random
from enum import Enum
from math import cos, sin, pi
from abc import ABC, abstractmethod
from time import time


class TurnState(Enum):
    """ Is the ship currently rotating. """
    STATIONARY = 1
    RIGHT = 2
    LEFT = 3


class BoostState(Enum):
    """ Is the ship booster currently on. """
    STATIONARY = 1
    BOOSTING = 2


class Entity(ABC):

    @abstractmethod
    def update(self):
        """
        Update the internals e.g. position, velocity of the entity.
        """
        raise NotImplementedError

    @abstractmethod
    def draw(self):
        """
        Draw the entity on the screen.
        """
        raise NotImplementedError


class Particle(Entity):
    """ Particles which are fired from the particle canon. """

    def __init__(self, centre_x, centre_y, velocity_x, velocity_y):
        self.centre_x = centre_x
        self.centre_y = centre_y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y

    def update(self):
        """ Update the position of the particle. """
        self.centre_x += self.velocity_x
        self.centre_y += self.velocity_y

    def draw(self):
        """ Draw the bullet on the new position. """
        pyglet.graphics.draw(1, pyglet.gl.GL_POINTS, ('v2i', (int(self.centre_x), int(self.centre_y))))


class Ship(Entity):
    """ A ship that is in the game. """

    def __init__(self, centre_x, centre_y, window):
        """
        Initialise the position, velocity, where the ship is facing, size of the ship, thrust,
         turning settings and particle canon.

        :param centre_x: The x coordinate of the center of the ship.
        :param centre_y: The y coordinate of the center of the ship
        """
        self.facing = 0
        self.centre_x = centre_x
        self.centre_y = centre_y
        self.velocity_x = 0
        self.velocity_y = 0
        self.height = 10
        self.turn_speed = 0.1
        self.turn_state = TurnState.STATIONARY
        self.boost_state = BoostState.STATIONARY
        self.thrust = 0
        self.thrust_max = 0.2
        self.thrust_incr = 0.02
        self.particle_canon_speed = 15
        self.window_width = window.width
        self.window_height = window.height
        self.reload_time = 0.25
        self.last_fire_time = time()

    def turn_right(self):
        """ Changes the state of the ship to turn right. """
        self.turn_state = TurnState.RIGHT

    def turn_left(self):
        """ Changes the state of the ship to turn left. """
        self.turn_state = TurnState.LEFT

    def stop_turn(self):
        """ Stop the ship from turning. """
        self.turn_state = TurnState.STATIONARY

    def turn(self):
        """ Turns the ship depending on the state of it's turn. """
        if self.turn_state is TurnState.RIGHT:
            self.facing -= self.turn_speed
            if self.facing < 0:
                self.facing = 2 * pi
        elif self.turn_state is TurnState.LEFT:
            self.facing += self.turn_speed
            if self.facing > 2 * pi:
                self.facing = 0

    def boost(self):
        """ Start the ship booster. """
        self.boost_state = BoostState.BOOSTING

    def stop_boost(self):
        """ Stop the ship booster. """
        self.boost_state = BoostState.STATIONARY

    def fire(self):
        """ Returns a particle object that is spawned from the front of the ship or None if not ready to fire. """
        current_time = time()
        if current_time - self.last_fire_time > self.reload_time:
            self.last_fire_time = current_time
            return Particle(
                self.centre_x + (2 * self.height * cos(self.facing)),
                self.centre_y + (2 * self.height * sin(self.facing)),
                self.particle_canon_speed * cos(self.facing),
                self.particle_canon_speed * sin(self.facing)
            )
        else:
            return None

    def velocity_handler(self):
        """
        Changes the value of the velocity of the ship in x and y axis.
        If the ship is already in the BOOSTING state it will create a higher thrust.
        """
        if self.boost_state is BoostState.BOOSTING:
            if self.thrust < self.thrust_max:
                self.thrust += self.thrust_incr
            self.velocity_x += cos(self.facing) * self.thrust
            self.velocity_y += sin(self.facing) * self.thrust
        else:
            self.thrust = 0

    def update(self):
        """ Update the various variables of the ship. """
        self.turn()
        self.velocity_handler()
        self.centre_x += self.velocity_x
        self.centre_y += self.velocity_y
        if self.centre_x < -10:
            self.centre_x = self.window_width + 10
        elif self.centre_x > self.window_width + 10:
            self.centre_x = -10
        if self.centre_y < -10:
            self.centre_y = self.window_height + 10
        elif self.centre_y > self.window_height + 10:
            self.centre_y = -10

    def draw(self):
        """ Redraw the ship at the 'new' location. """
        point_x = int(self.centre_x + (2 * self.height * cos(self.facing)))
        point_y = int(self.centre_y + (2 * self.height * sin(self.facing)))
        pyglet.graphics.draw_indexed(3, pyglet.gl.GL_LINE_LOOP,
                                     [0, 1, 2],
                                     ('v2i', (point_x, point_y,
                                              int(self.centre_x + (self.height * cos(self.facing + 140))),
                                              int(self.centre_y + (self.height * sin(self.facing + 140))),
                                              int(self.centre_x + (self.height * cos(self.facing - 140))),
                                              int(self.centre_y + (self.height * sin(self.facing - 140)))))
                                     )


class Asteroid(Entity):
    """ Handles how the asteroids are being drawn and their velocity and positioning. """

    def __init__(self, centre_x, centre_y, velocity_x, velocity_y, size):
        """ Initialise the velocity, position and shape of the asteroid. """
        self.centre_x = centre_x
        self.centre_y = centre_y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.radius = size
        self.points = []
        self.num_of_points = 7
        for i in range(0, self.num_of_points):
            self.points.append(random.uniform(self.radius-(self.radius/5), self.radius+(self.radius/5))
                               * cos(i*((2 * pi)/self.num_of_points)))
            self.points.append(random.uniform(self.radius-(self.radius/5), self.radius+(self.radius/5))
                               * sin(i*((2 * pi)/self.num_of_points)))

    def update(self):
        """ Update the position of the asteroid. """
        self.centre_x += self.velocity_x
        self.centre_y += self.velocity_y

    def draw(self):
        """ Draw the points of the asteroid and link the points. """
        current_points = []
        for i in range(0, self.num_of_points*2, 2):
            current_points.append(int(self.centre_x + self.points[i]))
            current_points.append(int(self.centre_y + self.points[i+1]))
        pyglet.graphics.draw(self.num_of_points, pyglet.gl.GL_LINE_LOOP, ('v2i', current_points))
