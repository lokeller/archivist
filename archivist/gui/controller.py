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

import os

UI_PATH = os.path.join(os.path.dirname(__file__), 'ui')

class Controller(object):

    def __init__(self, ui_file):

        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(UI_PATH, ui_file))
        self.builder.connect_signals(self)

    def __getattr__(self, name):
        w = self.builder.get_object(name)

        if w is None:
            raise AttributeError("Attribute %s not found" % name)

        return w
