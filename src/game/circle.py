import math


class Circle:

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
