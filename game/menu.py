import pyglet
import random

from apscheduler.schedulers.background import BackgroundScheduler

from game.control import Game, GameState
from game.agent import Agent, Action
from game.perception import VectorPerception

key = pyglet.window.key
 

class MenuScreen:
    """
    The main screen where the player chooses to start the game. The keys to
    play the game are shown on screen. Either the player can play themselves
    or an agent can play the game.
    """

    def __init__(self, window, screen_listener):
        self.label = pyglet.text.Label("Welcome to Asteroids", font_name="Arial", font_size=36,
                                       x=(window.width // 2) - 10, y=3*(window.height // 4) - 10,
                                       anchor_x="center", anchor_y="center")
        self.fps_display = pyglet.window.FPSDisplay(window=window)
        initial_stars = tuple([random.randint(0, window.width) if i % 2 == 0 else
                               random.randint(0, window.height) for i in range(0, 40)])
        self.stars = pyglet.graphics.vertex_list(len(initial_stars)//2, ('v2i', initial_stars))

        self.stars_runner = BackgroundScheduler()
        self.stars_runner.add_job(lambda: self.passing_stars(window),
                                  'interval', seconds=0.01, id='display passing stars')
        self.stars_runner.start()
        self.screen_listener = screen_listener

        @window.event
        def on_key_press(symbol, modifiers):
            if symbol == key.L:
                self.stars_runner.pause()
                self.screen = Player1Screen(window, screen_listener)
            elif symbol == key.O:
                self.stars_runner.pause()
                self.screen = AgentScreen(window, screen_listener)

    @property
    def screen(self):
        return self

    @screen.setter
    def screen(self, to_set):
        self.screen_listener.set_screen(to_set)

    def draw(self, window):
        self.stars.draw(pyglet.graphics.GL_POINTS)
        self.label.draw()
        self.fps_display.draw()
        pyglet.text.Label("L to Launch, P to Pause, K to Quit", font_name="Arial", font_size=12,
                          x=window.width // 2, y=window.height // 2, anchor_x="center", anchor_y="bottom").draw()
        pyglet.text.Label("W to Boost, D and A to turn and Space to Shoot", font_name="Arial", font_size=12,
                          x=window.width // 2, y=window.height // 2,
                          anchor_x="center", anchor_y="top").draw()

    def update(self, window):
        self.passing_stars(window)

    def passing_stars(self, window):
        """
        Cause stars to appear to be passing.
        """
        for i in range(0, len(self.stars.vertices), 2):
            # If the star has reached the edge of the screen reset it into the middle
            if self.stars.vertices[i] >= window.width or self.stars.vertices[i+1] >= window.height:
                self.stars.vertices[i] = random.randint((window.width/2)-(window.width/10),
                                                        (window.width/2)+(window.width/10))
                self.stars.vertices[i+1] = random.randint((window.height/2)-(window.height/10),
                                                          (window.height/2)+(window.height/10))
            else:
                # If the star has not reached the edge keep showing it passing through space
                if self.stars.vertices[i] > window.width-self.stars.vertices[i]:
                    self.stars.vertices[i] += window.width//300
                else:
                    self.stars.vertices[i] -= window.width//300
                if self.stars.vertices[i+1] > window.height-self.stars.vertices[i+1]:
                    self.stars.vertices[i+1] += window.height//300
                else:
                    self.stars.vertices[i+1] -= window.height//300


class AgentScreen:
    """
    If it is chosen that the agent should play the game this class is loaded.
    """

    def __init__(self, window, screen_listener):
        self.game = Game(window)
        self.agent = Agent(self.game.ship)
        self.game.attach(self.agent)
        self.screen_listener = screen_listener

        @window.event
        def on_key_press(symbol, modifiers):
            if symbol == key.L:
                self.screen = Player1Screen(window, screen_listener)
            elif symbol == key.O:
                self.screen = AgentScreen(window, screen_listener)
            elif symbol == key.K:
                self.screen = MenuScreen(window, screen_listener)
            elif symbol == key.P:
                self.game.pause_toggle()

    @property
    def screen(self):
        return self

    @screen.setter
    def screen(self, to_set):
        self.screen_listener.set_screen(to_set)

    def update(self, window):
        if self.game.state is not GameState.OVER:
            self.agent.perceive(VectorPerception(self.game))
            actions = self.agent.decide()
            for action in actions:
                if action is Action.TURNRIGHT:
                    self.game.ship.turn_right()
                elif action is Action.TURNLEFT:
                    self.game.ship.turn_left()
                elif action is Action.STOPTURN:
                    self.game.ship.stop_turn()
                elif action is Action.BOOST:
                    self.game.ship.boost()
                elif action is Action.STOPBOOST:
                    self.game.ship.stop_boost()
                elif action is Action.FIRE:
                    self.game.particles.append(self.game.ship.fire())
            self.game.draw()
        else:
            self.agent.perceive(self.game)
            self.game = Game(window)
            self.agent.new_game(self.game)
            self.game.attach(self.agent)

    def draw(self, window):
        pyglet.text.Label("Agent Points: " + str(self.agent.points), font_name="Arial", font_size=12,
                          x=0, y=window.height,
                          anchor_x="left", anchor_y="top").draw()


class Player1Screen:
    """
    The screen for when playing a one player game. Capture the key presses to direct the ship.
    """

    def __init__(self, window, screen_listener):
        """
        Register handlers for when redrawing the window and key presses. Initialise the game.

        :param window: The window to get the drawing mechanism and key presses from.
        """
        self.game = Game(window)
        self.game.start()

        self.screen_listener = screen_listener

        @window.event
        def on_key_press(symbol, modifiers):
            if symbol == key.L:
                self.screen = Player1Screen(window, screen_listener)
            elif symbol == key.O:
                self.screen = AgentScreen(window, screen_listener)
            elif symbol == key.K:
                self.screen = MenuScreen(window, screen_listener)
            elif symbol == key.P:
                self.game.pause_toggle()
            elif self.game.state is GameState.INPLAY and symbol == key.W:
                self.game.ship.boost()
            elif self.game.state is GameState.INPLAY and symbol == key.D:
                self.game.ship.turn_right()
            elif self.game.state is GameState.INPLAY and symbol == key.A:
                self.game.ship.turn_left()
            elif self.game.state is GameState.INPLAY and symbol == key.SPACE:
                self.game.particles.append(self.game.ship.fire())

        @window.event
        def on_key_release(symbol, modifiers):
            if (self.game.state is GameState.INPLAY or self.game.state is GameState.PAUSED)\
                    and (symbol == key.A or symbol == key.D):
                self.game.ship.stop_turn()
            if (self.game.state is GameState.INPLAY or self.game.state is GameState.PAUSED) and symbol == key.W:
                self.game.ship.stop_boost()

    @property
    def screen(self):
        return self

    @screen.setter
    def screen(self, to_set):
        self.screen_listener.set_screen(to_set)

    def draw(self, window):
        self.game.draw()

    def update(self, window):
        if self.game.state is GameState.OVER:
            window.screen = GameOverScreen(window, self.screen_listener, self.game.points)
        self.game.update()


class GameOverScreen:
    """
    When the player dies this screen is shown.
    """

    def __init__(self, window, screen_listener, points):
        self.fps_display = pyglet.clock.ClockDisplay()
        self.points = points
        self.screen_listener = screen_listener

        @window.event
        def on_key_press(symbol, modifiers):
            if symbol == key.L:
                self.screen = Player1Screen(window, screen_listener)
            elif symbol == key.K:
                self.screen = MenuScreen(window, screen_listener)
            elif symbol == key.O:
                self.screen = AgentScreen(window, screen_listener)

    @property
    def screen(self):
        return self

    @screen.setter
    def screen(self, to_set):
        self.screen_listener.set_screen(to_set)

    def draw(self, window):
        self.fps_display.draw()
        pyglet.text.Label("Game Over", font_name="Arial", font_size=36,
                          x=(window.width // 2) - 10, y=3 * (window.height // 4) - 10,
                          anchor_x="center", anchor_y="center").draw()
        pyglet.text.Label("Points: " + str(self.points), font_name="Arial", font_size=12,
                          x=window.width // 2, y=window.height // 2,
                          anchor_x="center", anchor_y="bottom").draw()
        pyglet.text.Label("L to Launch again, K to Quit", font_name="Arial", font_size=12,
                          x=window.width // 2, y=window.height // 2, anchor_x="center", anchor_y="top").draw()

    def update(self, window):
        pass


class Controller:
    """
    Starts the program. Creates a window and calls the menu screen.
    """
    def __init__(self):
        self.window = pyglet.window.Window()
        self.screen = MenuScreen(self.window, self)

        @self.window.event
        def on_draw():
            self.update(self.window)

        pyglet.clock.schedule(lambda dt: 1 / 60)
        pyglet.app.run()

    def update(self, window):
        window.clear()
        self.screen.update(window)
        self.screen.draw(window)

    def set_screen(self, screen_to_set):
        self.screen = screen_to_set
