#
#   Copyright 2016 Lorenzo Keller
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

import archivist.util
import os
from urllib.parse import urlparse
import configparser

folder_types = {}

def RegisterFolderType(clazz):
    folder_types[clazz.type_name] = clazz

class Folder(object):

    type_name = "plain"

    creation_args = []

    def __init__(self, cabinet, name):
        self.cabinet = cabinet
        self.storage_path = os.path.join(cabinet.access_path, name)

    @property
    def name(self):
        return os.path.relpath(self.storage_path, self.cabinet.access_path)

    @property
    def access_path(self):
        return self.storage_path

    @property
    def supports_unmount(self):
        return False

    def mount(self, progress=None):
        pass

    def unmount(self, progress=None):
        pass

    @property
    def is_mounted(self):
        return True

    def snapshot(self, progress=None):
        progress and progress.on_progress("Adding all changes\n")

        archivist.util.exec(['git', 'add', '-v', '--all', '.'], 
                            wd=self.storage_path, progress=progress)
        progress and progress.on_progress("Committing all changes\n")

        archivist.util.exec(['git', 'commit', '--allow-empty', 
                        '-q', '-m', 'Snapshot'], 
                            wd=self.storage_path, progress=progress)

        progress and progress.on_progress("Done\n")

    def sync(self, progress=None):
        progress and progress.on_progress("Performing sync\n")

        archivist.util.exec(['git', 'annex', 'sync', '--content'], 
                            wd=self.storage_path, progress=progress)

        progress and progress.on_progress("Done")


    @classmethod
    def load(cls, cabinet, name, config):
        return Folder(cabinet, name)

    @classmethod
    def create(cls, cabinet, name, args, progress=None):

        abs_cabinet_path = os.path.abspath(cabinet.access_path)
        dirname = os.path.abspath(os.path.join(abs_cabinet_path, name))

        if os.path.relpath(dirname, abs_cabinet_path) != name:
            raise Exception("Invalid name")

        if os.path.isdir(dirname):
            raise Exception("Already exists")

        os.makedirs(dirname)

        archivist.util.exec(['git', 'init', '.'], 
                wd=dirname, progress=progress)

        archivist.util.exec(['git', 'annex', 'init', '--version=6'], 
                wd=dirname, progress=progress)

        config = configparser.ConfigParser()

        config['folder'] = {'type': cls.type_name}

        with open(os.path.join(dirname, '.git', 'archivist'), 'w') as configfile:
           config.write(configfile)


RegisterFolderType(Folder)

class EncryptedFolder(Folder):

    type_name = "encrypted"
    creation_args = []

    def __init__(self, cabinet, storage_path):
        Folder.__init__(self, cabinet, storage_path)

    @property
    def access_path(self):
        return self.storage_path + ".Decrypted"

    @property
    def supports_unmount(self):
        return True

    def mount(self, progress=None):

        if self.is_mounted:
            raise Exception("Already mounted")

        if not os.path.isdir(self.access_path):
            os.makedirs(self.access_path)

        archivist.util.exec(['encfs', '--extpass=/usr/libexec/openssh/gnome-ssh-askpass',
                                 '-i', '10', '-S', self.storage_path, self.access_path],
                                    progress=progress)

    def unmount(self, progress=None):
        archivist.util.exec(['fusermount', '-u', self.access_path], progress=progress)

        if os.listdir(self.access_path) == []:
            os.rmdir(self.access_path)

    @property
    def is_mounted(self):
        return os.path.ismount(self.access_path)

    @classmethod
    def load(cls, cabinet, name, config):
        return EncryptedFolder(cabinet, name)


RegisterFolderType(EncryptedFolder)

cabinet_types = {}

def RegisterCabinetType(clazz):
    cabinet_types[clazz.type_name] = clazz

