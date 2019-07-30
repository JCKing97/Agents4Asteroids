import pyglet
import random
from enum import Enum
from math import cos, sin, pi, sqrt
from apscheduler.schedulers.background import BackgroundScheduler

key = pyglet.window.key


class MenuScreen:

    def __init__(self, window):

        self.label = pyglet.text.Label("Welcome to Asteroids", font_name="Arial", font_size=36,
                                       x=(window.width // 2) - 10, y=3*(window.height // 4) - 10,
                                       anchor_x="center", anchor_y="center")
        self.fps_display = pyglet.clock.ClockDisplay()
        initial_stars = tuple([random.randint(0, window.width) if i % 2 == 0 else
                               random.randint(0, window.height) for i in range(0, 40)])
        self.stars = pyglet.graphics.vertex_list(len(initial_stars)//2, ('v2i', initial_stars))

        @window.event
        def on_draw():
            window.clear()
            self.stars.draw(pyglet.graphics.GL_POINTS)
            self.passing_stars(window, self.stars)
            self.label.draw()
            self.fps_display.draw()
            pyglet.text.Label("L to Launch, P to Pause, K to Quit", font_name="Arial", font_size=12,
                              x=window.width // 2, y=window.height//2, anchor_x="center", anchor_y="bottom").draw()
            pyglet.text.Label("W to Boost, D and A to turn and Space to Shoot", font_name="Arial", font_size=12,
                              x=window.width // 2, y=window.height//2,
                              anchor_x="center", anchor_y="top").draw()

    def passing_stars(self, window, stars):
        """
        Cause stars to appear to be passing
        """
        for i in range(0, len(stars.vertices), 2):
            # If the star has reached the edge of the screen reset it into the middle
            if stars.vertices[i] >= window.width or stars.vertices[i+1] >= window.height:
                stars.vertices[i] = random.randint((window.width/2)-(window.width/10),
                                                        (window.width/2)+(window.width/10))
                stars.vertices[i+1] = random.randint((window.height/2)-(window.height/10),
                                                          (window.height/2)+(window.height/10))
            else:
                # If the star has not reached the edge keep showing it passing through space
                if stars.vertices[i] > window.width-stars.vertices[i]:
                    stars.vertices[i] += window.width//100
                else:
                    stars.vertices[i] -= window.width//100
                if stars.vertices[i+1] > window.height-stars.vertices[i+1]:
                    stars.vertices[i+1] += window.height//150
                else:
                    stars.vertices[i+1] -= window.height//150


class TurnState(Enum):
    STATIONARY = 1
    RIGHT = 2
    LEFT = 3


class BoostState(Enum):
    STATIONARY = 1
    BOOSTING = 2


class Particle:

    def __init__(self, centre_x, centre_y, velocity_x, velocity_y):
        self.centre_x = centre_x
        self.centre_y = centre_y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y

    def draw(self):
        self.centre_x += self.velocity_x
        self.centre_y += self.velocity_y
        pyglet.graphics.draw(1, pyglet.gl.GL_POINTS, ('v2i', (int(self.centre_x), int(self.centre_y))))


class Ship:

    def __init__(self, centre_x, centre_y):
        self.facing = 0
        self.centre_x = centre_x
        self.centre_y = centre_y
        self.velocity_x = 0
        self.velocity_y = 0
        self.height = 10
        self.turn_speed = 0.3
        self.turn_state = TurnState.STATIONARY
        self.boost_state = BoostState.STATIONARY
        self.thrust = 0
        self.thrust_max = 2
        self.thrust_incr = 0.4
        self.particle_canon_speed = 20

    def turn_right(self):
        self.turn_state = TurnState.RIGHT

    def turn_left(self):
        self.turn_state = TurnState.LEFT

    def stop_turn(self):
        self.turn_state = TurnState.STATIONARY

    def turn(self):
        if self.turn_state is TurnState.RIGHT:
            self.facing -= self.turn_speed
        elif self.turn_state is TurnState.LEFT:
            self.facing += self.turn_speed

    def boost(self):
        self.boost_state = BoostState.BOOSTING

    def stop_boost(self):
        self.boost_state = BoostState.STATIONARY

    def fire(self):
        return Particle(
            self.centre_x + (2 * self.height * cos(self.facing)),
            self.centre_y + (2 * self.height * sin(self.facing)),
            self.particle_canon_speed * cos(self.facing),
            self.particle_canon_speed * sin(self.facing)
        )

    def velocity_handler(self):
        if self.boost_state is BoostState.BOOSTING:
            if self.thrust < self.thrust_max:
                self.thrust += self.thrust_incr
            self.velocity_x += cos(self.facing) * self.thrust
            self.velocity_y += sin(self.facing) * self.thrust
        else:
            self.thrust = 0

    def draw(self):
        self.turn()
        self.velocity_handler()
        self.centre_x += self.velocity_x
        self.centre_y += self.velocity_y
        pyglet.graphics.draw_indexed(3, pyglet.gl.GL_LINE_LOOP,
                                     [0, 1, 2],
                                     ('v2i', (int(self.centre_x + (2 * self.height * cos(self.facing))),
                                              int(self.centre_y + (2 * self.height * sin(self.facing))),
                                              int(self.centre_x + (self.height * cos(self.facing + 140))),
                                              int(self.centre_y + (self.height * sin(self.facing + 140))),
                                              int(self.centre_x + (self.height * cos(self.facing - 140))),
                                              int(self.centre_y + (self.height * sin(self.facing - 140)))))
                                     )


class Asteroid:

    def __init__(self, centre_x, centre_y, velocity_x, velocity_y, size):
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

    def draw(self):
        self.centre_x += self.velocity_x
        self.centre_y += self.velocity_y
        current_points = []
        for i in range(0, self.num_of_points*2, 2):
            current_points.append(int(self.centre_x + self.points[i]))
            current_points.append(int(self.centre_y + self.points[i+1]))
        pyglet.graphics.draw(self.num_of_points, pyglet.gl.GL_LINE_LOOP, ('v2i', current_points))


class Player1Screen:

    def __init__(self, window):
        self.ship = Ship(window.width//2, window.height//2)
        self.particles = []
        self.fps_display = pyglet.clock.ClockDisplay()
        self.asteroids = []
        self.asteroid_creator = BackgroundScheduler()
        self.asteroid_creator.start()
        self.asteroid_creator.add_job(lambda: self.asteroid_generate(window), 'interval', seconds=3)

        @window.event
        def on_draw():
            window.clear()
            self.ship.draw()
            self.fps_display.draw()
            self.particles, self.asteroids, self.ship = \
                self.entity_update(window, self.particles, self.asteroids, self.ship)
            if self.ship is None:
                print("Game over")

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

    def out_of_window(self, asteroid, window):
        return (window.height + asteroid.radius < asteroid.centre_y or asteroid.centre_y < -asteroid.radius) or\
               (window.width + asteroid.radius < asteroid.centre_x or asteroid.centre_x < -asteroid.radius)

    def entity_update(self, window, particles, asteroids, ship):
        destroyed_particles = []
        preserved_particles = []
        preserved_asteroids = []
        ship = ship
        for asteroid in asteroids:
            destroyed_asteroid = False
            if self.out_of_window(asteroid, window):
                destroyed_asteroid = True
            if self.intersecting_ship(asteroid, ship):
                return preserved_particles, preserved_asteroids, None
            for particle in particles:
                if self.is_inside(particle.centre_x, particle.centre_y, asteroid):
                    destroyed_asteroid = True
                    destroyed_particles.append(particle)
            if not destroyed_asteroid:
                preserved_asteroids.append(asteroid)
                asteroid.draw()
        for particle in particles:
            if particle not in destroyed_particles and\
                    0 < particle.centre_x < window.width and 0 < particle.centre_y < window.height:
                particle.draw()
                preserved_particles.append(particle)
        return preserved_particles, preserved_asteroids, ship

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
        if ((v2y - v1y) * (asteroid.centre_x - v1x) - (v2x - v1x) * (asteroid.centre_y - v1y)) >= 0  and \
            ((v3y - v2y) * (asteroid.centre_x - v2x) - (v3x - v2x) * (asteroid.centre_y - v2y)) >= 0 and \
            ((v1y - v3y) * (asteroid.centre_x - v3x) - (v1x - v3x) * (asteroid.centre_x - v3x)) >= 0:
           
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


class State(Enum):
    MENU = 1
    LAUNCHED = 2
    PAUSED = 3


class Controller:

    def __init__(self):
        self.window = pyglet.window.Window()
        self.screen = MenuScreen(self.window)
        self.state = State.MENU

        @self.window.event
        def on_key_press(symbol, modifiers):
            if symbol == key.L:
                self.screen = Player1Screen(self.window)
                self.state = State.LAUNCHED
            elif symbol == key.K:
                self.screen = MenuScreen(self.window)
                self.state = State.MENU
            elif symbol == key.P:
                if self.state is State.LAUNCHED:
                    self.state = State.PAUSED
                elif self.state is State.PAUSED:
                    self.state = State.LAUNCHED
            elif self.state is State.LAUNCHED and symbol == key.W:
                self.screen.ship.boost()
            elif self.state is State.LAUNCHED and symbol == key.D:
                self.screen.ship.turn_right()
            elif self.state is State.LAUNCHED and symbol == key.A:
                self.screen.ship.turn_left()
            elif self.state is State.LAUNCHED and symbol == key.SPACE:
                self.screen.particles.append(self.screen.ship.fire())

        @self.window.event
        def on_key_release(symbol, modifiers):
            if (self.state is State.LAUNCHED or self.state is State.PAUSED) and (symbol == key.A or symbol == key.D):
                self.screen.ship.stop_turn()
            if (self.state is State.LAUNCHED or self.state is State.PAUSED) and symbol == key.W:
                self.screen.ship.stop_boost()

        pyglet.app.run()


if __name__ == "__main__":
    Controller()
