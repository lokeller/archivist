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
from archivist.gui.widgets.cabinet_settings import *
from archivist.gui.windows.add_cabinet import *

from gi.repository import Pango

class SettingsWindow(Controller):

    def __init__(self, archive):
        Controller.__init__(self, 'settings.ui')
 
        self.archive = archive

        treeview = self.cabinets_treeview

        renderer = Gtk.CellRendererPixbuf()

        renderer.set_property('width', 32)
        renderer.set_property('xalign', 1.0)
        renderer.set_property('stock-size', Gtk.IconSize.MENU)
        renderer.set_padding(4, 10)
    
        column = Gtk.TreeViewColumn("icon", renderer)
        column.add_attribute(renderer, "icon-name", 0)

        treeview.append_column(column)

        renderer = Gtk.CellRendererText()
        renderer.set_property("wrap-mode", Pango.WrapMode.WORD)
        renderer.set_property("ellipsize", Pango.EllipsizeMode.END)

        column = Gtk.TreeViewColumn("title", renderer)
        column.set_expand(True)
        column.add_attribute(renderer, "text", 1)

        treeview.append_column(column)
        treeview.get_selection().connect("changed", self.on_cabinet_changed)

        self._update()

        self.cabinets_scrolledwindow.set_size_request(200, -1)

        self.window.resize(1000, 600)

    def _update(self):
        
        i = 0

        self.cabinet_settings = []
        self.liststore_cabinets.clear()
        self.cabinets_notebook.forall( lambda widget : self.cabinets_notebook.remove(widget))

        for cabinet in self.archive.cabinets:
            self.liststore_cabinets.append(["preferences-system-network-symbolic", cabinet.name, i])
            i = i + 1
            controller = CabinetSettingsWidget(cabinet)
            self.cabinet_settings.append(self.cabinet_settings)
            self.cabinets_notebook.append_page(controller.widget) 

    def on_add_cabinet_clicked(self, widget):
        controller = AddCabinetWindow(self.archive)
        controller.window.connect('destroy', lambda x: self._update())
        controller.window.set_transient_for(self.window)
        controller.window.show_all()

    def on_remove_cabinet_clicked(self, widget):

        dialog = Gtk.MessageDialog(self.window, 0, Gtk.MessageType.QUESTION,
            Gtk.ButtonsType.YES_NO, "Do you really want to remove the cabinet?")
        dialog.format_secondary_text(
            "Removing the cabinet from the list will not remove the cabinet folders from disk.")
        response = dialog.run()

        if response == Gtk.ResponseType.YES:
            model, it = self.cabinets_treeview.get_selection().get_selected()
            self.archive.get_cabinet(model[it][1]).delete()
            self._update()

        dialog.destroy()

    def on_cabinet_changed(self, selection):
        model, it = selection.get_selected()

        if it is None:
            return

        self.cabinets_notebook.set_current_page(model[it][2])
