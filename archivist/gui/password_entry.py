#
#   Copyright 2017 Lorenzo Keller
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

import os


from archivist.gui.windows.create_password import *
from archivist.gui.windows.get_password import *

import sys

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Root dir not available")
        sys.exit(1)

    if os.path.exists(os.path.join(sys.argv[1], '.encfs6.xml')):
        controller = GetPasswordPrompt()
    else:
        controller = CreatePasswordPrompt()

    controller.window.show_all()
    controller.window.set_keep_above(True)
    controller.window.present()

    Gtk.main()
