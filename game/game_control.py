import pyglet
import random
from enum import Enum
from math import cos, sin, sqrt
from apscheduler.schedulers.background import BackgroundScheduler
from game.game_entities import Ship, Asteroid

key = pyglet.window.key


class GameState(Enum):
    INPLAY = 1
    PAUSED = 2
    OVER = 3


class Game:

    def __init__(self, window):
        self.ship = Ship(window.width//2, window.height//2)
        self.particles = []
        self.fps_display = pyglet.window.FPSDisplay(window=window)
        self.asteroids = []
        self.asteroid_creator = BackgroundScheduler()
        self.asteroid_creator.start()
        self.asteroid_creator.add_job(lambda: self.asteroid_generate(window), 'interval', seconds=0.5,
                                      id='asteroid generator')
        self.state = GameState.INPLAY
        self.window_width = window.width
        self.window_height = window.height
        self.points = 0
        self.agents = []

    def multiplier(self):
        fps = pyglet.clock.get_fps()
        return ((100 - fps) / 100) if fps < 80 else 0.2

    def draw(self):
        if self.state is GameState.INPLAY:
            self.ship.update(self.window_width, self.window_height, self.multiplier())
            self.fps_display.draw()
            self.ship.draw()
            self.particles, self.asteroids, self.ship, reward = \
                self.entity_update(self.window_width, self.window_height, self.particles, self.asteroids, self.ship)
            for agent in self.agents:
                agent.perceive(self, reward, GameState.INPLAY if self.ship is not None else GameState.OVER)
            if self.ship is None:
                self.game_over()
        else:
            self.fps_display.draw()
            self.ship.draw()
            for asteroid in self.asteroids:
                asteroid.draw()
            for particle in self.particles:
                particle.draw()
        pyglet.text.Label("Points: " + str(self.points), font_name="Arial", font_size=12,
                          x=self.window_width, y=self.window_height,
                          anchor_x="right", anchor_y="top").draw()

    def game_over(self):
        self.state = GameState.OVER

    def pause_unpause(self):
        if self.state is GameState.INPLAY:
            self.state = GameState.PAUSED
            self.asteroid_creator.pause_job('asteroid generator')
        else:
            self.state = GameState.INPLAY
            self.asteroid_creator.resume_job('asteroid generator')

    def particle_update(self, window, particles):
        for particle in particles:
            if 0 < particle.centre_x < window.width and 0 < particle.centre_y < window.height:
                particle.centre_x += particle.velocity_x
                particle.centre_y += particle.velocity_y
                particle.draw()
            else:
                particles.remove(particle)

    def add_particle(self, particle):
        self.particles.append(particle)

    def asteroid_generate(self, window):
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
        return (window_height + asteroid.radius < asteroid.centre_y or asteroid.centre_y < -asteroid.radius) or\
               (window_width + asteroid.radius < asteroid.centre_x or asteroid.centre_x < -asteroid.radius)

    def entity_update(self, window_width, window_height, particles, asteroids, ship):
        destroyed_particles = []
        preserved_particles = []
        preserved_asteroids = []
        ship = ship
        reward = 0
        for asteroid in asteroids:
            destroyed_asteroid = False
            if self.out_of_window(asteroid,  window_width, window_height):
                destroyed_asteroid = True
            if self.intersecting_ship(asteroid, ship):
                self.game_over_update()
                return preserved_particles, preserved_asteroids, None, -20
            for particle in particles:
                if self.is_inside(particle.centre_x, particle.centre_y, asteroid):
                    reward += 1
                    destroyed_asteroid = True
                    destroyed_particles.append(particle)
            if not destroyed_asteroid:
                preserved_asteroids.append(asteroid)
                asteroid.update(self.multiplier())
                asteroid.draw()
        for particle in particles:
            if particle not in destroyed_particles and\
                    0 < particle.centre_x < window_width and 0 < particle.centre_y < window_height:
                particle.update(self.multiplier())
                particle.draw()
                preserved_particles.append(particle)
        return preserved_particles, preserved_asteroids, ship, reward

    def intersecting_ship(self, asteroid, ship):
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
        if ((v2y - v1y)*(asteroid.centre_x - v1x) - (v2x - v1x)*(asteroid.centre_y - v1y)) >= 0  and \
            ((v3y - v2y)*(asteroid.centre_x - v2x) - (v3x - v2x)*(asteroid.centre_y - v2y)) >= 0  and \
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
