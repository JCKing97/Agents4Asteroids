import pyglet
import random

key = pyglet.window.key


class MenuScreen:

    def __init__(self, window):

        self.label = pyglet.text.Label("Welcome to Asteroids", font_name="Arial", font_size=36,
                                  x=(window.width // 2) - 10, y=(window.height // 2) - 10,
                                  anchor_x="center", anchor_y="center")
        self.fps_display = pyglet.clock.ClockDisplay()
        initial_stars = tuple([random.randint(0, window.width) if i % 2 == 0 else
                               random.randint(0, window.height) for i in range(0, 40)])
        self.stars = pyglet.graphics.vertex_list(len(initial_stars)//2, ('v2i', initial_stars))

        @window.event
        def on_draw():
            window.clear()
            self.stars.draw(pyglet.graphics.GL_POINTS)
            self.passing_stars(window)
            self.label.draw()
            self.fps_display.draw()

    def passing_stars(self, window):
        """
        Cause stars to appear to be passing
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
                    self.stars.vertices[i] += window.width//100
                else:
                    self.stars.vertices[i] -= window.width//100
                if self.stars.vertices[i+1] > window.height-self.stars.vertices[i+1]:
                    self.stars.vertices[i+1] += window.height//100
                else:
                    self.stars.vertices[i+1] -= window.height//100


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
