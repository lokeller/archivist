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

import threading
import archivist.util

from gi.repository import GLib

class ProgressWidget(Controller):

    def __init__(self, message, action, after=None):

        Controller.__init__(self, "progress.ui")

        self.action = action
        self.success = False
        self.after = after

        # setup custom styles 
        style = Gtk.CssProvider()
        style.load_from_data(b".success { color: #00AA00; font-weight: bold; } "
                             b".failure { color: #EE0000; font-weight: bold; }"
                             b"GtkTextView { padding: 10px; color: #fff; "
                             b"background-color: #000; font-family: courier; }")


        self.result_label.get_style_context().add_provider(style, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.text_view.get_style_context().add_provider(style, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.text_buffer = self.text_view.get_buffer()

        self.label.set_text(message)

        # textview text style for errors
        self.error_style = self.text_buffer.create_tag("error",
            foreground="red")

    def _append_error(self, message):
        end = self.text_buffer.get_end_iter()
        self.text_buffer.insert_with_tags(end, message, self.error_style)
        self.text_view.scroll_to_iter(end, 0, True, 1, 0)

    def _append_progress(self, message):
        end = self.text_buffer.get_end_iter()
        self.text_buffer.insert(end, message)
        self.text_view.scroll_to_iter(end, 0, True, 1, 0)

    def _on_start(self):
        self.widget.show_all()
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

        self.result_label.show()

        if self.after is not None:
            self.after(self.success)

    def _task(self):

        widget = self

        class Progress(archivist.util.ProgressMonitor):
            def on_error(self, message):
                GLib.idle_add(lambda : widget._append_error(message))

            def on_progress(self, message):
                GLib.idle_add(lambda : widget._append_progress(message))

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
