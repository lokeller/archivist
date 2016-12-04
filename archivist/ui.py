#
#   Copyright 2016 Lorenzo Keller
#
#   This file is part of archivist
#
#
#   archivist is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   archivist is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with archivist.  If not, see <http://www.gnu.org/licenses/>.
#


import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Gio
from gi.repository import GLib
from gi.repository import GObject

from archivist.model import *

import threading
import os
import subprocess

MY_CABINET_PATH = os.path.expanduser("~/My Cabinet")

class Operation(Gtk.Window):

    def __init__(self, title, message, action):
        Gtk.Window.__init__(self, title=title)

        self.action = action
        self.success = False

        # window properties
        self.set_border_width(20)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_deletable(False)

        # setup custom styles 
        style = Gtk.CssProvider()
        style.load_from_data(b".success { color: #00AA00; font-weight: bold; } "
                             b".failure { color: #EE0000; font-weight: bold; }"
                             b"GtkTextView { padding: 10px; color: #fff; "
                             b"background-color: #000; font-family: courier; }")

        # setup client side title bar
        self.hb = Gtk.HeaderBar()
        self.hb.set_show_close_button(False)
        self.hb.props.title = title
        self.set_titlebar(self.hb)

        # main layout
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        # layout at the top
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        vbox.pack_start(hbox, False, False, 0)

        # label with message
        label = Gtk.Label(label=message)
        label.set_halign(Gtk.Align.START)
        hbox.pack_start(label, True, True, 0)

        # spinner for progress
        self.spinner = Gtk.Spinner()        
        hbox.pack_end(self.spinner, False, True, 0)

        # label with status of execution
        self.result_label = Gtk.Label()
        self.result_label.get_style_context().add_provider(style, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        hbox.pack_end(self.result_label, False, False, 0)

        # expander that hides the details
        self.expander = Gtk.Expander.new("Details")
        self.expander.connect('notify::expanded', self._on_expanded)
        self.expander.set_property("margin-top", 20)
        vbox.pack_start(self.expander, True, True, 0)

        # scrollwindow for the details
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        self.expander.add(scrolled_window)

        # textview with the details
        self.text_view = Gtk.TextView()
        self.text_view.get_style_context().add_provider(style, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.text_buffer = self.text_view.get_buffer()
        scrolled_window.add(self.text_view)

        # textview text style for errors
        self.error_style = self.text_buffer.create_tag("error",
            foreground="red")

        # layout at the bottom with buttons
        buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        vbox.pack_end(buttons_box, False, False, 0)

        # button to dismiss window
        self.close_button = Gtk.Button(label="Close")
        self.close_button.connect("clicked", lambda x : self.destroy())
        buttons_box.pack_end(self.close_button, False, False, 0)


    def _on_expanded(self, widget, prp):
        if self.expander.get_property("expanded") :
            self.resize(400, 400)
        else:
            self.resize(400, 150)

    def _append_error(self, message):
        end = self.text_buffer.get_end_iter()
        self.text_buffer.insert_with_tags(end, message, self.error_style)
        self.text_view.scroll_to_iter(end, 0, True, 1, 0)

    def _append_progress(self, message):
        end = self.text_buffer.get_end_iter()
        self.text_buffer.insert(end, message)
        self.text_view.scroll_to_iter(end, 0, True, 1, 0)

    def _on_start(self):
        self.show_all()
        self.resize(400,150)
        self.close_button.hide()
        self.result_label.hide()
        self.spinner.start()

    def _on_finish(self):
        self.spinner.stop()
        self.spinner.hide()

        if self.success:
            self.result_label.set_text("Success")
            clazz = "success"
        else:
            self.result_label.set_text("Error")
            clazz = "failure"

        self.result_label.get_style_context().add_class(clazz)

        self.close_button.show()
        self.result_label.show()

        if self.expander.get_property("expanded"):
            self.resize(400,450)
        else:
            self.resize(400,150)

    def _task(self):

        window = self

        class Progress(archivist.util.ProgressMonitor):
            def on_error(self, message):
                GLib.idle_add(lambda : window._append_error(message))

            def on_progress(self, message):
                GLib.idle_add(lambda : window._append_progress(message))

        GLib.idle_add(self._on_start)

        try :
            self.action(Progress())
            self.success = True
        except Exception:
            self.success = False
            raise
        finally:
            GLib.idle_add(self._on_finish)

    def execute(self):
        t = threading.Thread(target=self._task)
        t.start()


class Tray:

    def __init__(self):
        self.statusicon = Gtk.StatusIcon()
        self.statusicon.set_from_stock(Gtk.STOCK_NETWORK)
        self.statusicon.connect("popup-menu", self.on_right_click_icon)

        self.cabinets = Archive().cabinets

    def on_right_click_icon(self, icon, button, time):
        menu = Gtk.Menu()

        for cabinet in self.cabinets:
            cabinet_menu = self._create_cabinet_menu(cabinet)
            menu.append(cabinet_menu)

        if len(self.cabinets) == 0:
            menu.append(Gtk.MenuItem("No cabinets"))
            
        menu.append(Gtk.SeparatorMenuItem())

        quit = Gtk.MenuItem()
        quit.set_label("Quit")
        quit.connect("activate", Gtk.main_quit)
        menu.append(quit)

        menu.show_all()

        def pos(menu, x, y, push_in):
                return (Gtk.StatusIcon.position_menu(menu, x, y, push_in))

        self.menu = menu
        self.menu.popup(None, None, pos, self.statusicon, button, time)

    def _create_cabinet_menu(self, cabinet):            

        menu_item = Gtk.MenuItem()
        menu_item.set_label(cabinet.name)

        menu = Gtk.Menu()

        if cabinet.is_mounted:

            for folder in cabinet.folders:
                folder_menu = self._create_folder_menu(folder)
                menu.append(folder_menu)

            if len(cabinet.folders) == 0:
                menu.append(Gtk.MenuItem(label="No folders"))

            menu.append(Gtk.SeparatorMenuItem())

            sync = Gtk.MenuItem()
            sync.set_label("Sync all folders")
            menu.append(sync)
            sync.connect("activate", lambda x : self._on_sync_cabinet(cabinet) )

            snapshot = Gtk.MenuItem()
            snapshot.set_label("Snapshot all folders")
            menu.append(snapshot)
            snapshot.connect("activate", lambda x : self._on_snapshot_cabinet(cabinet))

            if cabinet.supports_unmount:
                unmount = Gtk.MenuItem()
                unmount.set_label("Unmount")
                unmount.connect("activate", lambda x : self._on_unmount_cabinet(cabinet))
                menu.append(unmount)
        else:
            mount = Gtk.MenuItem()
            mount.set_label("Mount")
            mount.connect("activate", lambda x : self._on_mount_cabinet(cabinet))
            menu.append(mount)

        menu_item.set_submenu(menu)

        return menu_item

    def _on_unmount_cabinet(self, cabinet):
        op = Operation("Unmounting cabinet", "Cabinet unmount in progress...", cabinet.unmount)
        op.execute()

    def _on_mount_cabinet(self, cabinet):
        op = Operation("Mounting cabinet", "Cabinet mount in progress...", cabinet.mount)
        op.execute()

    def _on_sync_cabinet(self, cabinet):
        op = Operation("Synching cabinet", "Cabinet sync in progress...", cabinet.sync)
        op.execute()

    def _on_snapshot_cabinet(self, cabinet):
        op = Operation("Snapshotting cabinet", "Cabinet snapshot in progress...", cabinet.snapshot)
        op.execute()

    def _create_folder_menu(self, folder):
        menu_item = Gtk.MenuItem()
        menu_item.set_label(folder.name)

        menu = Gtk.Menu()

        if folder.is_mounted:
            open_local = Gtk.MenuItem.new_with_label("Open")
            open_local.connect("activate", lambda x : self._on_open_folder(folder))
            menu.append(open_local)

            if folder.supports_unmount:
                decrypt = Gtk.MenuItem.new_with_label("Unmount")
                decrypt.connect("activate", lambda x : self._on_unmount_folder(folder))
                menu.append(decrypt)

        else:
            decrypt = Gtk.MenuItem.new_with_label("Mount")
            decrypt.connect("activate", lambda x : self._on_mount_folder(folder))
            menu.append(decrypt)

        sync = Gtk.MenuItem.new_with_label("Sync")
        sync.connect("activate", lambda x : self._on_sync_folder(folder))
        menu.append(sync)

        snapshot = Gtk.MenuItem.new_with_label("Snapshot")
        snapshot.connect("activate", lambda x : self._on_snapshot_folder(folder))
        menu.append(snapshot)

        menu_item.set_submenu(menu)

        return menu_item

    def _on_open_folder(self, folder):
        subprocess.check_call(['xdg-open', folder.access_path])

    def _on_unmount_folder(self, folder):
        op = Operation("Unmounting folder", "Folder unmount in progress...", folder.unmount)
        op.execute()

    def _on_mount_folder(self, folder):
        op = Operation("Mounting folder", "Folder mount in progress...", folder.mount)
        op.execute()

    def _on_sync_folder(self, folder):
        op = Operation("Synching folder", "Folder sync in progress...", folder.sync)
        op.execute()

    def _on_snapshot_folder(self, folder):
        op = Operation("Snapshotting folder", "Folder snapshot in progress...", folder.snapshot)
        op.execute()

def main():
    t = Tray()
    Gtk.main()

if __name__ == "__main__":
    main()

