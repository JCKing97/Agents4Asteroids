import pyglet
import random
from enum import Enum
from math import cos, sin, sqrt
from typing import List, Tuple

from apscheduler.schedulers.background import BackgroundScheduler

from game.entities import Asteroid, Particle
from game.agent import Agent, Action

key = pyglet.window.key


class GameState(Enum):
    """ Is the game currently running, paused or is it game over. """
    INPLAY = 1
    PAUSED = 2
    OVER = 3


class Game:
    """ Handles the interaction between the agents and the environment. Handles the updating of the environment. """

    def __init__(self, window, agents: List[Agent]):
        """
        Initialise the agents, particles, asteroids (and asteroid creator), state of the game, points and agents.
        :param window: The window to create the entities on.
        """
        self.agents: List[Agent] = agents
        self.particles: List[Particle] = []
        self.asteroids: List[Asteroid] = []

        self.asteroid_creator = BackgroundScheduler()
        self.asteroid_creator.add_job(lambda: self.asteroid_generate(window), 'interval', seconds=0.5,
                                      id='asteroid generator')

        self.state: GameState = GameState.INPLAY
        self.window_width: int = window.width
        self.window_height: int = window.height
        self.points: int = 0

    def draw(self):
        """ Draws the entities. """
        for agent in self.agents:
            agent.draw()
        for asteroid in self.asteroids:
            asteroid.draw()
        for particle in self.particles:
            particle.draw()

    def update(self):
        """ Update the state of the entities """
        if self.state == GameState.INPLAY:
            self.particles, self.asteroids, self.agents, reward = \
                self.entity_update(self.window_width, self.window_height, self.particles, self.asteroids, self.agents)
            self.points += reward
            if not self.agents:
                self.game_over()

    def pause_toggle(self):
        """ Sets the game state from INPLAY to PAUSED and vice versa. """
        if self.state is GameState.INPLAY:
            self.state = GameState.PAUSED
            self.asteroid_creator.pause_job('asteroid generator')
        else:
            self.state = GameState.INPLAY
            self.asteroid_creator.resume_job('asteroid generator')

    def add_particle(self, particle):
        """ Adds a particle to the list of current particles. """
        self.particles.append(particle)

    def asteroid_generate(self, window):
        """
        Creates an asteroid. This also seems like it should be in the entity class. As in the calculations
        could be in the Asteroid class and then we just call here asteroid.generate().
        """
        if random.randint(0, 1) == 0:
            start_x = random.choice([0, window.width])
            start_y = random.randint(0, window.height)
            if start_x == 0:
                velocity_x = random.randint(1, 3)
            else:
                velocity_x = random.randint(-3, -1)
            velocity_y = random.randint(-3, 3)
        else:
            start_x = random.randint(0, window.width)
            start_y = random.choice([0, window.height])
            if start_y == 0:
                velocity_y = random.randint(1, 3)
            else:
                velocity_y = random.randint(-3, -1)
            velocity_x = random.randint(-3, 3)
        self.asteroids.append(Asteroid(start_x, start_y, velocity_x, velocity_y, 15))

    def out_of_window(self, asteroid,  window_width, window_height):
        """ Calculates if an asteroid is visible. """
        return (window_height + asteroid.radius < asteroid.centre_y or asteroid.centre_y < -asteroid.radius) or\
               (window_width + asteroid.radius < asteroid.centre_x or asteroid.centre_x < -asteroid.radius)

    def entity_update(self, window_width, window_height, particles: List[Particle], asteroids: List[Asteroid],
                      agents: List[Agent]) -> Tuple[List[Particle], List[Asteroid], List[Agent], int]:
        """ Updates the game entity objects. This includes the particles, asteroids and the agents ships. """
        destroyed_particles = []
        preserved_particles = []
        preserved_asteroids = []
        preserved_agents = agents
        reward = 0
        for agent in agents:
            agent.perceive(agent.get_perception_type()(agent.get_ship(), particles, asteroids, []))
            self.enact_decision(agent, agent.decide())
            agent.get_ship().update()
        for asteroid in asteroids:
            for agent in agents:
                if self.intersecting_ship(asteroid, agent.get_ship()):
                    preserved_agents.remove(agent)
            destroyed_asteroid = False
            if self.out_of_window(asteroid,  window_width, window_height):
                destroyed_asteroid = True
            for particle in particles:
                if self.is_inside(particle.centre_x, particle.centre_y, asteroid):
                    reward += 1
                    destroyed_asteroid = True
                    destroyed_particles.append(particle)
            if not destroyed_asteroid:
                preserved_asteroids.append(asteroid)
                asteroid.update()
        for particle in particles:
            if particle not in destroyed_particles and\
                    0 < particle.centre_x < window_width and 0 < particle.centre_y < window_height:
                particle.update()
                preserved_particles.append(particle)
        return preserved_particles, preserved_asteroids, preserved_agents, reward

    def enact_decision(self, agent: Agent, decision: Action):
        """
        Enact the decisions made by the agent in the order they are given.

        :param agent: The agent that is carrying out the action
        :param decision: The action to enact.
        """
        agent_ship = agent.get_ship()
        if decision is Action.TURNRIGHT:
            agent_ship.turn_right()
        elif decision is Action.TURNLEFT:
            agent_ship.turn_left()
        elif decision is Action.STOPTURN:
            agent_ship.stop_turn()
        elif decision is Action.BOOST:
            agent_ship.boost()
        elif decision is Action.STOPBOOST:
            agent_ship.stop_boost()
        elif decision is Action.FIRE:
            self.particles.append(agent_ship.fire())

    def intersecting_ship(self, asteroid, ship):
        """ Calculates the collision detection between the ship and asteroids. """
        # Detection adapted from http://www.phatcode.net/articles.php?id=459
        v1x = int(ship.centre_x + (2 * ship.height * cos(ship.facing)))
        v1y = int(ship.centre_y + (2 * ship.height * sin(ship.facing)))
        v2x = int(ship.centre_x + (ship.height * cos(ship.facing + 140)))
        v2y = int(ship.centre_y + (ship.height * sin(ship.facing + 140)))
        v3x = int(ship.centre_x + (ship.height * cos(ship.facing - 140)))
        v3y = int(ship.centre_y + (ship.height * sin(ship.facing - 140)))
        # Check if the vertices of the ship are intersecting the asteroid
        if self.is_inside(v1x, v1y, asteroid) or\
                self.is_inside(v2x, v2y, asteroid) or\
                self.is_inside(v3x, v3y, asteroid):
            return True
        # Check if circle center inside the ship
        if ((v2y - v1y)*(asteroid.centre_x - v1x) - (v2x - v1x)*(asteroid.centre_y - v1y)) >= 0 and \
                ((v3y - v2y)*(asteroid.centre_x - v2x) - (v3x - v2x)*(asteroid.centre_y - v2y)) >= 0 and \
                ((v1y - v3y)*(asteroid.centre_x - v3x) - (v1x - v3x)*(asteroid.centre_y - v3x)) >= 0:
            return True
        # Check if edges intersect circle
        # First edge
        c1x = asteroid.centre_x - v1x
        c1y = asteroid.centre_y - v1y
        e1x = v2x - v1x
        e1y = v2y - v1y

        k = c1x * e1x + c1y * e1y

        if k > 0:
            length = sqrt(e1x * e1x + e1y * e1y)
            k = k / length
            if k < length:
                if sqrt(c1x * c1x + c1y * c1y - k * k) <= asteroid.radius:
                    return True

        # Second edge
        c2x = asteroid.centre_x - v2x
        c2y = asteroid.centre_y - v2y
        e2x = v3x - v2x
        e2y = v3y - v2y

        k = c2x * e2x + c2y * e2y

        if k > 0:
            length = sqrt(e2x * e2x + e2y * e2y)
            k = k / length
            if k < length:
                if sqrt(c2x * c2x + c2y * c2y - k * k) <= asteroid.radius:
                    return True

        # Third edge
        c3x = asteroid.centre_x - v3x
        c3y = asteroid.centre_y - v3y
        e3x = v1x - v3x
        e3y = v1y - v3y

        k = c3x * e3x + c3y * e3y

        if k > 0:
            length = sqrt(e3x * e3x + e3y * e3y)
            k = k / length
            if k < length:
                if sqrt(c3x * c3x + c3y * c3y - k * k) <= asteroid.radius:
                    return True
        return False

    def is_inside(self, x, y, circle):
        if ((x - circle.centre_x) * (x - circle.centre_x) + (y - circle.centre_y) * (y - circle.centre_y)
                <= circle.radius * circle.radius):
            return True
        else:
            return False

    def start(self):
        """ Run the game. """
        self.asteroid_creator.start()

    def game_over(self):
        """ The end of the game when the player dies. """
        self.asteroid_creator.pause()
        self.state = GameState.OVER

    def on_key_press(self, symbol, modifiers):
        """
        On key presses update the actions of the user agents.

        :param symbol: The key pressed.
        :param modifiers: ?
        """
        for agent in self.agents:
            agent.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        """
        On key release update the actions of the user agents.

        :param symbol: The key release.
        :param modifiers: ?
        """
        for agent in self.agents:
            agent.on_key_release(symbol, modifiers)
