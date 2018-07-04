import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject


class DrawSignals(GObject.GObject):
    __gsignals__ = {'video_draw': (GObject.SIGNAL_RUN_LAST, None, (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT)),
                    'image_draw': (GObject.SIGNAL_RUN_LAST, None, (str,))}

    def __init__(self):
        super().__init__()


class MouseSignals(GObject.GObject):
    __gsignals__ = {'mouse_press': (GObject.SIGNAL_RUN_LAST, None, (float, float)),
                    'mouse_realise': (GObject.SIGNAL_RUN_LAST, None, (float, float)),
                    'mouse_move': (GObject.SIGNAL_RUN_LAST, None, (float, float))}

    def __init__(self):
        super().__init__()

