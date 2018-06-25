import vlc
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib


class Video:
    def __init__(self):
        self.player_paused = False
        self.is_player_active = False
        self.playback_button = Gtk.Button()
        self.play_image = self._set_button_image(self.playback_button, 'gtk-media-play')
        self.pause_image = Gtk.Image.new_from_icon_name('gtk-media-pause', Gtk.IconSize.MENU)
        self.stop_button = Gtk.Button()
        self._set_button_image(self.stop_button, 'gtk-media-stop')
        self.next_frame_button = Gtk.Button()
        self._set_button_image(self.next_frame_button, 'gtk-media-next')
        self.fast_forward_button = Gtk.ToggleButton()
        self.fast_forward_button.set_label('x5')
        self.slow_forward_button = Gtk.ToggleButton()
        self.slow_forward_button.set_label('x1/2')
        self.frame_slider = Gtk.Scale()
        self.video_area = Gtk.DrawingArea()
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.vlcInstance = vlc.Instance('--no-xlib')
        self.player = self.vlcInstance.media_player_new()
        self._setup()

    def _move_frame_slider(self):
        while self.is_player_active and not self.player_paused:
            time = self.player.get_time() / 1000
            self.frame_slider.set_value(time)
            yield True
        yield False

    @staticmethod
    def _set_button_image(button, image_string):
        image = Gtk.Image.new_from_icon_name(image_string, Gtk.IconSize.MENU)
        button.set_image(image)
        return image

    def _setup(self):
        self.playback_button.connect('clicked', self._toggle_player_playback)
        self.playback_button.set_sensitive(False)
        self.stop_button.connect('clicked', self._stop)
        self.stop_button.set_sensitive(False)
        self.fast_forward_button.connect('toggled', self._fast_forward)
        self.fast_forward_button.set_sensitive(False)
        self.slow_forward_button.connect('toggled', self._slow_forward)
        self.slow_forward_button.set_sensitive(False)
        self.next_frame_button.connect('clicked', self._next_frame)
        self.next_frame_button.set_sensitive(False)
        self.frame_slider.connect('value-changed', self._frame_slider_change)
        self.frame_slider.set_sensitive(False)
        self.video_area.set_size_request(300, 300)
        self.video_area.connect('realize', self._realized)
        self.controls = Gtk.Box(spacing=1)
        self.controls.pack_start(self.playback_button, False, False, 0)
        self.controls.pack_start(self.stop_button, False, False, 0)
        self.controls.pack_start(self.slow_forward_button, False, False, 0)
        self.controls.pack_start(self.fast_forward_button, False, False, 0)
        self.controls.pack_start(self.next_frame_button, False, False, 0)
        self.controls.pack_start(self.frame_slider, True, True, 10)

    def _add_marks_to_frame_slider(self, length):
        self.frame_slider.clear_marks()
        step = int(length / 10)
        for time in range(0, int(length)-step, step):
            self.frame_slider.add_mark(time, Gtk.PositionType.BOTTOM, str(time))

    def _stop(self, widget, data=None):
        self.player.stop()
        self.is_player_active = False
        self.playback_button.set_image(self.play_image)
        self.frame_slider.set_value(0)
        self.frame_slider.set_sensitive(False)
        self.next_frame_button.set_sensitive(False)

    def _toggle_player_playback(self, widget, data=None):
        if not self.is_player_active:
            self._play()
        elif self.player_paused:
            self._play()
        else:
            self._pause()

    def _play(self):
        self.player.play()
        self.player_paused = False
        image = self.pause_image
        self.frame_slider.set_sensitive(False)
        self.next_frame_button.set_sensitive(False)
        GLib.idle_add(self._move_frame_slider().__next__)
        self.playback_button.set_image(image)
        self.is_player_active = True

    def _pause(self):
        self.player.pause()
        self.player_paused = True
        image = self.play_image
        self.frame_slider.set_sensitive(True)
        self.next_frame_button.set_sensitive(True)
        self.playback_button.set_image(image)
        self.is_player_active = True

    def _realized(self, widget, data=None):
        win_id = widget.get_window().get_xid()
        self.player.set_xwindow(win_id)

    def set_video_file(self, video_file):
        self.player.set_mrl(video_file)
        media = self.player.get_media()
        media.parse()
        video_length = media.get_duration() / 1000
        adjustment = Gtk.Adjustment(value=0, lower=0, upper=video_length, step_increment=100, page_increment=100, page_size=100)
        self.frame_slider.set_adjustment(adjustment)
        self._add_marks_to_frame_slider(video_length)
        self._enable_buttons()

    def _enable_buttons(self):
        self.playback_button.set_sensitive(True)
        self.stop_button.set_sensitive(True)
        self.fast_forward_button.set_sensitive(True)
        self.slow_forward_button.set_sensitive(True)

    def _frame_slider_change(self, adjustment, data=None):
        if not self.player.is_playing():
            time = adjustment.get_value()
            self.player.set_time(int(time * 1000))

    def play(self):
        self._play()

    def stop(self):
        self._stop(None)

    def pause(self):
        self._pause()

    def next_frame(self):
        self._next_frame(None)

    def fast_forward(self):
        self._fast_forward(None)

    def slow_forward(self):
        self._slow_forward(None)

    def _next_frame(self, widget, data=None):
        self.player.next_frame()

    def _fast_forward(self, widget, data=None):
        if self.fast_forward_button.get_active():
            self.slow_forward_button.set_active(False)
            self.player.set_rate(5)
        else:
            self.player.set_rate(1)

    def _slow_forward(self, widget, data=None):
        if self.slow_forward_button.get_active():
            self.fast_forward_button.set_active(False)
            self.player.set_rate(0.5)
        else:
            self.player.set_rate(1)

    def clean_up(self):
        self.stop()
        self.vlcInstance.release()


