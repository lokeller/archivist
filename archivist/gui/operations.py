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

from archivist.gui.windows.operation import *

import os
import sys

def do_unmount_folder(folder, after=None, parent=None):
    op = OperationWindow("Unmounting folder", "Folder unmount in progress...", folder.unmount, after, parent)
    op.execute()

def do_mount_folder(folder, after=None, parent=None):

    def mount_with_args(progress, folder=folder):
        args = {"password_program": "'%s' '%s' '%s'" % ( sys.executable, 
                                    os.path.join(os.path.dirname(__file__), 'password_entry.py'),
                                    folder.storage_path ) }
        folder.mount(args, progress)

    op = OperationWindow("Mounting folder", "Folder mount in progress...", mount_with_args, after, parent)
    op.execute()

def do_sync_folder(folder, after=None, parent=None):
    op = OperationWindow("Synching folder", "Folder sync in progress...", folder.sync, after, parent)
    op.execute()

def do_snapshot_folder(folder, after=None, parent=None):
    op = OperationWindow("Snapshotting folder", "Folder snapshot in progress...", folder.snapshot, after, parent)
    op.execute()

def do_unmount_cabinet(cabinet, after=None, parent=None):
    op = OperationWindow("Unmounting cabinet", "Cabinet unmount in progress...", cabinet.unmount, after, parent)
    op.execute()

def do_mount_cabinet(cabinet, after=None, parent=None):
    op = OperationWindow("Mounting cabinet", "Cabinet mount in progress...", cabinet.mount, after, parent)
    op.execute()

def do_sync_cabinet(cabinet, after=None, parent=None):
    op = OperationWindow("Synching cabinet", "Cabinet sync in progress...", cabinet.sync, after, parent)
    op.execute()

def do_snapshot_cabinet(cabinet, after=None, parent=None):
    op = OperationWindow("Snapshotting cabinet", "Cabinet snapshot in progress...", cabinet.snapshot, after, parent)
    op.execute()
