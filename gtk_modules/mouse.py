from gtk_modules import MouseSignals
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


class Mouse:
    def __init__(self, event_box=None):
        if event_box is None:
            self.event_box = Gtk.EventBox()
        else:
            self.event_box = event_box
        self.signals = MouseSignals()
        self.event_box.connect('realize', self._realize)
        self.event_box.connect('button-press-event', self.press)
        self.event_box.connect('button-release-event', self.release)
        self.event_box.connect('motion_notify_event', self.move)
        self.size = None

    def _realize(self, widget):
        draw_area = widget.get_child()
        draw_area.connect('size-allocate', self._get_size)

    def _get_size(self, _, allocation):
        self.size = (allocation.width, allocation.height)

    def press(self, _, event):
        if event.button == 1:
            self.signals.emit('left_mouse_press', event.x, event.y, *self.size)
        elif event.button == 2:
            self.signals.emit('middle_mouse_press', event.x, event.y, *self.size)
        elif event.button == 3:
            self.signals.emit('right_mouse_press', event.x, event.y, *self.size)

    def release(self, _, event):
        if event.button == 1:
            self.signals.emit('left_mouse_release', event.x, event.y)
        elif event.button == 2:
            self.signals.emit('middle_mouse_release', event.x, event.y)
        elif event.button == 3:
            self.signals.emit('right_mouse_release', event.x, event.y)

    def move(self, _, event):
        if event.state & Gdk.ModifierType.BUTTON1_MASK:
            self.signals.emit('left_mouse_move', event.x, event.y)
        elif event.state & Gdk.ModifierType.BUTTON2_MASK:
            self.signals.emit('middle_mouse_move', event.x, event.y)
        elif event.state & Gdk.ModifierType.BUTTON3_MASK:
            self.signals.emit('right_mouse_move', event.x, event.y)
