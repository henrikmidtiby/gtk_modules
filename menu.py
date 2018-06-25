from collections import OrderedDict
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio


class Menu:
    def __init__(self, app_class):
        self._menu_items = OrderedDict()
        self._menu_action_dict = {}
        self._actions_dict = {}
        self.app_class = app_class

    def add_sub_menu(self, sub_name, label_ordered_dict):
        self._menu_items.update({sub_name: list(label_ordered_dict.keys())})
        self._menu_action_dict.update(label_ordered_dict)

    def enable_menu_item(self, label, enabled):
        action = self._actions_dict.get(label)
        action.set_enabled(enabled)

    def make_actions(self):
        for menu_item, action_tuple in self._menu_action_dict.items():
            action = self._make_action(self.app_class, *action_tuple)
            self._actions_dict.update({menu_item: action})

    @staticmethod
    def _make_action(app_class, name, _, func, enabled=True):
        action = Gio.SimpleAction.new(name, None)
        action.connect('activate', func)
        app_class.add_action(action)
        action.set_enabled(enabled)
        return action

    def activate_menu(self):
        menu_builder = Gtk.Builder()
        menu_builder.add_from_string(self._to_xml())
        menu_bar = menu_builder.get_object('menu_bar')
        self.app_class.set_menubar(menu_bar)

    def _get_action_name(self, label):
        action_name = self._menu_action_dict.get(label)[0]
        return action_name

    def _get_accel(self, label):
        accel = self._menu_action_dict.get(label)[1]
        return accel

    def _to_xml(self):
        xml = '<interface><menu id="menu_bar">'
        for sub_menu, menu_items in self._menu_items.items():
            xml += '<submenu><attribute name="label">' + sub_menu + '</attribute>'
            for menu_item in menu_items:
                xml += '<item><attribute name="label">' + menu_item + '</attribute>'
                xml += '<attribute name="action">app.' + self._get_action_name(menu_item) + '</attribute>'
                if self._get_accel(menu_item) is not None:
                    xml += '<attribute name="accel">' + self._get_accel(menu_item) + '</attribute>'
                xml += '</item>'
            xml += '</submenu>'
        xml += '</menu></interface>'
        return xml
