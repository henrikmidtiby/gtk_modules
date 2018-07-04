import gi
gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
gi.require_version('GstVideo', '1.0')
gi.require_foreign('cairo')
from gi.repository import Gst, GObject, Gtk, GdkX11, GstVideo, GLib
# Needed for window.get_xid(), xvimagesink.set_window_handle(), respectively:
Gst.init()


class Video:
    def __init__(self, draw_area, draw_signal):
        self.draw_area = draw_area
        self.draw_signal = draw_signal
        self.pipeline = None
        self.bus = None
        self.duration = None
        self.player_paused = False
        self.is_player_active = False
        self.last_play_rate_state = 'normal'
        self.playback_button = Gtk.Button()
        self.play_image = self._set_button_image(self.playback_button, 'gtk-media-play')
        self.pause_image = Gtk.Image.new_from_icon_name('gtk-media-pause', Gtk.IconSize.MENU)
        self.stop_button = Gtk.Button()
        self._set_button_image(self.stop_button, 'gtk-media-stop')
        self.next_frame_button = Gtk.Button()
        self._set_button_image(self.next_frame_button, 'gtk-media-next')
        self.normal_forward_button = Gtk.RadioButton.new_from_widget(None)
        self.normal_forward_button.set_label('x1')
        self.normal_forward_button.set_mode(False)
        self.fast_forward_button = Gtk.RadioButton.new_from_widget(self.normal_forward_button)
        self.fast_forward_button.set_label('x5')
        self.fast_forward_button.set_mode(False)
        self.slow_forward_button = Gtk.RadioButton.new_from_widget(self.normal_forward_button)
        self.slow_forward_button.set_label('x1/2')
        self.slow_forward_button.set_mode(False)
        self.frame_slider = Gtk.Scale()
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._setup_controls()

    def _setup_controls(self):
        self.playback_button.connect('clicked', self._toggle_player_playback)
        self.playback_button.set_sensitive(False)
        self.stop_button.connect('clicked', self._stop)
        self.stop_button.set_sensitive(False)
        self.normal_forward_button.connect('toggled', self._change_speed, 'normal')
        self.fast_forward_button.connect('toggled', self._change_speed, 'fast')
        self.slow_forward_button.connect('toggled', self._change_speed, 'slow')
        self.next_frame_button.connect('clicked', self._next_frame)
        self.frame_slider.connect('value-changed', self._frame_slider_change)
        self._enable_control(False)
        self.controls = Gtk.Box(spacing=1)
        self.controls.pack_start(self.playback_button, False, False, 0)
        self.controls.pack_start(self.stop_button, False, False, 0)
        self.controls.pack_start(self.normal_forward_button, False, False, 0)
        self.controls.pack_start(self.slow_forward_button, False, False, 0)
        self.controls.pack_start(self.fast_forward_button, False, False, 0)
        self.controls.pack_start(self.next_frame_button, False, False, 0)
        self.controls.pack_start(self.frame_slider, True, True, 10)

    def open_video(self, video_file):
        uri = 'file://' + video_file
        self.pipeline = Gst.parse_launch('playbin uri=' + uri)
        cairo_overlay_bin = self._setup_gstreamer()
        self.bus = self._setup_bus()
        self.pipeline.set_property('video-sink', cairo_overlay_bin)
        self.play()
        self.pause()

    def _setup_bus(self):
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect('message::eos', self.on_eos)
        bus.connect('message::error', self.on_error)
        bus.enable_sync_message_emission()
        bus.connect('sync-message::element', self._on_sync_message)
        return bus

    def _on_sync_message(self, bus, msg):
        if msg.get_structure().get_name() == 'prepare-window-handle':
            xid = self.draw_area.get_window().get_xid()
            msg.src.set_window_handle(xid)
            self.duration = self.pipeline.query_duration(Gst.Format.TIME)[1]
            video_length = self.duration * 1e-9
            adjustment = Gtk.Adjustment(value=0, lower=0, upper=video_length, step_increment=100, page_increment=100,
                                        page_size=100)
            self.frame_slider.set_adjustment(adjustment)
            self._add_marks_to_frame_slider(video_length)
            self._enable_buttons()

    def _setup_gstreamer(self):
        adaptor1 = Gst.ElementFactory.make('videoconvert', 'adaptor1')
        overlay = Gst.ElementFactory.make('cairooverlay', 'overlay')
        adaptor2 = Gst.ElementFactory.make('videoconvert', 'adaptor2')
        self.sink = Gst.ElementFactory.make('xvimagesink', 'cairo_sink')
        cairo_overlay_bin = Gst.Bin.new('cairo_overlay_bin')
        cairo_overlay_bin.add(adaptor1)
        cairo_overlay_bin.add(overlay)
        cairo_overlay_bin.add(adaptor2)
        cairo_overlay_bin.add(self.sink)
        adaptor1.link(overlay)
        overlay.link(adaptor2)
        adaptor2.link(self.sink)
        pad = Gst.Element.get_static_pad(adaptor1, 'sink')
        ghost_pad = Gst.GhostPad.new('sink', pad)
        ghost_pad.set_active(True)
        cairo_overlay_bin.add_pad(ghost_pad)
        overlay.connect('draw', self._on_draw)
        return cairo_overlay_bin

    def _on_draw(self, _overlay, context, _timestamp, _duration):
        position = self.pipeline.query_position(Gst.Format.TIME)[1]
        self.draw_signal.emit('video_draw', context, position)

    def _move_frame_slider(self):
        while self.is_player_active and not self.player_paused:
            time = self.pipeline.query_position(Gst.Format.TIME)[1] * 1e-9
            self.frame_slider.set_value(time)
            yield True
        yield False

    @staticmethod
    def _set_button_image(button, image_string):
        image = Gtk.Image.new_from_icon_name(image_string, Gtk.IconSize.MENU)
        button.set_image(image)
        return image

    def _add_marks_to_frame_slider(self, length):
        self.frame_slider.clear_marks()
        step = int(length / 10)
        for time in range(0, int(length)-step, step):
            self.frame_slider.add_mark(time, Gtk.PositionType.BOTTOM, str(time))

    def _toggle_player_playback(self, widget, data=None):
        if not self.is_player_active:
            self._play()
        elif self.player_paused:
            self._play()
        else:
            self._pause()

    def _stop(self, widget, data=None):
        self.pipeline.set_state(Gst.State.READY)
        self.is_player_active = False
        self.playback_button.set_image(self.play_image)
        self.frame_slider.set_value(0)
        self.frame_slider.set_sensitive(False)
        self.next_frame_button.set_sensitive(False)

    def _play(self):
        self.pipeline.set_state(Gst.State.PLAYING)
        self.player_paused = False
        image = self.pause_image
        self._enable_control(False)
        GLib.idle_add(self._move_frame_slider().__next__)
        self.playback_button.set_image(image)
        self.is_player_active = True

    def _pause(self):
        self.pipeline.set_state(Gst.State.PAUSED)
        self.player_paused = True
        image = self.play_image
        self._enable_control()
        self.playback_button.set_image(image)
        self.is_player_active = True

    def _realized(self, widget, data=None):
        pass

    def _enable_buttons(self):
        self.playback_button.set_sensitive(True)
        self.stop_button.set_sensitive(True)
        self._enable_control()

    def _enable_control(self, enable=True):
        self.frame_slider.set_sensitive(enable)
        self.normal_forward_button.set_sensitive(enable)
        self.fast_forward_button.set_sensitive(enable)
        self.slow_forward_button.set_sensitive(enable)
        self.next_frame_button.set_sensitive(enable)

    def _frame_slider_change(self, adjustment, data=None):
        state = self.pipeline.get_state(Gst.State.PLAYING).state
        if state == Gst.State.PAUSED:
            time = adjustment.get_value()
            self.pipeline.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, time * Gst.SECOND)

    def play(self):
        self._play()

    def stop(self):
        self._stop(None)

    def pause(self):
        self._pause()

    def next_frame(self):
        self._next_frame(None)

    def fast_forward(self):
        self._change_speed(None, 'fast')

    def slow_forward(self):
        self._change_speed(None, 'slow')

    def _next_frame(self, widget, data=None):
        self.sink.send_event(Gst.Event.new_step(Gst.Format.BUFFERS, 1, 1, True, False))

    def _change_speed(self, widget, data=None):
        if data != self.last_play_rate_state:
            rate = 1
            position = self.pipeline.query_position(Gst.Format.TIME)[1]
            if data == 'fast' and self.fast_forward_button.get_active():
                rate = 5
            elif data == 'slow' and self.slow_forward_button.get_active():
                rate = 0.5
            self.sink.send_event(Gst.Event.new_seek(rate, Gst.Format.TIME, Gst.SeekFlags.FLUSH | Gst.SeekFlags.ACCURATE,
                                                    Gst.SeekType.SET, position, Gst.SeekType.NONE, 0))
        self.last_play_rate_state = data

    def clean_up(self):
        self.stop()

    def on_eos(self, bus, msg):
        print('on_eos(): seeking to start of video')
        self.pipeline.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, 0)

    def on_error(self, bus, msg):
        print('on_error():', msg.parse_error())


