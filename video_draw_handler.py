import numpy as np
from signals import DrawSignals


class DrawHandler:
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

    def draw(self, event, context, position, draw_area_size, video_size):
        self.draw_points(context, position, draw_area_size, video_size)
        self.draw_lines(context, position, draw_area_size, video_size)
        self.draw_boxes(context, position, draw_area_size, video_size)
        if self.temp_line is not None:
            self.draw_temp_line(context, position, draw_area_size, video_size)
        if self.temp_box is not None:
            self.draw_temp_box(context, position, draw_area_size, video_size)

    def draw_points(self, context, position, draw_area_size, video_size):
        for p in self.points:
            if p[4] == position:
                self._draw_point(p, context, draw_area_size, video_size)

    @staticmethod
    def _draw_point(point, context, draw_area_size, video_size):
        scale = np.mean(np.array(video_size) / point[2:4])
        new_p = point[:2] * scale
        size_scale = np.mean(np.array(video_size) / np.array(draw_area_size))
        size = 10 * size_scale
        context.set_source_rgba(1, 0, 0, 1)
        context.arc(*new_p, size, 0, 6.28)
        context.fill()

    def draw_point(self, event, x, y, width, height, position):
        self.points.append(np.array([x, y, width, height, position]))
        self.video_draw_signal()

    def draw_temp_line(self, context, position, draw_area_size, video_size):
        if self.temp_line[6] == position:
            self._draw_line(self.temp_line, context, draw_area_size, video_size)

    @staticmethod
    def _draw_line(line, context, draw_area_size, video_size):
        scale = np.mean(np.array(video_size) / line[4:6])
        new_l = line[:4] * scale
        size_scale = np.mean(np.array(video_size) / np.array(draw_area_size))
        size = 3 * size_scale
        context.set_line_width(size)
        context.set_source_rgba(1, 0, 0, 1)
        context.move_to(*new_l[:2])
        context.line_to(*new_l[2:4])
        context.stroke()

    def draw_line(self, event, x1, y1, x2, y2, width, height, position):
        self.temp_line = None
        self.lines.append(np.array([x1, y1, x2, y2, width, height, position]))
        self.video_draw_signal()

    def draw_lines(self, context, position, draw_area_size, video_size):
        for l in self.lines:
            if l[6] == position:
                self._draw_line(l, context, draw_area_size, video_size)

    def draw_line_live(self, event, x1, y1, x2, y2, width, height, position):
        self.temp_line = np.array([x1, y1, x2, y2, width, height, position])
        self.video_draw_signal()

    def draw_temp_box(self, context, position, draw_area_size, video_size):
        if self.temp_box[6] == position:
            self._draw_box(self.temp_box, context, draw_area_size, video_size)

    @staticmethod
    def _draw_box(box, context, draw_area_size, video_size):
        scale = np.mean(np.array(video_size) / box[4:6])
        new_l = box[:4] * scale
        size_scale = np.mean(np.array(video_size) / np.array(draw_area_size))
        size = 3 * size_scale
        context.set_line_width(size)
        context.set_source_rgba(1, 0, 0, 1)
        context.move_to(*new_l[:2])
        context.line_to(new_l[0], new_l[3])
        context.line_to(*new_l[2:4])
        context.line_to(new_l[2], new_l[1])
        context.line_to(*new_l[:2])
        context.stroke()

    def draw_box(self, event, x1, y1, x2, y2, width, height, position):
        self.temp_box = None
        self.boxes.append(np.array([x1, y1, x2, y2, width, height, position]))
        self.video_draw_signal()

    def draw_boxes(self, context, position, draw_area_size, video_size):
        for box in self.boxes:
            if box[6] == position:
                self._draw_box(box, context, draw_area_size, video_size)

    def draw_box_live(self, event, x1, y1, x2, y2, width, height, position):
        self.temp_box = np.array([x1, y1, x2, y2, width, height, position])
        self.video_draw_signal()

    def change_default_color(self, color):
        pass

    def change_default_width(self, line_width):
        pass

    def change_default_point_radius(self, radius):
        pass
