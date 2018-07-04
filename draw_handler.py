import math
import cairo
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


class DrawHandler:
    def __init__(self):
        pass

    def test_draw(self, video_draw, context, position):
        x, y = self.pos(position)
        context.set_source_rgba(1, 0, 0, 1)
        context.arc(x, y, 10, 0, 6.28)
        context.fill()

    def pos(self, t):
        t = t / 1e9
        x = math.cos(t) * 50 + 70
        y = math.sin(t) * 50 + 70
        return x, y

    def draw_point_live(self, x, y, radius=None):
        pass

    def draw_box_live(self, x1, y1, x2, y2, line_width=None):
        pass

    def draw_line_live(self, x1, y1, x2, y2, line_width=None):
        pass

    def change_default_color(self, color):
        pass

    def change_default_width(self, line_width):
        pass

    def change_default_point_radius(self, radius):
        pass
