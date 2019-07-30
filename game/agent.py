from enum import Enum
from game.game_control import GameState


class Action(Enum):
    BOOST = 1
    STOPBOOST = 2
    TURNRIGHT = 3
    TURNLEFT = 4
    STOPTURN = 5
    FIRE = 6


class Agent:

    def __init__(self, game):
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
        self.last_action = []

    def perceive(self, game, reward, game_state):
        new_ship_state = {'centre_x': game.ship.centre_x, 'centre_y': game.ship.centre_y,
                           'velocity_x': game.ship.velocity_x, 'velocity_y': game.ship.velocity_y,
                           'facing': game.ship.facing, 'thrust': game.ship.thrust,
                           'turn_speed': game.ship.turn_speed, 'height': game.ship.height}
        new_asteroid_data = [{'centre_x': asteroid.centre_x, 'centre_y': asteroid.centre_y,
                               'velocity_x': asteroid.velocity_x, 'velocity_y': asteroid.velocity_y,
                               'radius': asteroid.radius} for asteroid in game.asteroids]
        new_particle_data = [{'centre_x': particle.centre_x, 'centre_y': particle.centre_y,
                               'velocity_x': particle.velocity_x, 'velocity_y': particle.velocity_y}
                              for particle in game.particles]
        self.remember(self.ship_state, self.asteroid_data, self.particle_data, self.last_action, new_ship_state,
                      new_asteroid_data, new_particle_data, reward, game_state)
        self.experience_replay()

    def remember(self, ship_data, asteroid_data, particle_data, last_action, new_ship_data, new_asteroid_data,
                 new_particle_data, reward, game_state):
        pass

    def experience_replay(self):
        pass

    def decide(self):
        action = [Action.TURNRIGHT, Action.FIRE]
        self.last_action = [Action.TURNRIGHT, Action.FIRE]
        return action

    def new_game(self, game):
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
        self.last_action = []
