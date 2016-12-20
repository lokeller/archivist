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

from archivist.model import *
import archivist.ui
import argparse
import getpass

def get_archive(args):
    return Archive(args.archive_path)

def archive_init(args):
    get_archive(args).init()

def archive_ls_cabinets(args):
    for cabinet in get_archive(args).cabinets:
        print(cabinet.name)

def archive_add_cabinet(args):
    archive = get_archive(args)
   
    type_name = args.type_name
    type_args = {}
    for arg in cabinet_types[type_name].creation_args:
        type_args[arg] = vars(args)[type_name + "." + arg]
     
    archive.add_cabinet(args.cabinet_name, type_name, type_args)

def archive_delete_cabinet(args):
    archive = get_archive(args)

    archive.get_cabinet(args.cabinet_name).delete()

def create_archive_subparser(subparsers):

    archive_parser = subparsers.add_parser('archive', help="archive object")

    archive_subparsers = archive_parser.add_subparsers(help="archive actions")

    init_parser = archive_subparsers.add_parser('init', help="Initialiye the archive")
    init_parser.set_defaults(func=archive_init)

    list_parser = archive_subparsers.add_parser('ls-cabinets', help="List cabinets in the archive")
    list_parser.set_defaults(func=archive_ls_cabinets)

    add_parser = archive_subparsers.add_parser('add-cabinet', help="Adds a cabinet in the archive")

    add_parser.add_argument("cabinet_name", help="Name of the cabinet")
    add_type_subparser = add_parser.add_subparsers(dest='type_name', help="type of archive")

    for type_name in cabinet_types:
        type_parser = add_type_subparser.add_parser(type_name)
        for arg in cabinet_types[type_name].creation_args:
            type_parser.add_argument("--" + type_name + "." + arg, required=True)

    add_parser.set_defaults(func=archive_add_cabinet)

    delete_parser = archive_subparsers.add_parser('delete-cabinet', help="Deletes a cabinet from the archive")
    delete_parser.add_argument('cabinet_name', help="Name of the cabinet to delete")
    delete_parser.set_defaults(func=archive_delete_cabinet)

def get_cabinet(args):
    archive = Archive(args.archive_path)
    cabinet = archive.get_cabinet(args.cabinet_name)

    if cabinet is None:
        print("Cabinet not found")
        exit(1)

    return cabinet
    

def cabinet_ls_folders(args):
    for folder in get_cabinet(args).folders:
        print(folder.name)

def cabinet_create_folder(args):
    cabinet = get_cabinet(args)
   
    type_name = args.type_name
    type_args = {}
    for arg in folder_types[type_name].creation_args:
        type_args[arg] = vars(args)[type_name + "." + arg]
     
    cabinet.create_folder(args.folder_name, type_name, type_args)

def cabinet_sync_folders(args):
    get_cabinet(args).sync()

def cabinet_snapshot_folders(args):
    get_cabinet(args).snapshot()

def cabinet_mount(args):
    get_cabinet(args).mount()

def cabinet_unmount(args):
    get_cabinet(args).unmount()

def create_cabinet_subparser(subparsers):
    cabinet_parser = subparsers.add_parser('cabinet', help="cabinet object")

    cabinet_parser.add_argument("cabinet_name", help="name of the cabinet")

    cabinet_subparsers = cabinet_parser.add_subparsers(dest="cabinet_action", help="cabinet actions")
    cabinet_subparsers.required = True

    # ls-folders

    parser = cabinet_subparsers.add_parser('ls-folders', help="List folders in the cabinet")
    parser.set_defaults(func=cabinet_ls_folders)

    # create-folder

    parser = cabinet_subparsers.add_parser('create-folder', help="Create a folder")

    parser.add_argument("folder_name", help="Name of the folder")
    subparser = parser.add_subparsers(dest='type_name', help="type of archive")
    subparser.required = True

    for type_name in folder_types:
        type_parser = subparser.add_parser(type_name)
        for arg in folder_types[type_name].creation_args:
            type_parser.add_argument("--" + type_name + "." + arg, required=True)

    parser.set_defaults(func=cabinet_create_folder )

    # mount

    parser = cabinet_subparsers.add_parser('mount', help="Mount cabinet")
    parser.set_defaults(func=cabinet_mount)

    # unmount

    parser = cabinet_subparsers.add_parser('unmount', help="Unmount cabinet")
    parser.set_defaults(func=cabinet_unmount)

    # sync-folders

    parser = cabinet_subparsers.add_parser('sync-folders', help="Sync all folders in the cabinet")
    parser.set_defaults(func=cabinet_sync_folders)

    # snapshot-folders

    parser = cabinet_subparsers.add_parser('snapshot-folders', help="Snapshot all folders in the cabinet")
    parser.set_defaults(func=cabinet_snapshot_folders)

