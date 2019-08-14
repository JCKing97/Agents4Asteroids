import pyglet
import random
from game.game_control import Game, GameState
from game.agent import Agent, Action

key = pyglet.window.key


class MenuScreen:
    """
    The main screen where the player chooses to start the game. The keys to
    play the game are shown on screen. Either the player can play themselves
    or an agent can play the game.
    """

    def __init__(self, window):

        self.label = pyglet.text.Label("Welcome to Asteroids", font_name="Arial", font_size=36,
                                       x=(window.width // 2) - 10, y=3*(window.height // 4) - 10,
                                       anchor_x="center", anchor_y="center")
        self.fps_display = pyglet.window.FPSDisplay(window=window)
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

        @window.event
        def on_key_press(symbol, modifiers):
            if symbol == key.L:
                self.screen = Player1Screen(window)
            elif symbol == key.O:
                self.screen = AgentScreen(window)

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


class AgentScreen:
    """
    If it is chosen that the agent should play the game this class is loaded.
    """

    def __init__(self, window):
        self.game = Game(window)
        self.agent = Agent(self.game)
        self.game.attach(self.agent)

        @window.event
        def on_draw():
            window.clear()
            pyglet.text.Label("Agent Points: " + str(self.agent.points), font_name="Arial", font_size=12,
                              x=0, y=window.height,
                              anchor_x="left", anchor_y="top").draw()
            if self.game.state is not GameState.OVER:
                self.agent.perceive(self.game)
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

        @window.event
        def on_key_press(symbol, modifiers):
            if symbol == key.L:
                self.screen = Player1Screen(window)
            elif symbol == key.O:
                self.screen = AgentScreen(window)
            elif symbol == key.K:
                self.screen = MenuScreen(window)
            elif symbol == key.P:
                self.game.pause_unpause()


class Player1Screen:
    """
    The player class which captures the keys to move the ship and play the game.
    """

    def __init__(self, window):
        self.game = Game(window)

        @window.event
        def on_draw():
            window.clear()
            if self.game.state is not GameState.OVER:
                self.game.draw()
            else:
                self.screen = GameOverScreen(window, self.game.points)

        @window.event
        def on_key_press(symbol, modifiers):
            if symbol == key.L:
                self.screen = Player1Screen(window)
            elif symbol == key.O:
                self.screen = AgentScreen(window)
            elif symbol == key.K:
                self.screen = MenuScreen(window)
            elif symbol == key.P:
                self.game.pause_unpause()
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


class GameOverScreen:
    """
    When the player dies this screen is shown
    """

    def __init__(self, window, points):
        self.fps_display = pyglet.clock.ClockDisplay()

        @window.event
        def on_draw():
            window.clear()
            self.fps_display.draw()
            pyglet.text.Label("Game Over", font_name="Arial", font_size=36,
                              x=(window.width // 2) - 10, y=3 * (window.height // 4) - 10,
                              anchor_x="center", anchor_y="center").draw()
            pyglet.text.Label("Points: " + str(points), font_name="Arial", font_size=12,
                              x=window.width // 2, y=window.height // 2,
                              anchor_x="center", anchor_y="bottom").draw()
            pyglet.text.Label("L to Launch again, K to Quit", font_name="Arial", font_size=12,
                              x=window.width // 2, y=window.height // 2, anchor_x="center", anchor_y="top").draw()

        @window.event
        def on_key_press(symbol, modifiers):
            if symbol == key.L:
                self.screen = Player1Screen(window)
            elif symbol == key.K:
                self.screen = MenuScreen(window)
            elif symbol == key.O:
                self.screen = AgentScreen(window)


class Controller:
    """
    Starts the program. Creates a window and calls the menu screen.
    """
    def __init__(self):
        self.window = pyglet.window.Window()
        self.screen = MenuScreen(self.window)
        pyglet.app.run()


