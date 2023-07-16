import os
import subprocess
import gi

from functools import partial
from threading import Thread

from distrobox_handler import (
    Distrobox,
    create_box,
    delete_box,
    get_apps_in_box,
    get_available_images_with_distro_name,
    open_terminal_in_box,
    upgrade_box,
)

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import GObject, Gtk, Gio, GLib, Adw


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_default_size(800, 450)

        self.make_titlebar()

        self.toast_overlay = Adw.ToastOverlay()
        self.main_box = Gtk.Box(
            hexpand_set=True, hexpand=True, orientation=Gtk.Orientation.VERTICAL
        )
        self.toast_overlay.set_child(self.main_box)

        self.main_box.set_spacing(10)
        self.main_box.set_margin_top(10)
        self.main_box.set_margin_bottom(10)
        self.main_box.set_margin_start(10)
        self.main_box.set_margin_end(10)

        self.set_child(self.toast_overlay)

        self.load_boxes()

    def make_titlebar(self):
        add_btn = Gtk.Button()
        add_btn.set_icon_name("list-add-symbolic")
        add_btn.connect("clicked", self.create_box)
        add_btn.set_tooltip_text("Create A Distrobox")

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

        if len(boxes) == 0:
            return self.render_no_boxes_message()

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

        while child := self.main_box.get_first_child():
            self.main_box.remove(child)

        self.main_box.append(tabs)

    def render_no_boxes_message(self):
        while child := self.main_box.get_first_child():
            self.main_box.remove(child)

        no_boxes_msg = Gtk.Label(label="No Boxes")
        no_boxes_msg_2 = Gtk.Label(
            label="Click the + at the top-left to create your first box!"
        )

        no_boxes_msg.add_css_class("title-1")
        no_boxes_msg_2.add_css_class("title-2")

        self.main_box.append(no_boxes_msg)
        self.main_box.append(no_boxes_msg_2)

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

        # Name
        name_entry_row = Adw.ActionRow()
        name_entry_row.set_hexpand(True)
        name_entry_row.set_title("Name")
        name_entry_row.add_suffix(Gtk.Label(label=box.name))

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

        # Show Applications
        show_box_applications_btn = Gtk.Button()
        show_box_applications_btn.set_icon_name("application-x-executable-symbolic")
        show_box_applications_btn.connect(
            "clicked", partial(self.show_box_applications, box.name)
        )
        show_box_applications_btn.add_css_class("flat")

        show_box_applications_row = Adw.ActionRow()
        show_box_applications_row.set_title("View Applications")
        show_box_applications_row.add_suffix(show_box_applications_btn)
        show_box_applications_row.set_activatable_widget(show_box_applications_btn)

        # Delete
        delete_box_btn = Gtk.Button()
        delete_box_btn.set_icon_name("user-trash-symbolic")
        delete_box_btn.connect("clicked", partial(self.delete_box, box.name))
        delete_box_btn.add_css_class("flat")

        delete_box_row = Adw.ActionRow()
        delete_box_row.set_title("Delete Box")
        delete_box_row.add_suffix(delete_box_btn)
        delete_box_row.set_activatable_widget(delete_box_btn)

        # Put all into list
        boxed_list.append(name_entry_row)
        boxed_list.append(open_terminal_row)
        boxed_list.append(upgrade_box_row)
        boxed_list.append(show_box_applications_row)
        boxed_list.append(delete_box_row)

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
        self.new_box_popup = Gtk.Window()
        self.new_box_popup.set_transient_for(self)
        self.new_box_popup.set_default_size(700, 350)
        self.new_box_popup.set_modal(True)

        title_lbl = Gtk.Label(label="Create A Distrobox")
        title_lbl.add_css_class("header")

        create_btn = Gtk.Button(label="Create")
        create_btn.add_css_class("suggested-action")

        cancel_btn = Gtk.Button(label="Cancel")
        cancel_btn.connect("clicked", lambda s: self.new_box_popup.destroy())

        new_box_titlebar = Adw.HeaderBar()
        new_box_titlebar.set_title_widget(title_lbl)
        new_box_titlebar.pack_end(create_btn)
        new_box_titlebar.pack_start(cancel_btn)

        self.new_box_popup.set_titlebar(new_box_titlebar)

        new_box_popup_main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        new_box_popup_main.set_spacing(10)
        new_box_popup_main.set_margin_top(10)
        new_box_popup_main.set_margin_bottom(10)
        new_box_popup_main.set_margin_start(10)
        new_box_popup_main.set_margin_end(10)

        boxed_list = Gtk.ListBox()
        boxed_list.add_css_class("boxed-list")

        # Edit Name
        name_entry_row = Adw.EntryRow()
        name_entry_row.set_hexpand(True)
        name_entry_row.set_title("Name")

        # Image Name
        images = get_available_images_with_distro_name()
        image_select = Gtk.DropDown()
        strlst = Gtk.StringList()

        for img in images:
            strlst.append(img)

        image_select.set_model(strlst)

        image_select_row = Adw.ActionRow()
        image_select_row.set_title("Image")
        image_select_row.set_activatable_widget(image_select)
        image_select_row.add_suffix(image_select)

        # do this down here cos the entry row needs to exist
        create_btn.connect(
            "clicked",
            lambda s: self.on_create_box_submit(
                name_entry_row.get_text(),
                image_select.get_selected_item(),
            ),
        )

        boxed_list.append(name_entry_row)
        boxed_list.append(image_select_row)

        new_box_popup_main.append(boxed_list)

        self.create_spinner = Gtk.Spinner()
        new_box_popup_main.append(self.create_spinner)

        self.new_box_popup.set_child(new_box_popup_main)
        self.new_box_popup.present()

    def on_create_box_submit(self, box_name: str, selected_image):
        if not box_name:
            return

        box_name = box_name.replace(" ", "-")

        image = selected_image.get_string().split(" ")[-1]

        def bg_func():
            create_box(box_name, image)
            GObject.idle_add(self.on_create_box_finish)

        self.create_spinner.start()
        Thread(target=bg_func).start()

    def on_create_box_finish(self):
        self.new_box_popup.destroy()

        toast = Adw.Toast.new("Box Created!")
        self.toast_overlay.add_toast(toast)
        self.create_spinner.stop()

        self.delayed_rerender()

    def delete_box(self, box_name: str, *args):
        delete_box(box_name)

        self.delayed_rerender()

        toast = Adw.Toast.new("Box Deleted!")
        self.toast_overlay.add_toast(toast)

    def show_box_applications(self, box_name: str, *args):
        self.show_apps_popup = Gtk.Window()
        self.show_apps_popup.set_transient_for(self)
        self.show_apps_popup.set_default_size(700, 350)
        self.show_apps_popup.set_modal(True)

        show_apps_main = Gtk.ScrolledWindow()
        self.show_apps_main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.show_apps_spinner = Gtk.Spinner()
        self.show_apps_main_box.append(self.show_apps_spinner)

        show_apps_main.set_child(self.show_apps_main_box)
        self.show_apps_popup.set_child(show_apps_main)

        self.show_apps_popup.present()
        self.show_apps_spinner.start()

        def bg_func():
            local_apps = get_apps_in_box(box_name)
            GObject.idle_add(self.on_list_local_apps_called, local_apps)

        Thread(target=bg_func).start()

    def on_list_local_apps_called(self, local_apps):
        boxed_list = Gtk.ListBox()
        boxed_list.add_css_class("boxed-list")

        for app in local_apps:
            app_row = Adw.ActionRow()
            app_row.set_title(app.name)

            img = Gtk.Image.new_from_icon_name(app.icon)
            app_row.add_prefix(img)

            btn = Gtk.Button(label="Add To Menu")
            btn.add_css_class("suggested-action")
            app_row.add_suffix(btn)

            boxed_list.append(app_row)

        self.show_apps_spinner.stop()
        self.show_apps_main_box.append(boxed_list)

    def delayed_rerender(self):
        self.load_boxes()
