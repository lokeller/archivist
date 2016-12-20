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

from archivist.gui.windows.tray import Tray
from archivist.model import Archive

def main():
    archive = Archive()

    if not archive.exists():
        archive.init()

    t = Tray(archive)
    Gtk.main()

if __name__ == "__main__":
    main()

