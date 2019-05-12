import math
import cairo
import contextlib
from .scene import Scene
from .player import Player
from .circle import Circle


class Game:

    def __init__(self, fps):

        self.size = (0, 0)
        self.scene_params = (0, 0, 0, 0)
        self._circle_generator = Circle.generator(2, 0.2)
        self.circles = [next(self._circle_generator)]
        self.buffers = []
        self.pressed_keys = []
        self.player = Player(0.5, 0, 0,
                             size=0.02,
                             range=0.8,
                             speed=1/fps)

    def _apply_scene_context(self, cr):

        """Apply scene parameters to the given Cairo context"""

        tr_x, tr_y, sc_x, sc_y = self.scene_params
        cr.translate(tr_x, tr_y)  # Centering
        cr.scale(sc_x, sc_y)  # 1:1 aspect ratio + upward vertical axis
        cr.translate(0, -1)  # Set 0,0 to bottom left

    def get_scene(self, cr):

        return GameScene(self, cr, Scene(cr, self._apply_scene_context))

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

        while len(self.circles) < screen + 1:
            self.circles.append(next(self._circle_generator))
        return self.circles[screen]

    def get_circles(self):

        """Return circles in neighbouring screens"""

        screen = self.player.screen

        # At most, we display circles from 3 screens
        return (self.get_circles_in_screen(screen-1) +
                self.get_circles_in_screen(screen) +
                self.get_circles_in_screen(screen+1))

    def get_buffer(self, screen):

        for index in range(len(self.buffers), screen + 2):
            self.buffers.append((index, self.new_buffer()))
        return self.buffers[screen]

    def buffer_context(self, buffer):

        return Scene(cairo.Context(buffer), self._apply_scene_context).scale

    def new_buffer(self):

        buffer = cairo.ImageSurface(cairo.FORMAT_ARGB32, *self.size)
        if False:
            with self.buffer_context(buffer) as cr:
                cr.set_source_rgba(0.2, 0.2, 0.2, 1)
                cr.rectangle(0.1, 0.1, 0.9, 0.9)
                cr.fill()
                cr.set_source_rgba(0.9, 0.9, 0.9, 1)
                cr.translate(0.5, 0.5)
                cr.scale(1, -1)
                cr.set_font_size(0.1)
                cr.show_text(str(len(self.buffers)))
        return buffer

    def get_buffers(self):

        screen = self.player.screen
        return [self.get_buffer(screen), self.get_buffer(screen + 1)]

    def invalidate_buffers(self):

        self.buffers = [(screen, None) for screen, _ in self.buffers]


class GameScene:

    def __init__(self, game, cr, scene):

        self.game = game
        self.player = self.game.player

        self.cr = cr
        self.scene = scene

    @contextlib.contextmanager
    def player_scene(self):
        with self.scene.scale as cr1:
            with self.player.scene(cr1).scale as cr2:
                yield cr2

    def draw(self):

        self.cr.set_source_rgba(0.1, 0.1, 0.1, 1)
        self.cr.paint()

        with self.scene.scale:
            self.draw_safe_area()

        self.draw_buffers()

        with self.player_scene():
            self.draw_circles()
            self.draw_target()
            self.draw_player()

    def draw_buffers(self):

        for screen, buffer in self.game.get_buffers():

            if buffer is not None:

                with self.game.buffer_context(buffer) as cr:
                    dy = screen - 0.5
                    if 1 > self.player.y - dy > 0:
                        cr.translate(0, -dy)
                        self.player.draw_trail(cr)

                px, py = self.player.position
                dx, dy = self.scene.dist(px - 0.5, py - screen)
                self.cr.set_source_surface(buffer, -dx, -dy)
                self.cr.paint()

    def draw_safe_area(self):

        px, py = self.player.position
        self.cr.set_source_rgba(0.12, 0.12, 0.12, 1)  # Slightly darker
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
