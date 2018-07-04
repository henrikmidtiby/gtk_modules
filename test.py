from collections import OrderedDict
from menu import Menu
from dialogs import ProgressDialog, FileDialog
from video import Video
from draw_handler import DrawHandler
from mouse import Mouse
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio


class Test(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='org.test',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.menu = Menu(self)
        file = OrderedDict()
        file.update({'_New': ('new', '&lt;Primary&gt;n', self.on_new)})
        file.update({'_Open': ('open', '&lt;Primary&gt;o', self.on_open)})
        file.update({'_Quit': ('quit', '&lt;Primary&gt;q', self.on_quit)})
        self.menu.add_sub_menu('_File', file)
        about = OrderedDict()
        about.update({'_Help': ('help', None, self.on_help, False)})
        self.menu.add_sub_menu('_About', about)
        self.mouse = Mouse()
        self.video = Video()
        self.draw_handler = DrawHandler()
        self.video.signals.connect('video_draw', self.draw_handler.test_draw)
        self.window = None

    def do_startup(self):
        Gtk.Application.do_startup(self)
        self.menu.make_actions()

    def do_activate(self):
        self.menu.activate_menu()
        self.window = Gtk.ApplicationWindow()
        self.window.set_title('Multi Image Annotator')
        self.window.set_application(self)
        self.window.connect('delete_event', self.on_quit)
        self.window.set_size_request(500, 500)
        vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.mouse.event_box.add(self.video.draw_area)
        vertical_box.pack_start(self.mouse.event_box, True, True, 0)
        vertical_box.pack_start(self.video.controls, False, False, 0)
        self.window.add(vertical_box)
        self.window.show_all()

    def on_about(self, *_):
        dialog = ProgressDialog(self.window, 'test', 10)
        progress_updater = dialog.update_progress()
        for x in progress_updater:
            print(x)

    def on_open(self, *_):
        dialog = FileDialog(self.window, 'File', 'open')
        dialog.add_mime_filter('python', 'text/x-python')
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            file = dialog.get_filename()
            dialog.destroy()
            self.video.open_video(file)
        else:
            dialog.destroy()

    def on_new(self, *_):
        self.video.play()

    def on_help(self, *_):
        self.video.pause()

    def on_quit(self, *_):
        self.quit()


if __name__ == '__main__':
    app = Test()
    app.run()
