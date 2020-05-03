from __future__ import annotations

from typing import List, Type

import pyglet
import random
from abc import ABC, abstractmethod

from apscheduler.schedulers.background import BackgroundScheduler

from game.control import Game, GameState
from game.agent import Agent
from game.entities import Ship

from agents.agent_loader import load_agents

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

    def on_key_press(self, symbol, modifiers):
        """
        Add nothing to the default key press handler.

        :param symbol: The key pressed.
        :param modifiers: ?
        """
        pass

    def on_key_release(self, symbol, modifiers):
        """
        Add nothing to the default key release handler.

        :param symbol: The key release.
        :param modifiers: ?
        """
        pass


class MenuScreen(Screen):
    """
    The main screen where the player chooses to start the game. The keys to
    play the game are shown on screen. Either the player can play themselves
    or an agent can play the game.
    """

    def __init__(self, window, screen_listener: ScreenListener):
        """
        Initialise the stars, screen listener, title, instructions and key press detection.

        :param window: The window to draw on.
        :param screen_listener: The listener for changes to the screen.
        """
        self.window = window
        super().__init__(screen_listener)

        self.label = pyglet.text.Label("Welcome to Asteroids", font_name="Arial", font_size=36,
                                       x=(window.width // 2) - 10, y=3*(window.height // 4) - 10,
                                       anchor_x="center", anchor_y="center")

        initial_stars = tuple([random.randint(0, window.width) if i % 2 == 0 else
                               random.randint(0, window.height) for i in range(0, 40)])
        self.stars = pyglet.graphics.vertex_list(len(initial_stars)//2, ('v2i', initial_stars))

        self.agents: List[Type[Agent]] = load_agents()
        self.agent_selector_current = 0

    def on_key_press(self, symbol, modifiers):
        if symbol == key.RIGHT:
            self.agent_selector_current = (self.agent_selector_current + 1) % len(self.agents)
        elif symbol == key.LEFT:
            self.agent_selector_current = (self.agent_selector_current - 1) % len(self.agents)
            if self.agent_selector_current < 0:
                self.agent_selector_current = len(self.agents) - 1
        elif symbol == key.L:
            agent = self.agents[self.agent_selector_current](
                Ship(self.window.width // 2, self.window.height // 2, self.window)
            )
            self.screen = GameScreen(self.window, self.screen_listener, [agent])

    def draw(self, window):
        """
        Draw the stars, title and instructions on the window.

        :param window: The window to draw on.
        """
        self.stars.draw(pyglet.graphics.GL_POINTS)
        self.label.draw()
        pyglet.text.Label("L to Launch, P to Pause, K to Quit", font_name="Arial", font_size=12,
                          x=window.width // 2, y=window.height // 2, anchor_x="center", anchor_y="bottom").draw()
        pyglet.text.Label("W to Boost, D and A to turn and Space to Shoot", font_name="Arial", font_size=12,
                          x=window.width // 2, y=window.height // 2,
                          anchor_x="center", anchor_y="top").draw()
        pyglet.text.Label("Agent: " + self.agents[self.agent_selector_current].__name__, font_name="Arial", font_size=12,
                          x=window.width // 2, y=(window.height // 2) - 18,
                          anchor_x="center", anchor_y="top").draw()

    def update(self, window):
        """
        Update the position of the stars.

        :param window: The window to draw the stars on.
        """
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


class GameScreen(Screen):
    """
    Load a game with the specified agents.
    """

    def __init__(self, window, screen_listener: ScreenListener, agents: List[Agent]):
        """
        Initialise the listener to detect changes in the screen, an agent, the game and key press handler.

        :param window: The window to draw on.
        :param screen_listener: The listener to detect changes in the screen.
        """
        super().__init__(screen_listener)
        self.game: Game = Game(window, agents)
        self.game.start()

    def update(self, window):
        """
        Update the game.

        :param window: The window to draw on.
        """
        if self.game.state is not GameState.OVER:
            self.game.update()
        else:
            self.game_over(window)

    def draw(self, window):
        """
        Draw the points and game, update the screen if necessary.

        :param window: The window to draw on.
        """
        pyglet.text.Label("Points: " + str(self.game.points), font_name="Arial", font_size=12,
                          x=0, y=window.height,
                          anchor_x="left", anchor_y="top").draw()
        if self.game.state is not GameState.OVER:
            self.game.draw()
        else:
            self.game_over(window)

    def game_over(self, window):
        """
        Change the screen to go to game over.

        :param window: The window to draw on.
        """
        self.screen = GameOverScreen(window, self.screen_listener, self.game.points)

    def on_key_press(self, symbol, modifiers):
        """
        Pause if P is pressed and delegate presses to the game.

        :param symbol: The key pressed.
        :param modifiers: ?
        """
        if symbol == key.P:
            self.game.pause_toggle()
        self.game.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        """
        Delegate releases to the game.

        :param symbol: The key released.
        :param modifiers: ?
        """
        self.game.on_key_release(symbol, modifiers)


class GameOverScreen(Screen):
    """
    When the player dies this screen is shown.
    """

    def __init__(self, window, screen_listener, points):
        """
        Initialise the screen listener to detect screen changes and the display title and points.

        :param window: The window to draw on.
        :param screen_listener: The listener to listen for changes in the screen.
        :param points: The points to display.
        """
        super().__init__(screen_listener)
        self.points = points

    def draw(self, window):
        """
        Draw the game over title, the points and instructions.

        :param window: The window to draw on.
        """
        pyglet.text.Label("Game Over", font_name="Arial", font_size=36,
                          x=(window.width // 2) - 10, y=3 * (window.height // 4) - 10,
                          anchor_x="center", anchor_y="center").draw()
        pyglet.text.Label("Points: " + str(self.points), font_name="Arial", font_size=12,
                          x=window.width // 2, y=window.height // 2,
                          anchor_x="center", anchor_y="bottom").draw()
        pyglet.text.Label("K to Quit to menu", font_name="Arial", font_size=12,
                          x=window.width // 2, y=window.height // 2, anchor_x="center", anchor_y="top").draw()

    def update(self, window):
        """
        Do not update.

        :param window: The window to draw on.
        """
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

        @self.window.event
        def on_key_press(symbol, modifiers):
            if symbol == key.K:
                self.screen = MenuScreen(self.window, self)
            self.screen.on_key_press(symbol, modifiers)

        @self.window.event
        def on_key_release(symbol, modifiers):
            self.screen.on_key_release(symbol, modifiers)

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
