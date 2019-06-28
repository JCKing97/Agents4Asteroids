import pyglet
import random

key = pyglet.window.key

class MenuScreen:

    def __init__(self, window):

        self.label = pyglet.text.Label("Welcome to Asteroids", font_name="Arial", font_size=36,
                                  x=(window.width // 2) - 10, y=(window.height // 2) - 10,
                                  anchor_x="center", anchor_y="center")
        self.fps_display = pyglet.clock.ClockDisplay()
        self.stars = pyglet.graphics.vertex_list(4, ('v2i', (
            random.randint(0, window.width), random.randint(0, window.height),
            random.randint(0, window.width), random.randint(0, window.height),
            random.randint(0, window.width), random.randint(0, window.height),
            random.randint(0, window.width), random.randint(0, window.height)
        )))

        @window.event
        def on_draw():
            window.clear()
            self.stars.draw(pyglet.graphics.GL_POINTS)
            self.twinkle(window)
            self.label.draw()
            self.fps_display.draw()

    def twinkle(self, window):
        """
        Set stars to twinkle in the background
        """
        star_to_twinkle = random.randint(0, 3)*2
        self.stars.vertices[star_to_twinkle] = random.randint(0, window.width)
        self.stars.vertices[star_to_twinkle+1] = random.randint(0, window.height)


class Player1Screen:

    def __init__(self, window):

        self.label = pyglet.text.Label("Play", font_name="Arial", font_size=36,
                                       x=(window.width // 2) - 10, y=(window.height // 2) - 10,
                                       anchor_x="center", anchor_y="center")

        @window.event
        def on_draw():
            window.clear()
            self.label.draw()


class Controller:

    def __init__(self):
        self.window = pyglet.window.Window()
        self.screen = MenuScreen(self.window)

        @self.window.event
        def on_key_press(symbol, modifiers):
            if symbol == key.P:
                self.screen = Player1Screen(self.window)
            elif symbol == key.H:
                self.screen = MenuScreen(self.window)

        pyglet.app.run()


if __name__ == "__main__":
    Controller()
