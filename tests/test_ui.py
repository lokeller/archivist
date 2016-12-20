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



import unittest
import time
import archivist.ui

import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from gi.repository import GLib

class UiTests(unittest.TestCase):

    def test_Operation_success(self):

        def simple_task(progress):

            for i in range(0,4):
                progress.on_progress("progress " + str(i) + "\n")
                time.sleep(1)
                progress.on_error("error\n")
                time.sleep(1)

        op = archivist.ui.Operation(title="Test operation", 
                       message="Interpolating splines...", 
                        action=simple_task )

        GLib.idle_add(op.execute)
        op.connect("destroy", Gtk.main_quit)

        Gtk.main()

    def test_Operation_error(self):

        def simple_task(progress):

            raise Exception("rrror")

        op = archivist.ui.Operation(title="Test operation", 
                       message="Interpolating splines...", 
                        action=simple_task )

        GLib.idle_add(op.execute)
        op.connect("destroy", Gtk.main_quit)

        Gtk.main()
