import numpy as np
from gtk_modules import DrawSignals
import gi
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk


class VideoDrawHandler:
    def __init__(self, video_draw_signal):
        self.video_draw_signal = video_draw_signal
        self.signals = DrawSignals()
        self.signals.connect('point_draw', self.draw_point)
        self.signals.connect('line_draw', self.draw_line)
        self.signals.connect('line_draw_live', self.draw_line_live)
        self.signals.connect('box_draw', self.draw_box)
        self.signals.connect('box_draw_live', self.draw_box_live)
        self.points = []
        self.lines = []
        self.boxes = []
        self.temp_line = None
        self.temp_box = None
        self.color = Gdk.RGBA(1, 0, 0, 1)
        self.str_func = None
        self.point_size = 5
        self.line_thickness = 3

    def draw(self, event, context, position, draw_area_size, video_size):
        self.draw_text(context, position, draw_area_size, video_size)
        self.draw_points(context, position, draw_area_size, video_size)
        self.draw_lines(context, position, draw_area_size, video_size)
        self.draw_boxes(context, position, draw_area_size, video_size)
        if self.temp_line is not None:
            self.draw_temp_line(context, position, draw_area_size, video_size)
        if self.temp_box is not None:
            self.draw_temp_box(context, position, draw_area_size, video_size)

    def draw_text(self, context, position, draw_area_size, video_size):
        if self.str_func is not None:
            text = self.str_func(position)
            if text:
                size_scale = np.mean(np.array(video_size) / np.array(draw_area_size))
                context.set_source_rgba(*Gdk.RGBA(0, 0, 0, 0.5))
                context.rectangle(0, 0, (10+len(text)*10) * size_scale, 20 * size_scale)
                context.fill()
                context.set_source_rgba(*self.color)
                context.move_to(5 * size_scale, 15 * size_scale)
                context.set_font_size(15 * size_scale)
                context.show_text(text)

    def draw_points(self, context, position, draw_area_size, video_size):
        for p, c, hide in self.points:
            if p[4] == position and not hide:
                self._draw_point(p, c, context, draw_area_size, video_size)

    def _draw_point(self, point, color, context, draw_area_size, video_size):
        scale = np.mean(np.array(video_size) / point[2:4])
        new_p = point[:2] * scale
        size_scale = np.mean(np.array(video_size) / np.array(draw_area_size))
        size = self.point_size * size_scale
        context.set_source_rgba(*color)
        context.arc(*new_p, size, 0, 2*np.pi)
        context.fill()

    def draw_point(self, event, data):
        self.video_draw_signal()

    def draw_temp_line(self, context, position, draw_area_size, video_size):
        if self.temp_line[6] == position:
            self._draw_line(self.temp_line, self.color, context, draw_area_size, video_size)

    def _draw_line(self, line, color, context, draw_area_size, video_size):
        scale = np.mean(np.array(video_size) / line[4:6])
        new_l = line[:4] * scale
        size_scale = np.mean(np.array(video_size) / np.array(draw_area_size))
        size = self.line_thickness * size_scale
        context.set_line_width(size)
        context.set_source_rgba(*color)
        context.move_to(*new_l[:2])
        context.line_to(*new_l[2:4])
        context.stroke()

    def draw_line(self, event, data):
        self.temp_line = None
        self.video_draw_signal()

    def draw_lines(self, context, position, draw_area_size, video_size):
        for l, c, hide in self.lines:
            if l[6] == position and not hide:
                self._draw_line(l, c, context, draw_area_size, video_size)

    def draw_line_live(self, event, x1, y1, x2, y2, width, height, position):
        self.temp_line = np.array([x1, y1, x2, y2, width, height, position])
        self.video_draw_signal()

    def draw_temp_box(self, context, position, draw_area_size, video_size):
        if self.temp_box[6] == position:
            self._draw_box(self.temp_box, self.color, context, draw_area_size, video_size)

    def _draw_box(self, box, color, context, draw_area_size, video_size):
        scale = np.mean(np.array(video_size) / box[4:6])
        new_l = box[:4] * scale
        size_scale = np.mean(np.array(video_size) / np.array(draw_area_size))
        size = self.line_thickness * size_scale
        context.set_line_width(size)
        context.set_source_rgba(*color)
        context.move_to(*new_l[:2])
        context.line_to(new_l[0], new_l[3])
        context.line_to(*new_l[2:4])
        context.line_to(new_l[2], new_l[1])
        context.line_to(*new_l[:2])
        context.stroke()

    def draw_box(self, event, data):
        self.temp_box = None
        self.video_draw_signal()

    def draw_boxes(self, context, position, draw_area_size, video_size):
        for box, color in self.boxes:
            if box[6] == position:
                self._draw_box(box, color, context, draw_area_size, video_size)

    def draw_box_live(self, event, x1, y1, x2, y2, width, height, position):
        self.temp_box = np.array([x1, y1, x2, y2, width, height, position])
        self.video_draw_signal()
