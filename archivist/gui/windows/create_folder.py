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

class CreateFolderWindow(Controller):

    def __init__(self, cabinet):
        Controller.__init__(self, "create-folder.ui")

        self.cabinet = cabinet

    def on_cancel_clicked(self, widget):
        self.window.destroy()

    def on_prepare(self, assistant, page):

        if page == self.create_step:
            page.set_property("margin", 20)
            progress = ProgressWidget("Creating folder...", self._create_folder, self._after)
            page.pack_start(progress.widget, True, True, 0)
            progress.execute()

    def _create_folder(self, progress):
        if self.plain_folder.get_active():
            self.cabinet.create_folder(self.folder_name.get_text(), 'plain', {}, progress=progress)
        elif self.encrypted_folder.get_active():
            self.cabinet.create_folder(self.folder_name.get_text(), 'encrypted', {}, progress=progress)

    def _after(self, success):
        self.window.commit()
        self.window.set_page_complete(self.create_step, True)

    def on_name_changed(self, widget):
        self.window.set_page_complete(self.name_step, widget.get_text() != "")
