import pyglet
import random


def twinkle(window, stars):
    """
    Set stars to twinkle in the background
    """
    star_to_twinkle = random.randint(0, 3)*2
    stars.vertices[star_to_twinkle] = random.randint(0, window.width)
    stars.vertices[star_to_twinkle+1] = random.randint(0, window.height)



def launch():
    """
    Set up and launch the game
    """
    window = pyglet.window.Window()
    label = pyglet.text.Label("Welcome to Asteroids", font_name="Arial", font_size=36,
                              x=window.width//2, y=window.height//2,
                              anchor_x="center", anchor_y="center")
    fps_display = pyglet.clock.ClockDisplay()
    stars = pyglet.graphics.vertex_list(4, ('v2i', (
        random.randint(0, window.width), random.randint(0, window.height),
        random.randint(0, window.width), random.randint(0, window.height),
        random.randint(0, window.width), random.randint(0, window.height),
        random.randint(0, window.width), random.randint(0, window.height)
    )))

    @window.event
    def on_draw():
        window.clear()
        stars.draw(pyglet.graphics.GL_POINTS)
        twinkle(window, stars)
        label.draw()
        fps_display.draw()

    pyglet.app.run()


if __name__ == "__main__":
    launch()
