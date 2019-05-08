import random
import math
from .scene import Scene, tmp_context
from .player import Player
from .circle import Circle


CIRCLES_PER_SCREEN = 2


class Game:

    def __init__(self, fps):

        self._size = (0, 0)
        self._scene_params = (0, 0, 0, 0)
        self.circles = []
        self.pressed_keys = []
        self.player = Player(0.5, 0, 0,
                             size=0.02,
                             range=1,
                             speed=0.5/fps)

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size):
        self._size = size

    @property
    def scene_params(self):
        return self._scene_params

    @scene_params.setter
    def scene_params(self, scene_params):
        self._scene_params = scene_params

    def apply_scene_context(self, cr):

        """Apply scene parameters to the given Cairo context"""

        tr_x, tr_y, sc_x, sc_y = self.scene_params
        cr.translate(tr_x, tr_y)  # Centering
        cr.scale(sc_x, sc_y)  # 1:1 aspect ratio + upward vertical axis
        cr.translate(0, -1)  # Set 0,0 to bottom left

    def get_scene(self, cr):

        main_scene = Scene(cr, self.apply_scene_context)
        return GameScene(self, cr, main_scene)

    def on_keypress(self, keyname):

        if keyname == "Left":
            self.player.rotate(-math.pi/12)
        if keyname == "Right":
            self.player.rotate(math.pi/12)

        if keyname not in self.pressed_keys:
            self.pressed_keys.append(keyname)

    def on_keyrelease(self, keyname):

        if keyname in self.pressed_keys:
            self.pressed_keys.remove(keyname)

    def pressed(self, key):

        return key in self.pressed_keys

    def tick(self):

        if self.pressed("space") and not self.player.hook:
            self.player.find_target(self.get_circles())

        if not self.pressed("space"):
            self.player.reset_hook()

        self.player.move()
        return True

    def get_circles_in_screen(self, screen):

        """
        Return circles in given screen, creating them if they did not exist
        """

        try:

            return self.circles[screen]

        except IndexError:

            # Where to start placing circles
            offset = len(self.circles)

            # Maximal and minimal radis
            max_r = 1/(10*CIRCLES_PER_SCREEN)
            min_r = 0.05

            circles = []
            for i in range(CIRCLES_PER_SCREEN):
                r = random.uniform(min_r, max_r)
                # Random x position, but ensuring we do not overflow
                x = random.uniform(r, 1 - r)
                # offset + nth screen portion + some margin between circles
                y = offset + i*1/CIRCLES_PER_SCREEN + 1/(2*CIRCLES_PER_SCREEN)
                circles.append(Circle(x, y, r))

            self.circles.append(circles)
            return circles

    def get_circles(self):

        """Return circles in neighbouring screens"""

        screen = self.player.screen

        # At most, we display circles from 3 screens
        return (self.get_circles_in_screen(screen-1) +
                self.get_circles_in_screen(screen) +
                self.get_circles_in_screen(screen+1))


class GameScene:

    def __init__(self, game, cr, scene):

        self.game = game
        self.player = self.game.player
        self.cr = cr
        self.scene = scene

    def player_scene(self):

        return self.player.scene(self.cr)

    def draw(self):

        self.cr.set_source_rgba(0.1, 0.1, 0.1, 1)
        self.cr.paint()

        with self.scene.scale():

            self.draw_safe_area()
            self.draw_player()

            with self.player_scene().scale():
                self.draw_circles()
                self.draw_target()

    def draw_safe_area(self):

        px, py = self.player.position
        self.cr.set_source_rgba(0.11, 0.11, 0.11, 1)  # Slightly darker
        self.cr.rectangle(-px+0.5, -1, 1, 3)
        self.cr.fill()

    def draw_player(self):

        self.player.draw(self.cr)

    def draw_target(self):

        target = self.player.target()
        if self.player.hook:
            target.draw_zone(self.cr, self.player.dist_circle(target))

    def draw_circles(self):

        for circle in self.game.get_circles():
            circle.draw(self.cr)