def get_folder(args):
    archive = Archive(args.archive_path)

    try:
        cabinet_name, folder_name = args.folder_name.split(os.sep, 1)
    except ValueError:
        print("Invalid folder name")
        exit(1)

    cabinet = archive.get_cabinet(cabinet_name)

    if cabinet is None:
        print("Cannot find cabinet")
        exit(1)

    folder = cabinet.get_folder(folder_name)
    
    if folder is None:
        print("Cannot find folder")
        exit(1)

    return folder

def folder_sync(args):
    get_folder(args).sync()

def folder_snapshot(args):
    get_folder(args).snapshot()

def folder_mount(args):
    folder = get_folder(args)
    folder.mount()

def folder_unmount(args):
    get_folder(args).unmount()

def folder_clone(args):
    folder = get_folder(args)

    archive = Archive(args.archive_path)
    dest_cabinet_name, dest_folder_name = args.destination.split(os.sep, 1)
    dest_cabinet = archive.get_cabinet(dest_cabinet_name)

    folder.clone(dest_cabinet, dest_folder_name)

def folder_access_path(args):
    print(get_folder(args).access_path)

def create_folder_subparser(subparsers):
    folder_parser = subparsers.add_parser('folder', help="folder object")

    folder_parser.add_argument("folder_name", help="name of the folder (starting with cabinet name)")

    folder_subparsers = folder_parser.add_subparsers(dest="folder_action", help="folder actions")
    folder_subparsers.required = True

    # mount

    parser = folder_subparsers.add_parser('mount', help="Mount folder")
    parser.set_defaults(func=folder_mount)

    # unmount

    parser = folder_subparsers.add_parser('unmount', help="Unmount folder")
    parser.set_defaults(func=folder_unmount)

    # clone
    parser = folder_subparsers.add_parser('clone', help="Clone the folders")
    parser.add_argument('destination', help="Where the clone should be created (cabinet/path/to/folder)")
    parser.set_defaults(func=folder_clone)

    # sync

    parser = folder_subparsers.add_parser('sync', help="Sync all folders in the folder")
    parser.set_defaults(func=folder_sync)

    # snapshot

    parser = folder_subparsers.add_parser('snapshot', help="Snapshot all folders in the folder")
    parser.set_defaults(func=folder_snapshot)

    # access_path

    parser = folder_subparsers.add_parser('access-path', help="Returns the access path")
    parser.set_defaults(func=folder_access_path)

def start_ui(args):
    archivist.ui.main()

def main():
    parser = argparse.ArgumentParser(description="Manage an archive")

    subparsers = parser.add_subparsers(dest="object_type", help='sub-commands help')
    subparsers.required = True

    parser.add_argument("--archive_path", default=DEFAULT_ARCHIVE_PATH, 
                                    help="path to the archive")

    ui_parser = subparsers.add_parser('gui', help="start ui")
    ui_parser.set_defaults(func=start_ui)

    create_archive_subparser(subparsers)
    create_cabinet_subparser(subparsers)
    create_folder_subparser(subparsers)

    args = parser.parse_args()

    args.func(args)


if __name__ == "__main__":
    main()
