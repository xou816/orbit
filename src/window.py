# window.py
#
# Copyright 2019 Alexandre Trendel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gtk, Gdk, GObject
from .game import Game


FPS_TH = 60


@Gtk.Template(resource_path='/dev/alextren/Orbit/window.ui')
class OrbitWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'OrbitWindow'

    canvas = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.canvas.add_events(Gdk.EventMask.SCROLL_MASK |
                               Gdk.EventMask.BUTTON_PRESS_MASK |
                               Gdk.EventMask.BUTTON_RELEASE_MASK |
                               Gdk.EventMask.POINTER_MOTION_MASK |
                               Gdk.EventMask.POINTER_MOTION_HINT_MASK |
                               Gdk.EventMask.KEY_PRESS_MASK |
                               Gdk.EventMask.KEY_RELEASE_MASK)
        self.game = Game(FPS_TH)
        GObject.timeout_add(1000//FPS_TH, self.main)

    def main(self):

        proceed = self.game.tick()
        self.canvas.queue_draw()
        return proceed

    @Gtk.Template.Callback()
    def on_draw(self, win, cr):

        self.game.get_scene(cr).draw()

    @Gtk.Template.Callback()
    def on_configure(self, widget, event, data=None):

        self.game.size = self.canvas_size()
        self.game.scene_params = self.scene_params()
        return False

    @Gtk.Template.Callback()
    def on_keypress(self, widget, event):

        keyname = Gdk.keyval_name(event.keyval)
        self.game.on_keypress(keyname)

    @Gtk.Template.Callback()
    def on_keyrelease(self, widget, event):

        keyname = Gdk.keyval_name(event.keyval)
        self.game.on_keyrelease(keyname)

    def canvas_size(self):

        return (self.canvas.get_allocated_width(),
                self.canvas.get_allocated_height())

    def scene_params(self):

        """Compute scaling and translation parameters"""

        w, h = self.canvas_size()
        mn = min(w, h)
        mx = max(w, h)
        # Booleans to determine whether or not to translate along x/y
        tr_x, tr_y = int(mx == w), int(mx == h)
        return tr_x*(mx-mn)/2, tr_y*(mx-mn)/2, mn, -mn

