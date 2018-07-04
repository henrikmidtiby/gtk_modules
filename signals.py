from gi.repository import GObject


class DrawSignals(GObject.GObject):
    __gsignals__ = {'video_draw': (GObject.SIGNAL_RUN_LAST, None, (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT)),
                    'image_draw': (GObject.SIGNAL_RUN_LAST, None, (str,))}

    def __init__(self):
        super().__init__()


class MouseSignals(GObject.GObject):
    __gsignals__ = {'left_mouse_press': (GObject.SIGNAL_RUN_LAST, None, (float, float)),
                    'left_mouse_realise': (GObject.SIGNAL_RUN_LAST, None, (float, float)),
                    'left_mouse_move': (GObject.SIGNAL_RUN_LAST, None, (float, float)),
                    'right_mouse_press': (GObject.SIGNAL_RUN_LAST, None, (float, float)),
                    'right_mouse_realise': (GObject.SIGNAL_RUN_LAST, None, (float, float)),
                    'right_mouse_move': (GObject.SIGNAL_RUN_LAST, None, (float, float)),
                    'middle_mouse_press': (GObject.SIGNAL_RUN_LAST, None, (float, float)),
                    'middle_mouse_realise': (GObject.SIGNAL_RUN_LAST, None, (float, float)),
                    'middle_mouse_move': (GObject.SIGNAL_RUN_LAST, None, (float, float))}

    def __init__(self):
        super().__init__()

