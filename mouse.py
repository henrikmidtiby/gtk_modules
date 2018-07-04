from signals import MouseSignals
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class Mouse:
    def __init__(self):
        signals = MouseSignals()
        self.event_box = Gtk.EventBox()
        self.event_box.connect('button-press-event', self.press)
        self.event_box.connect('button-release-event', self.release)
        self.event_box.connect('motion_notify_event', self.move)

    def press(self, widget, event, data=None):
        print('press', event.x, event.y)

    def release(self, widget, event, data=None):
        print('release', event.x, event.y)

    def move(self, widget, event, data=None):
        print('move', event.x, event.y)
