import math
import cairo
from .scene import tmp_context, Scene


HOOK_DIST_TOLERANCE = 0.01


class Player:

    def __init__(self, x, y, angle, size=0.01, range=1, speed=1):

        """Create a new player"""

        self._old_pos = (x, y)
        self._pos = (x, y)
        self._angle = angle
        self.size = size
        self.range = range
        self.speed = speed

        self.hook = False
        self.hook_data = None

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, angle):
        angle = math.fmod(angle, 2*math.pi)
        if angle < 0:
            angle = 2*math.pi + angle
        self._angle = angle

    @property
    def x(self): return self._pos[0]

    @property
    def y(self): return self._pos[1]

    @property
    def position(self):
        return self._pos

    @position.setter
    def position(self, new_pos):
        self._old_pos = self._pos
        self._pos = new_pos

    @property
    def screen(self):

        """
        Return the index of the buffer on which the player should be drawn
        """

        return int(self.y)

    @property
    def vector(self):

        """Return a directional vector"""

        dir_x = math.sin(self.angle)
        dir_y = -math.cos(self.angle)
        return dir_x, dir_y

    def scene(self, cr):

        return Scene(cr, self._apply_scene_context)

    def rotate(self, angle):

        """
        Rotate player by given angle, relative to vertical axis, clock wise is
        positive.
        """

        self.angle = self.angle + angle

    def move(self):

        """Compute next position"""

        if self.hook:
            circle, rotation = self.hook_data
            dist = self.dist_circle(circle)
            self.rotate(rotation*self.speed/dist)
            self.position = (circle.x - rotation*dist*math.cos(self.angle),
                             circle.y + rotation*dist*math.sin(self.angle))
        else:
            x, y = self.position
            self.position = (x + self.speed*math.sin(self.angle),
                             y + self.speed*math.cos(self.angle))

    def dist_circle(self, circle):

        return math.hypot(circle.y-self.y, circle.x-self.x)

    def reset_hook(self):

        self.hook = False
        self.hook_data = None

    def natural_hook_point(self, circle):

        angle = self.angle
        if angle == 0:
            angle = math.pi/120  # Small angle

        # Linear equation for player direction
        slope = 1/math.tan(angle)
        intercept = self.y - slope*self.x

        # Linear equation for the line that is orthogonal to player direction
        # and goes through the circle's center
        slope_circle = -math.tan(angle)
        intercept_circle = circle.y - slope_circle*circle.x

        # Natural hook point
        hx = (intercept_circle - intercept)/(slope - slope_circle)
        hy = slope*hx + intercept

        return hx, hy

    def rotation(self, circle):

        cx, cy = circle.x, circle.y
        x1, y1 = self.x-cx, self.y-cy
        x2, y2 = self.vector
        # Cross product positive along z axis (orthogonal to screen)
        if x1*y2 + y1*x2 > 0:
            return 1
        else:
            return -1

    def target(self):

        if self.hook_data is not None:
            return self.hook_data[0]
        else:
            return None

    def candidate_target(self, circles):

        return min(circles, key=self.dist_circle)

    def _apply_scene_context(self, cr):

        cr.translate(0.5 - self.x, 0.5 - self.y)

    def find_target(self, circles):

        x, y = self.position
        target = self.candidate_target(circles)
        tx, ty = target.x, target.y
        rotation = self.rotation(target)

        if self.hook_data is None and self.dist_circle(target) < self.range:

            hx, hy = self.natural_hook_point(target)
            dx, dy = self.vector
            dot_prod = (hx-x)*dx + (hy-y)*dy

            # Natural hook point is on our way!
            # We save data, but we do not hook!
            if dot_prod < 0:
                self.hook = False
                self.hook_data = (target, rotation)
            else:
                # We need to change the player's angle since it is not a
                # natural hook
                new_angle = math.atan2(y-ty, x-tx)
                # Reverse if positive rotation
                self.angle = 1/2*(1+rotation)*math.pi - new_angle

                self.hook = True
                self.hook_data = (target, rotation)

        # We have a target defined, we're just not close enough yet!
        if self.hook_data is not None and not self.hook:

            circle, rotation = self.hook_data
            hx, hy = self.natural_hook_point(circle)
            if (abs(hx-x) < HOOK_DIST_TOLERANCE and
                    abs(hy-y) < HOOK_DIST_TOLERANCE):
                self.hook = True

    def draw(self, cr):

        """Draw player"""

        size = self.size
        with tmp_context(cr):
            cr.translate(self.x, self.y)  # Center player
            cr.rotate(-self.angle)
            cr.move_to(size, -3/2*size)
            cr.line_to(size, 0)
            # Everything is drawn at 0,0 but translated beforehand
            cr.arc(0, 0, size, 0, math.pi)
            cr.line_to(-size, -3/2*size)
            cr.close_path()
            cr.set_source_rgba(0.8, 0.8, 0.8, 1)
            cr.fill()

    def draw_trail(self, cr):

        """Draw player trail from x, y to player position"""

        with tmp_context(cr):

            # Everything is drawn at (0,0) and must be translated and rotated
            x, y = self._old_pos
            cr.translate(x, y)
            cr.rotate(-self.angle)

            colors = [
                (0.5, 0.05, 0.05, 1),
                (0.05, 0.5, 0.05, 1),
                (0.05, 0.05, 0.5, 1),
            ]
            size = self.size/(len(colors))
            px, py = self.position
            dist = math.hypot(px-x, py-y)

            for i, color in enumerate(colors):

                cr.set_source_rgba(*color)
                cr.set_line_cap(cairo.LINE_CAP_SQUARE)
                cr.set_line_width(size)
                cr.move_to(-size/2 + i*size, 0)
                cr.line_to(-size/2 + i*size, dist)
                cr.stroke()
