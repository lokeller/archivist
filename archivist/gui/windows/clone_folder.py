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
from archivist.gui.windows.operation import *

import os

class CloneFolderWindow(Controller):

    def __init__(self, cabinet):
        Controller.__init__(self, "clone-folder.ui")
        self.ok_button.grab_default()
        self.cabinet = cabinet

        self.folder_store = Gtk.ListStore(str,str,str)

        for c in cabinet.archive.cabinets:

            if not c.is_mounted:
                continue

            for f in c.folders:
                self.folder_store.append([c.name, f.name, os.path.join(c.name, f.name)])

        self.folder_combobox.set_model(self.folder_store)

        renderer_text = Gtk.CellRendererText()
        self.folder_combobox.pack_start(renderer_text, True)
        self.folder_combobox.add_attribute(renderer_text, "text", 2)

    def on_country_combo_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter != None:
            model = combo.get_model()
            country = model[tree_iter][0]
            print("Selected: country=%s" % country)        


    def data_changed(self,widget):
        if self.name_entry.get_text() == "" or self.folder_combobox.get_active_iter() is None:
            self.ok_button.set_sensitive(False)
        else:
            self.ok_button.set_sensitive(True)

    def on_clone(self, progress):
        combo = self.folder_combobox
        model = combo.get_model()
        tree_iter = combo.get_active_iter()

        src_cabinet = self.cabinet.archive.get_cabinet(model[tree_iter][0])
        src_folder = src_cabinet.get_folder(model[tree_iter][1])

        src_folder.clone(self.cabinet, self.name_entry.get_text(), progress=progress)

    def on_finish(self):
        self.window.destroy()

    def ok_action(self, widget):
        op = OperationWindow("Cloning folder", "Folder cloning in progress...", self.on_clone, self.on_finish, self.window)
        op.execute()


    def cancel_action(self, widget):
        self.window.destroy()
        


