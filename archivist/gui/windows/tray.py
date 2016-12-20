#
#   Copyright 2016-2017 Lorenzo Keller
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

from archivist.model import *
from archivist.gui.windows.settings import SettingsWindow
from archivist.gui.operations import *

class Tray:

    def __init__(self, archive):
        self.statusicon = Gtk.StatusIcon()
        self.statusicon.set_from_stock(Gtk.STOCK_NETWORK)
        self.statusicon.connect("popup-menu", self.on_right_click_icon)

        self.archive = archive

    def _on_settings(self, widget):
        self.settings = SettingsWindow(self.archive)
        self.settings.window.show_all()

    def on_right_click_icon(self, icon, button, time):
        menu = Gtk.Menu()

        for cabinet in self.archive.cabinets:
            cabinet_menu = self._create_cabinet_menu(cabinet)
            menu.append(cabinet_menu)

        if len(self.archive.cabinets) == 0:
            menu.append(Gtk.MenuItem("No cabinets"))
            
        menu.append(Gtk.SeparatorMenuItem())

        settings = Gtk.MenuItem()
        settings.set_label("Settings...")
        settings.connect("activate", self._on_settings)
        menu.append(settings)

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

            open_menu = Gtk.MenuItem()
            open_menu.set_label("Open")
            menu.append(open_menu)
            open_menu.connect("activate",lambda x : self.on_open_cabinet(cabinet) )

            sync = Gtk.MenuItem()
            sync.set_label("Sync all folders")
            menu.append(sync)
            sync.connect("activate", lambda x : do_sync_cabinet(cabinet) )

            snapshot = Gtk.MenuItem()
            snapshot.set_label("Snapshot all folders")
            menu.append(snapshot)
            snapshot.connect("activate", lambda x : do_snapshot_cabinet(cabinet))

            if cabinet.supports_unmount:
                unmount = Gtk.MenuItem()
                unmount.set_label("Unmount")
                unmount.connect("activate", lambda x : do_unmount_cabinet(cabinet))
                menu.append(unmount)
        else:
            mount = Gtk.MenuItem()
            mount.set_label("Mount")
            mount.connect("activate", lambda x : do_mount_cabinet(cabinet))
            menu.append(mount)

        menu_item.set_submenu(menu)

        return menu_item

    def _create_folder_menu(self, folder):
        menu_item = Gtk.MenuItem()
        menu_item.set_label(folder.name)

        menu = Gtk.Menu()

        if folder.is_mounted:
            open_local = Gtk.MenuItem.new_with_label("Open")
            open_local.connect("activate", lambda x : self.on_open_folder(folder))
            menu.append(open_local)

            if folder.supports_unmount:
                decrypt = Gtk.MenuItem.new_with_label("Unmount")
                decrypt.connect("activate", lambda x : do_unmount_folder(folder))
                menu.append(decrypt)

        else:
            decrypt = Gtk.MenuItem.new_with_label("Mount")
            decrypt.connect("activate", lambda x : do_mount_folder(folder))
            menu.append(decrypt)

        sync = Gtk.MenuItem.new_with_label("Sync")
        sync.connect("activate", lambda x : do_sync_folder(folder))
        menu.append(sync)

        snapshot = Gtk.MenuItem.new_with_label("Snapshot")
        snapshot.connect("activate", lambda x : do_snapshot_folder(folder))
        menu.append(snapshot)

        menu_item.set_submenu(menu)

        return menu_item

    def on_open_folder(self, folder):
        subprocess.check_call(['xdg-open', folder.access_path])

    def on_open_cabinet(self, cabinet):
        subprocess.check_call(['xdg-open', cabinet.access_path])

