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
from archivist.gui.widgets.progress import *

class AddCabinetWindow(Controller):

    def __init__(self, archive):
        Controller.__init__(self, "add-cabinet.ui")

        self.archive = archive

    def update_pages(self):

        if self.sshfs_cabinet.get_active():
            self.remote_step.show_all()
        else:
            self.remote_step.hide()

        if self.local_cabinet.get_active():
            self.local_step.show_all()
        else:
            self.local_step.hide()

    def on_type_changed(self, widget):
        self.update_pages()

    def on_cancel_clicked(self, widget):
        self.window.destroy()

    def on_prepare(self, assistant, page):

        self.update_pages()

        if page == self.create_step:
            page.set_property("margin", 20)
            progress = ProgressWidget("Adding cabinet...", self._create_cabinet, self._after)
            page.pack_start(progress.widget, True, True, 0)
            progress.execute()

    def _create_cabinet(self, progress):
        name = self.name_entry.get_text()

        if self.local_cabinet.get_active():
            args = {'storagePath': self.local_path_chooser.get_filename()}
            self.archive.add_cabinet(name, 'plain', args)

        elif self.sshfs_cabinet.get_active():
            args = {'host': self.host_entry.get_text(), 'path': self.path_entry.get_text()}
            self.archive.add_cabinet(name, 'sshfs', args)

    def _after(self, success):
        self.window.commit()
        self.window.set_page_complete(self.create_step, True)

    def on_local_settings_changed(self, widget):
        self.window.set_page_complete(self.local_step, self.local_path_chooser.get_uri() != None)

    def on_remote_settings_changed(self, widget):
        state = self.host_entry.get_text() != "" and self.path_entry.get_text() != ""

        self.window.set_page_complete(self.remote_step, state)

    def on_name_changed(self, widget):
        self.window.set_page_complete(self.name_step, widget.get_text() != "")
