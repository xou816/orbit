import math
import random
import itertools


class Circle:

    def generator(circles_per_screen, margin):

        # Maximal and minimal radis
        max_r = 1/(10*circles_per_screen)
        min_r = 0.05

        for generated in itertools.count():

            screen_circles = []

            for i in range(circles_per_screen):
                r = random.uniform(min_r, max_r)
                # Random x position, but ensuring we do not overflow
                x = random.uniform(r, 1 - r)
                # offset + nth screen portion + some margin between circles
                y = generated + i*1/circles_per_screen + margin
                screen_circles.append(Circle(x, y, r))

            yield screen_circles

    """Drawn circle"""

    def __init__(self, x, y, r):

        """Create a circle"""

        self.x = x
        self.y = y
        self.radius = r

    def draw(self, cr, color=None):

        """Draw circle based on player's position px, py"""

        # Small trick for cool coloring effect
        if color is None:
            color = (0.6*(self.y % 1 + 0.5), 0, 0.1, 1)
        cr.set_source_rgba(*color)
        cr.arc(self.x, self.y, self.radius, 0, 2*math.pi)
        cr.fill()

    def draw_zone(self, cr, radius):

        cr.set_dash([0.01, 0.02])
        cr.set_source_rgba(0.6, 0, 0.1, 1)
        cr.set_line_width(0.005)
        cr.arc(self.x, self.y, radius, 0, 2*math.pi)
        cr.stroke()
