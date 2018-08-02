from gtk_modules.signals import DrawSignals
import cairo
import gi
gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
gi.require_version('GstVideo', '1.0')
gi.require_foreign('cairo')
from gi.repository import Gst, GObject, Gtk, GdkX11, GstVideo, GLib
# All Needed for window.get_xid(), xvimagesink.set_window_handle(), respectively.
Gst.init()


class Video:
    def __init__(self):
        self.overlay = None
        self.draw_area = Gtk.DrawingArea()
        self.draw_area.connect('size-allocate', self._get_size)
        self.event_box = Gtk.EventBox()
        self.event_box.add(self.draw_area)
        self.aspect_frame = Gtk.AspectFrame(label=None, xalign=0, yalign=0, ratio=1, obey_child=False)
        self.aspect_frame.add(self.event_box)
        self.aspect_frame.set_hexpand(False)
        self.aspect_frame.set_vexpand(False)
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.add(self.aspect_frame)
        self.size = (100, 100)
        self.video_size = None
        self.fps = None
        self.signals = DrawSignals()
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
        self.previous_frame_button = Gtk.Button()
        self._set_button_image(self.previous_frame_button, 'gtk-media-previous')
        self.normal_forward_button = Gtk.RadioButton.new_from_widget(None)
        self.normal_forward_button.set_label('x1')
        self.normal_forward_button.set_mode(False)
        self.fast_forward_button = Gtk.RadioButton.new_from_widget(self.normal_forward_button)
        self.fast_forward_button.set_label('x5')
        self.fast_forward_button.set_mode(False)
        self.slow_forward_button = Gtk.RadioButton.new_from_widget(self.normal_forward_button)
        self.slow_forward_button.set_label('x1/2')
        self.slow_forward_button.set_mode(False)
        self.zoom_spinner = Gtk.SpinButton()
        zoom_adjustment = Gtk.Adjustment(value=25, lower=10, upper=200, step_increment=5, page_increment=25, page_size=0)
        self.zoom_spinner.set_adjustment(zoom_adjustment)
        self.zoom_spinner.set_numeric(True)
        self.zoom_spinner.set_update_policy(Gtk.SpinButtonUpdatePolicy.IF_VALID)
        self.zoom_spinner.set_snap_to_ticks(True)
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
        self.previous_frame_button.connect('clicked', self._previous_frame)
        self.zoom_spinner.connect('value-changed', self._change_zoom)
        self.frame_slider.connect('value-changed', self._frame_slider_change)
        self._enable_control(False)
        self.controls = Gtk.Box(spacing=1)
        self.controls.pack_start(self.playback_button, False, False, 0)
        self.controls.pack_start(self.stop_button, False, False, 0)
        self.controls.pack_start(self.normal_forward_button, False, False, 0)
        self.controls.pack_start(self.slow_forward_button, False, False, 0)
        self.controls.pack_start(self.fast_forward_button, False, False, 0)
        self.controls.pack_start(self.previous_frame_button, False, False, 0)
        self.controls.pack_start(self.next_frame_button, False, False, 0)
        self.controls.pack_start(self.zoom_spinner, False, False, 0)
        self.controls.pack_start(self.frame_slider, True, True, 10)

    def open_video(self, video_file):
        uri = 'file://' + video_file
        self.pipeline = Gst.parse_launch('playbin uri=' + uri)
        cairo_overlay_bin = self._setup_gstreamer()
        self.bus = self._setup_bus()
        self.pipeline.set_property('video-sink', cairo_overlay_bin)
        self.play()
        self.pause()
        self.pipeline.get_state(5 * Gst.SECOND)
        pad = self.pipeline.emit('get-video-pad', 0)
        caps = pad.get_current_caps()
        _, width = caps.get_structure(0).get_int('width')
        _, height = caps.get_structure(0).get_int('height')
        _, fps_num, fps_den = caps.get_structure(0).get_fraction('framerate')
        self.fps = fps_num / fps_den
        self.video_size = (width, height)
        self.aspect_frame.set(xalign=0, yalign=0, ratio=width/height, obey_child=False)
        self.aspect_frame.set_size_request(width/4, height/4)

    def _setup_bus(self):
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect('message::eos', self.on_eos)
        bus.connect('message::error', self.on_error)
        bus.enable_sync_message_emission()
        bus.connect('sync-message::element', self._on_sync_message)
        return bus

    def _on_sync_message(self, _, msg):
        if msg.get_structure().get_name() == 'prepare-window-handle':
            xid = self.draw_area.get_window().get_xid()
            msg.src.set_window_handle(xid)
            self.duration = self.pipeline.query_duration(Gst.Format.TIME)[1]
            video_length = self.duration * 1e-9
            adjustment = Gtk.Adjustment(value=0, lower=0, upper=video_length,
                                        step_increment=1, page_increment=1, page_size=0)
            self.frame_slider.set_adjustment(adjustment)
            self._add_marks_to_frame_slider(video_length)
            self._enable_buttons()

    def _setup_gstreamer(self):
        adaptor1 = Gst.ElementFactory.make('videoconvert', 'adaptor1')
        self.overlay = Gst.ElementFactory.make('cairooverlay', 'overlay')
        adaptor2 = Gst.ElementFactory.make('videoconvert', 'adaptor2')
        self.sink = Gst.ElementFactory.make('xvimagesink', 'cairo_sink')
        cairo_overlay_bin = Gst.Bin.new('cairo_overlay_bin')
        cairo_overlay_bin.add(adaptor1)
        cairo_overlay_bin.add(self.overlay)
        cairo_overlay_bin.add(adaptor2)
        cairo_overlay_bin.add(self.sink)
        adaptor1.link(self.overlay)
        self.overlay.link(adaptor2)
        adaptor2.link(self.sink)
        pad = Gst.Element.get_static_pad(adaptor1, 'sink')
        ghost_pad = Gst.GhostPad.new('sink', pad)
        ghost_pad.set_active(True)
        cairo_overlay_bin.add_pad(ghost_pad)
        self.overlay.connect('draw', self._on_draw)
        return cairo_overlay_bin

    def get_position(self):
        position = self.pipeline.query_position(Gst.Format.TIME)[1]
        return position

    def _on_draw(self, _overlay, context, _timestamp, _duration):
        if self.video_size is not None:
            position = self.get_position()
            self.signals.emit('video_draw', context, position, self.size, self.video_size)

    def _get_size(self, _, allocation):
        self.size = (allocation.width, allocation.height)
        if self.video_size is not None:
            value = self.size[0] / self.video_size[0] * 100
            self.zoom_spinner.get_adjustment().set_value(value)

    def emit_draw_signal(self):
        if self.overlay:
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, *self.size)
            cr = cairo.Context(surface)
            self.overlay.emit('draw', cr, Gst.util_get_timestamp(), Gst.util_get_timestamp())
            time = self.frame_slider.get_adjustment().get_value()
            self.pipeline.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH | Gst.SeekFlags.ACCURATE, time * Gst.SECOND)

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

    def _toggle_player_playback(self, _):
        if not self.is_player_active:
            self._play()
        elif self.player_paused:
            self._play()
        else:
            self._pause()

    def toggle_player_playback(self):
        self._toggle_player_playback(None)

    def _stop(self, _):
        self.pipeline.set_state(Gst.State.READY)
        self.is_player_active = False
        self.playback_button.set_image(self.play_image)
        self.frame_slider.set_value(0)
        self.frame_slider.set_sensitive(False)
        self.next_frame_button.set_sensitive(False)
        self.previous_frame_button.set_sensitive(False)
        self.zoom_spinner.set_sensitive(False)

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
        self.previous_frame_button.set_sensitive(enable)

    def jump_to_position(self, position):
        self.frame_slider.get_adjustment().set_value(position)

    def _frame_slider_change(self, adjustment):
        state = self.pipeline.get_state(Gst.State.PLAYING).state
        if state == Gst.State.PAUSED:
            time = adjustment.get_value()
            self.pipeline.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH | Gst.SeekFlags.ACCURATE, time * Gst.SECOND)

    def _next_frame(self, _):
        time = self.frame_slider.get_adjustment().get_value() + 1/self.fps
        self.frame_slider.get_adjustment().set_value(time)

    def _previous_frame(self, _):
        time = self.frame_slider.get_adjustment().get_value() - 1/self.fps
        self.frame_slider.get_adjustment().set_value(time)

    def _change_zoom(self, widget):
        adjustment = widget.get_adjustment()
        value = adjustment.get_value()
        width = self.video_size[0] * value / 100
        height = self.video_size[1] * value / 100
        self.aspect_frame.set_size_request(width, height)

    def zoom_in(self):
        value = self.zoom_spinner.get_value() + 10
        self.zoom_spinner.set_value(value)

    def zoom_out(self):
        value = self.zoom_spinner.get_value() - 10
        self.zoom_spinner.set_value(value)

    def zoom_normal(self):
        self.zoom_spinner.set_value(100)

    def _change_speed(self, _, data=None):
        if data != self.last_play_rate_state:
            rate = 1
            position = self.get_position()
            if data == 'fast' and self.fast_forward_button.get_active():
                rate = 5
            elif data == 'slow' and self.slow_forward_button.get_active():
                rate = 0.5
            self.sink.send_event(Gst.Event.new_seek(rate, Gst.Format.TIME, Gst.SeekFlags.FLUSH | Gst.SeekFlags.ACCURATE,
                                                    Gst.SeekType.SET, position, Gst.SeekType.NONE, 0))
        self.last_play_rate_state = data

    def change_speed(self, data=None):
        if data == 'fast':
            self.fast_forward_button.set_active(True)
        elif data == 'slow':
            self.slow_forward_button.set_active(True)
        else:
            self.normal_forward_button.set_active(True)

    def play(self):
        self._play()

    def stop(self):
        self._stop(None)

    def pause(self):
        self._pause()

    def next_frame(self):
        self._next_frame(None)

    def previous_frame(self):
        self._previous_frame(None)

    def fast_forward(self):
        self._change_speed(None, 'fast')

    def slow_forward(self):
        self._change_speed(None, 'slow')

    def on_eos(self, _, __):
        self.pause()
        # print('on_eos(): seeking to start of video')
        # self.pipeline.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, 0)

    @staticmethod
    def on_error(_, msg):
        print('on_error():', msg.parse_error())
