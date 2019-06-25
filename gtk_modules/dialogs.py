import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import pathlib


class Dialog(Gtk.Dialog):
    def __init__(self, parent, header, response=None, size=None):
        Gtk.Dialog.__init__(self, title=header, transient_for=parent)
        if response == 'no_yes':
            response = (Gtk.STOCK_NO, Gtk.ResponseType.NO, Gtk.STOCK_YES, Gtk.ResponseType.YES)
            self.add_buttons(*response)
        elif response == 'cancel_ok':
            response = (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)
            self.add_buttons(*response)
        elif response == 'close':
            response = (Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
            self.add_buttons(*response)
        if size is not None:
            self.set_default_size(*size)
        self.box = self.get_content_area()


class ProgressDialog(Dialog):
    def __init__(self, parent, header, max_k):
        super().__init__(parent, header, size=(300, 50))
        self.max_k = max_k
        label = Gtk.Label(label=header)
        self.progress_bar = Gtk.ProgressBar()
        self.box.add(label)
        self.box.add(self.progress_bar)
        self.show_all()

    def update_progress(self):
        for k in range(self.max_k):
            fraction = k / self.max_k
            self.progress_bar.set_fraction(fraction)
            yield True
        self.close()
        yield False


class FileDialog(Gtk.FileChooserDialog):
    def __init__(self, parent, header, action=None, current_name=None, current_folder=None):
        do_overwrite_confirmation = False
        select_multiple = False
        if action == 'select_folder':
            action = Gtk.FileChooserAction.SELECT_FOLDER
            response = (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        elif action == 'save':
            action = Gtk.FileChooserAction.SAVE
            response = (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE_AS, Gtk.ResponseType.OK)
            do_overwrite_confirmation = True
        elif action == 'open_multiple':
            action = Gtk.FileChooserAction.OPEN
            response = (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
            select_multiple = True
        else:
            action = Gtk.FileChooserAction.OPEN
            response = (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        super().__init__(title=header, transient_for=parent, action=action)
        self.add_buttons(*response)
        self.set_do_overwrite_confirmation(do_overwrite_confirmation)
        self.set_select_multiple(select_multiple)
        if current_folder is not None:
            p = pathlib.Path(current_folder)
            self.set_current_folder(str(p.parent))
        if current_name is not None:
            self.set_current_name(current_name)
        self.add_pattern_filter('Any files', '*')

    def add_mime_filter(self, name, mime_type):
        file_filter = Gtk.FileFilter()
        file_filter.set_name(name)
        file_filter.add_mime_type(mime_type)
        self.add_filter(file_filter)

    def add_pattern_filter(self, name, pattern):
        file_filter = Gtk.FileFilter()
        file_filter.set_name(name)
        file_filter.add_pattern(pattern)
        self.add_filter(file_filter)
