import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, GLib, Adw

def _(a):
    return a


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_default_size(1600, 900)

        self.set_titlebar(Gtk.Box())

        self.main_box = Gtk.Box(hexpand_set=True, hexpand=True, orientation=Gtk.Orientation.HORIZONTAL)

        self.left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.left_box.set_size_request(250, -1)

        self.right_box = Gtk.Box(hexpand_set=True, hexpand=True, orientation=Gtk.Orientation.VERTICAL)
        self.right_box.set_size_request(300, -1)

        self.left_header = Adw.HeaderBar(css_classes=["flat"], show_end_title_buttons=False)
        self.left_header.set_title_widget(Gtk.Label(label="All", css_classes=["title"]))
        self.left_box.append(self.left_header)
        self.left_box.append(Gtk.Separator())

        self.right_header = Adw.HeaderBar(css_classes=["flat"])
        self.right_header.set_title_widget(Gtk.Label(label="Box", css_classes=["title"]))
        self.right_box.append(self.right_header)
        self.right_box.append(Gtk.Separator())

        self.main_box.append(self.left_box)
        self.main_box.append(Gtk.Separator())
        self.main_box.append(self.right_box)

        self.set_child(self.main_box)
