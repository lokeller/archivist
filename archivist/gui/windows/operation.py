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

class OperationWindow(Controller):

    def __init__(self, title, message, action, after=None, parent=None):
        Controller.__init__(self, 'operation.ui')

        self.action = action
        self.success = False
        self.after = after

        self.window.set_title(title)

        # setup modal if necessary
        if parent:
            self.window.set_modal(True)
            self.window.set_transient_for(parent)
            self.window.set_keep_above(True)

        # progress
        self.progress = ProgressWidget(message, action, self.on_progress_finished)
        self.progress.expander.connect('notify::expanded', self.on_progress_expanded)
        self.box1.pack_start(self.progress.widget, True, True, 0)

    def on_close_clicked(self, widget):
        self.window.destroy()

    def on_progress_expanded(self, widget, prp):
        if self.progress.expander.get_property("expanded") :
            self.window.resize(400, 400)
        else:
            self.window.resize(400, 150)

    def on_progress_finished(self, success):

        self.close_button.show()

        if self.progress.expander.get_property("expanded"):
            self.window.resize(400,450)
        else:
            self.window.resize(400,150)

        if self.after is not None:
            self.after()

    def execute(self):
        self.window.show_all()
        self.window.resize(400,150)
        self.close_button.hide()

        self.progress.execute()