class Cabinet(object):

    type_name = "plain"
    creation_args = ['storagePath']

    def __init__(self, archive, name, storage_path):
        self.archive = archive
        self.name = name
        self.storage_path = storage_path

    @property
    def access_path(self):
        return self.storage_path

    @property
    def supports_unmount(self):
        return False

    def mount(self, progress=None):
        pass

    def unmount(self, progress=None):
        pass

    @property
    def is_mounted(self):
        return True

    def get_folder(self, name):

        if not self.is_mounted:
            raise Exception("Not cabinet mounted")

        config_path = os.path.join(self.access_path, name, ".git","archivist")
        
        if not os.path.isfile(config_path):
            return None

        config = configparser.ConfigParser()
        config.read(config_path)

        folder_type = config.get("folder", "type", fallback=None)

        if folder_type is None:
            raise Exception("Folder without type found")

        if folder_type not in folder_types:
            raise Exception("Unsupported type of folder")

        return folder_types[folder_type].load(self, name, config)

    @property
    def folders(self):

        if not self.is_mounted:
            raise Exception("Not cabinet mounted")

        folders = []

        # search for all the folders in the cabinet
        for dirpath, dirnames, filenames in os.walk(self.access_path):

            folder = self.get_folder(os.path.relpath(dirpath, self.access_path))

            if folder is None:
                continue

            # don't walk into subdirs
            del dirnames[:]

            folders.append(folder)

        return folders

    def sync(self, progress=None):

        if not self.is_mounted:
            raise Exception("Not cabinet mounted")

        for folder in self.folders:
            progress and progress.on_progress("Synching " + folder.name + "\n")
            folder.sync(progress)

    def snapshot(self, progress=None):

        if not self.is_mounted:
            raise Exception("Not cabinet mounted")

        for folder in self.folders:
            progress and progress.on_progress("Snapshotting " + folder.name + "\n")
            folder.snapshot(progress)

    def create_folder(self, name, folder_type, args, progress=None):

        if not self.is_mounted:
            raise Exception("Not cabinet mounted")

        if folder_type not in folder_types:
            raise Exception("Unsupported type of folder")

        folder_types[folder_type].create(self, name, args, progress)

    @classmethod
    def load(cls, archive, config, name):

        storage_path = config.get("backend", "storagePath", fallback=None)

        if storage_path is None:
            raise Exception("Invalid storage path")

        return Cabinet(archive, name, storage_path)


    @classmethod
    def create(cls, archive, name, args):

        if os.path.dirname(name) != "":
            raise Exception("Invalid name")

        for arg in cls.creation_args:
            if arg not in args:
                raise Exception("Argument %s missing" % arg)

        config_path = os.path.join(archive.cabinets_path, name)

        config = configparser.ConfigParser()

        config["cabinet"] = { 'type' : cls.type_name}
        config["backend"] = args

        with open(config_path, "w") as fp:
            config.write(fp)

RegisterCabinetType(Cabinet)

class SshFsCabinet(Cabinet):

    type_name = "sshfs"
    creation_args = ['host', 'path']

    def __init__(self, archive, name, host, path):
        self.archive = archive
        self.name = name
        self.host = host
        self.path = path

    @property
    def access_path(self):
        return self.archive.get_cabinet_wd(self)

    @property
    def supports_unmount(self):
        return True

    def mount(self, progress=None):
        if self.is_mounted:
            raise Exception("Already mounted")

        if not os.path.isdir(self.access_path):
            os.makedirs(self.access_path)

        archivist.util.exec(['sshfs', self.host + ":" + self.path, self.access_path], progress=progress)

    def unmount(self, progress=None):
        archivist.util.exec(['fusermount', '-u', self.access_path], progress=progress)

        if os.listdir(self.access_path) == []:
            os.rmdir(self.access_path)

    @property
    def is_mounted(self):
        return os.path.ismount(self.access_path)

    @classmethod
    def load(cls, archive, config, name):

        host = config.get("backend", "host", fallback=None)
        path = config.get("backend", "path", fallback="")

        if host is None:
            raise Exception("Invalid host")

        if path is None:
            raise Exception("Invalid path")

        return SshFsCabinet(archive, name, host, path)

RegisterCabinetType(SshFsCabinet)

DEFAULT_ARCHIVE_PATH = os.path.expanduser("~/.archivist")

class Archive(object):

    def __init__(self, path=DEFAULT_ARCHIVE_PATH):
        self.path = path

    def get_cabinet_wd(self, cabinet):
        return os.path.join(self.path, "workdir", cabinet.name)

    @property
    def cabinets_path(self):
        return os.path.join(self.path, "cabinets")

    def get_cabinet(self, name):
        full_path = os.path.join(self.cabinets_path, name)

        if not os.path.isfile(full_path):
            return None

        config = configparser.ConfigParser()
        config.read(full_path)

        cabinet_type = config.get("cabinet", "type", fallback=None)

        if cabinet_type is None:
            raise Exception("Cabinet without type found")

        if cabinet_type not in cabinet_types:
            raise Exception("Unsupported type of cabinet")

        return cabinet_types[cabinet_type].load(self, config, name)

    @property
    def cabinets(self):

        if not os.path.isdir(self.cabinets_path):
            return []

        cabinets = []

        for name in os.listdir(self.cabinets_path):

            cabinet = self.get_cabinet(name)

            if cabinet is None:
                continue

            cabinets.append(cabinet)

        return cabinets

    def add_cabinet(self, name, cabinet_type, args):
        if cabinet_type not in cabinet_types:
            raise Exception("Unsupported type of cabinet")

        cabinet_types[cabinet_type].create(self, name, args)
         

    def init(self):
        if os.path.exists(self.path):
            raise Exception("Archive already exists")
        
        os.makedirs(self.path) 
        os.makedirs(os.path.join(self.path, "workdir"))
        os.makedirs(os.path.join(self.path, "cabinets"))
