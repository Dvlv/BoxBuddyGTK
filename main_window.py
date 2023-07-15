import os
import subprocess
import gi

from functools import partial

from distrobox_handler import Distrobox, open_terminal_in_box, upgrade_box

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, GLib, Adw


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_default_size(1280, 720)

        self.make_titlebar()

        self.main_box = Gtk.Box(
            hexpand_set=True, hexpand=True, orientation=Gtk.Orientation.HORIZONTAL
        )

        self.main_box.set_spacing(10)
        self.main_box.set_margin_top(10)
        self.main_box.set_margin_bottom(10)
        self.main_box.set_margin_start(10)
        self.main_box.set_margin_end(10)

        self.set_child(self.main_box)

        self.load_boxes()

    def make_titlebar(self):
        add_btn = Gtk.Button()
        add_btn.set_icon_name("list-add-symbolic")
        add_btn.connect("clicked", self.create_box)

        title_lbl = Gtk.Label(label="BoxBuddy")
        title_lbl.add_css_class("header")

        self.titlebar = Adw.HeaderBar()
        self.titlebar.set_title_widget(title_lbl)
        self.titlebar.pack_start(add_btn)

        self.set_titlebar(self.titlebar)

    def load_boxes(self):
        """
        Loads tab for each box
        """
        from distrobox_handler import get_all_distroboxes

        boxes = get_all_distroboxes()

        tabs = Gtk.Notebook()
        tabs.set_tab_pos(Gtk.PositionType.LEFT)
        tabs.set_hexpand(True)
        tabs.set_vexpand(True)

        for box in boxes:
            tab = self.make_box_tab(box)
            tab.set_hexpand(True)
            tab.set_vexpand(True)

            tab_title = Gtk.Grid()
            tab_title.set_column_spacing(0)

            tab_title_label = Gtk.Label(label=box.name)

            # TODO
            tab_title_img = Gtk.Image.new_from_icon_name("view-pin-symbolic")

            tab_title.attach(tab_title_img, 0, 0, 1, 1)
            tab_title.attach(tab_title_label, 1, 0, 1, 1)

            tabs.append_page(tab, tab_title)

        self.main_box.append(tabs)

    def make_box_tab(self, box: Distrobox) -> Gtk.Box:
        """
        Makes box-specific form for the main content
        """
        vbox = Gtk.Box(hexpand=True, orientation=Gtk.Orientation.VERTICAL)
        vbox.set_spacing(15)
        vbox.set_margin_top(10)
        vbox.set_margin_bottom(10)
        vbox.set_margin_start(10)
        vbox.set_margin_end(10)

        page_title = Gtk.Label(label=f"Manage {box.name}")
        page_title.add_css_class("title-1")

        boxed_list = Gtk.ListBox()
        boxed_list.add_css_class("boxed-list")

        # Edit Name
        name_entry_row = Adw.EntryRow()
        name_entry_row.set_hexpand(True)
        name_entry_row.set_title("Name")
        name_entry_row.set_text(box.name)

        # Open Terminal
        open_terminal_btn = Gtk.Button()
        open_terminal_btn.set_icon_name("utilities-terminal-symbolic")
        open_terminal_btn.connect("clicked", partial(self.open_terminal, box.name))
        open_terminal_btn.add_css_class("flat")

        open_terminal_row = Adw.ActionRow()
        open_terminal_row.set_title("Open Terminal")
        open_terminal_row.add_suffix(open_terminal_btn)
        open_terminal_row.set_activatable_widget(open_terminal_btn)

        # Upgrade
        upgrade_box_btn = Gtk.Button()
        upgrade_box_btn.set_icon_name("system-software-update-symbolic")
        upgrade_box_btn.connect("clicked", partial(self.upgrade_box, box.name))
        upgrade_box_btn.add_css_class("flat")

        upgrade_box_row = Adw.ActionRow()
        upgrade_box_row.set_title("Upgrade Box")
        upgrade_box_row.add_suffix(upgrade_box_btn)
        upgrade_box_row.set_activatable_widget(upgrade_box_btn)

        # Put all into list
        boxed_list.append(name_entry_row)
        boxed_list.append(open_terminal_row)
        boxed_list.append(upgrade_box_row)

        # put list into page
        vbox.append(page_title)
        vbox.append(Gtk.Separator())
        vbox.append(boxed_list)

        return vbox

    def open_terminal(self, box_name: str, *args):
        """
        Runs 'distrobox enter' in either Gnome Terminal, Konsole, or xterm
        """
        open_terminal_in_box(box_name)

        GLib.timeout_add_seconds(1, self.delayed_rerender)

    def upgrade_box(self, box_name: str, *args):
        """
        Runs distrobox upgrade
        """
        upgrade_box(box_name)

    def create_box(self, *args):
        print("create_box")

    def delayed_rerender(self):
        pass
