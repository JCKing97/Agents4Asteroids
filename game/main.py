import pyglet
import random


def twinkle(delta_time, window):
    """
    Set stars to twinkle in the background
    """
    pyglet.graphics.draw(4, pyglet.gl.GL_POINTS, ('v2i', (
        random.randint(0, window.width), random.randint(0, window.height),
        random.randint(0, window.width), random.randint(0, window.height),
        random.randint(0, window.width), random.randint(0, window.height),
        random.randint(0, window.width), random.randint(0, window.height),
    )))


def launch():
    """
    Set up and launch the game
    """
    window = pyglet.window.Window()
    label = pyglet.text.Label("Welcome to Asteroids", font_name="Arial", font_size=36,
                              x=window.width//2, y=window.height//2,
                              anchor_x="center", anchor_y="center")
    fps_display = pyglet.clock.ClockDisplay()

    @window.event
    def on_draw():
        window.clear()
        pyglet.clock.schedule_interval(twinkle, 0.00001, window=window)
        label.draw()
        fps_display.draw()

    pyglet.app.run()


if __name__ == "__main__":
    launch()
