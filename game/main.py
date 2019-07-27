import pyglet
import random

key = pyglet.window.key


class MenuScreen:

    def __init__(self, window, draw_controls):

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
            self.passing_stars(window, self.stars)
            self.label.draw()
            self.fps_display.draw()
            draw_controls(window)

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


class Player1Screen:

    def __init__(self, window, draw_contols):

        self.label = pyglet.text.Label("Play", font_name="Arial", font_size=36,
                                       x=(window.width // 2) - 10, y=(window.height // 2) - 10,
                                       anchor_x="center", anchor_y="center")

        @window.event
        def on_draw():
            window.clear()
            self.label.draw()
            draw_contols(window)


class Controller:

    def __init__(self):
        self.window = pyglet.window.Window()
        self.screen = MenuScreen(self.window, self.draw_controls)

        @self.window.event
        def on_key_press(symbol, modifiers):
            if symbol == key.P:
                self.screen = Player1Screen(self.window, self.draw_controls)
            elif symbol == key.H:
                self.screen = MenuScreen(self.window, self.draw_controls)

        pyglet.app.run()

    def draw_controls(self, window):
        pyglet.text.Label("L to Launch, P to Pause, K to Quit, WASD to Move, Q and E to turn, and Space to Shoot", font_name="Arial", font_size=12,
                          x=window.width//2, anchor_x="center", anchor_y="bottom").draw()
        print("Drawing controls")


if __name__ == "__main__":
    Controller()
