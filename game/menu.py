from __future__ import annotations
import pyglet
import random
from abc import ABC, abstractmethod

from apscheduler.schedulers.background import BackgroundScheduler

from game.control import Game, GameState
from game.agent import Agent, Action
from game.perception import VectorPerception

key = pyglet.window.key


class ScreenListener(ABC):
    """ A base class to be implemented by anything that listens for screen changes. """

    @abstractmethod
    def notify(self, screen):
        """
        Notify a change in screen to the screen param.

        :param screen: The new screen to switch to.
        """
        raise NotImplementedError


class Screen(ABC):
    """
    A base class to be implemented by any screen used by the Controller.
    """

    def __init__(self, screen_listener: ScreenListener):
        """
        Set the listener to notify when changes to the screen being used are required.

        :param screen_listener:
        """
        self.screen_listener: ScreenListener = screen_listener

    @property
    def screen(self) -> Screen:
        """
        The screen to be used.

        :return: The screen
        :rtype: Screen
        """
        return self

    @screen.setter
    def screen(self, to_set: Screen):
        """
        Notify the listener that the screen has changed, so it can update and draw with the new screen.

        :param to_set: The screen to switch to.
        :return: None
        """
        self.screen_listener.notify(to_set)

    @abstractmethod
    def draw(self, window):
        """
        Draw the screens contents onto the window.

        :param window: The window to draw the contents onto.
        """
        raise NotImplementedError

    @abstractmethod
    def update(self, window):
        """
        Update the state of the screen based on the window.

        :param window: The window to update contents based on.
        """
        raise NotImplementedError


class MenuScreen(Screen):
    """
    The main screen where the player chooses to start the game. The keys to
    play the game are shown on screen. Either the player can play themselves
    or an agent can play the game.
    """

    def __init__(self, window, screen_listener):
        super().__init__(screen_listener)

        self.label = pyglet.text.Label("Welcome to Asteroids", font_name="Arial", font_size=36,
                                       x=(window.width // 2) - 10, y=3*(window.height // 4) - 10,
                                       anchor_x="center", anchor_y="center")

        initial_stars = tuple([random.randint(0, window.width) if i % 2 == 0 else
                               random.randint(0, window.height) for i in range(0, 40)])
        self.stars = pyglet.graphics.vertex_list(len(initial_stars)//2, ('v2i', initial_stars))

        self.stars_runner = BackgroundScheduler()
        self.stars_runner.add_job(lambda: self.passing_stars(window),
                                  'interval', seconds=0.01, id='display passing stars')
        self.stars_runner.start()

        @window.event
        def on_key_press(symbol, modifiers):
            if symbol == key.L:
                self.stars_runner.pause()
                self.screen = Player1Screen(window, screen_listener)
            elif symbol == key.O:
                self.stars_runner.pause()
                self.screen = AgentScreen(window, screen_listener)

    def draw(self, window):
        self.stars.draw(pyglet.graphics.GL_POINTS)
        self.label.draw()
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


class AgentScreen(Screen):
    """
    If it is chosen that the agent should play the game this class is loaded.
    """

    def __init__(self, window, screen_listener):
        super().__init__(screen_listener)
        self.game = Game(window)
        self.agent = Agent(self.game.ship)
        self.game.attach(self.agent)

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


class Player1Screen(Screen):
    """
    The screen for when playing a one player game. Capture the key presses to direct the ship.
    """

    def __init__(self, window, screen_listener):
        """
        Register handlers for when redrawing the window and key presses. Initialise the game.

        :param window: The window to get the drawing mechanism and key presses from.
        """
        super().__init__(screen_listener)
        self.game = Game(window)
        self.game.start()

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

    def draw(self, window):
        self.game.draw()

    def update(self, window):
        if self.game.state is GameState.OVER:
            self.screen = GameOverScreen(window, self.screen_listener, self.game.points)
        self.game.update()


class GameOverScreen(Screen):
    """
    When the player dies this screen is shown.
    """

    def __init__(self, window, screen_listener, points):
        super().__init__(screen_listener)
        self.points = points

        @window.event
        def on_key_press(symbol, modifiers):
            if symbol == key.L:
                self.screen = Player1Screen(window, screen_listener)
            elif symbol == key.K:
                self.screen = MenuScreen(window, screen_listener)
            elif symbol == key.O:
                self.screen = AgentScreen(window, screen_listener)

    def draw(self, window):
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


class Controller(ScreenListener):
    """
    Starts the program, controls the screens on show.
    """
    def __init__(self):
        self.window = pyglet.window.Window()
        self.screen = MenuScreen(self.window, self)

        @self.window.event
        def on_draw():
            self.clear_update_draw(self.window)

        pyglet.clock.schedule(lambda dt: 1 / 60)
        pyglet.app.run()

    def clear_update_draw(self, window):
        """
        Clear the window, update the screen and draw the screen.

        :param window: The window to update and draw with.
        :return: None
        """
        window.clear()
        self.screen.update(window)
        self.screen.draw(window)

    def notify(self, screen):
        """
        Set the current screen to screen_to_set.

        :param screen: The new screen to  be the current one.
        """
        self.screen = screen
