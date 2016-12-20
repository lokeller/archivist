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
from archivist.gui.operations import *

class FolderSettingsWidget(Controller):

    def __init__(self, folder):

        Controller.__init__(self, "folder-settings.ui")

        self.folder = folder

        self._update()

    def on_snapshot_clicked(self, widget):
        do_snapshot_folder(self.folder, self._update, self.widget.get_toplevel())

    def on_sync_clicked(self, widget):
        do_sync_folder(self.folder, self._update, self.widget.get_toplevel())

    def on_mount_clicked(self, widget, value):
        if value and not self.folder.is_mounted:
            do_mount_folder(self.folder, self._update, self.widget.get_toplevel())
        elif not value and self.folder.is_mounted:
            do_unmount_folder(self.folder, self._update, self.widget.get_toplevel())

    def _update(self):

        self.folder_name_label.set_text(self.folder.name)

        if not self.folder.supports_unmount:
            self.mount_switch.hide()
            self.mount_switch.set_property("no_show_all", True)
            self.folder_status_label.set_text("")

        if self.folder.supports_unmount:

            if self.folder.is_mounted:
                self.folder_status_label.set_text("Mounted")
                self.mount_switch.set_active(True)
                self.sync_folder_button.set_sensitive(True)
                self.snapshot_folder_button.set_sensitive(True)
            else:
                self.folder_status_label.set_text("Not mounted")
                self.mount_switch.set_active(False)
                self.sync_folder_button.set_sensitive(False)
                self.snapshot_folder_button.set_sensitive(False)
