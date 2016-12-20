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

from archivist.gui.controller import *
from archivist.gui.windows.create_folder import *
from archivist.gui.windows.clone_folder import *
from archivist.gui.widgets.folder_settings import *

class CabinetSettingsWidget(Controller):

    def __init__(self, cabinet):
        Controller.__init__(self, "cabinet-settings.ui")

        self.cabinet = cabinet

        self._update()

    def on_snapshot_all_clicked(self, widget):
        do_snapshot_cabinet(self.cabinet, self._update, self.widget.get_toplevel())

    def on_sync_all_clicked(self, widget):
        do_sync_cabinet(self.cabinet, self._update, self.widget.get_toplevel())

    def on_mount_clicked(self, widget, value):
        if widget.get_active() and not self.cabinet.is_mounted:
            do_mount_cabinet(self.cabinet, self._update, self.widget.get_toplevel())
        elif not widget.get_active() and self.cabinet.is_mounted:
            do_unmount_cabinet(self.cabinet, self._update, self.widget.get_toplevel())

    def on_create_folder_clicked(self, widget):
        controller = CreateFolderWindow(self.cabinet)
        controller.window.connect('destroy', lambda x: self._update())
        controller.window.set_transient_for(self.widget.get_toplevel())
        controller.window.show_all()

    def on_clone_clicked(self, widget):
        controller = CloneFolderWindow(self.cabinet)
        controller.window.connect('destroy', lambda x: self._update())
        controller.window.set_transient_for(self.widget.get_toplevel())
        controller.window.show_all()

    def _update(self):

        cabinet = self.cabinet

        self.cabinet_name_label.set_text(cabinet.name)

        status_label = self.cabinet_status_label
        mount_switch = self.mount_switch

        if not cabinet.supports_unmount:
            mount_switch.hide()
            mount_switch.set_property("no_show_all", True)
            status_label.set_text("")

        folders = self.folders

        if folders.get_child() is not None:
            folders.get_child().destroy()

        if cabinet.is_mounted:

            if cabinet.supports_unmount:
                status_label.set_text("Mounted")
                mount_switch.set_active(True)


            l = Gtk.ListBox()

            l.set_selection_mode(Gtk.SelectionMode.NONE)

            def header_fun(row, before):

                if before is None:
                    row.set_header(None)

                if row.get_header() is None:
                    current = Gtk.Separator.new(Gtk.Orientation.HORIZONTAL)
                    row.set_header(current)

            l.set_header_func(header_fun)

            self.folder_settings = []
            for folder in cabinet.folders:
                controller = FolderSettingsWidget(folder)
                self.folder_settings.append(controller)
                l.add(controller.widget)

            folders.add(l)

            if len(cabinet.folders) == 0:
                self.no_folders_label.show()
                folders.set_property("no_show_all", True)
                folders.hide()
            else:                
                self.no_folders_label.hide()
                folders.set_property("no_show_all", False)
                folders.show_all()

            if len(cabinet.folders) > 4:
                folders.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
                self.widget.child_set_property(folders, 'fill', True)
                self.widget.child_set_property(folders, 'expand', True)
            else:
                self.widget.child_set_property(folders, 'fill', False)
                self.widget.child_set_property(folders, 'expand', False)
                folders.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)

            self.create_folder_button.set_sensitive(True)
            self.sync_folders_button.set_sensitive(True)
            self.snapshot_folders_button.set_sensitive(True)

        else:

            if cabinet.supports_unmount:
                status_label.set_text("Not mounted")
                mount_switch.set_active(False)

            folders.hide()
            folders.set_property("no_show_all", True)

            self.create_folder_button.set_sensitive(False)
            self.sync_folders_button.set_sensitive(False)
            self.snapshot_folders_button.set_sensitive(False)
