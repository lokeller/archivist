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

import archivist.util
import os
from urllib.parse import urlparse
import configparser
import subprocess
import uuid

folder_types = {}

def RegisterFolderType(clazz):
    folder_types[clazz.type_name] = clazz

class Folder(object):

    type_name = "plain"

    creation_args = []
    mount_args = []

    def __init__(self, cabinet, name, config):
        self.cabinet = cabinet
        self.storage_path = os.path.join(cabinet.access_path, name)
        self.config = config

    @property
    def name(self):
        return os.path.relpath(self.storage_path, self.cabinet.access_path)

    @property
    def access_path(self):
        return self.storage_path

    @property
    def supports_unmount(self):
        return False

    def mount(self, args=None, progress=None):
        pass

    def unmount(self, progress=None):
        pass

    @property
    def is_mounted(self):
        return True

    def snapshot(self, progress=None):
        self._do_commit(allowEmpty=True, progress=progress)


    def _do_commit(self, allowEmpty=False, progress=None):
        progress and progress.on_progress("Adding all changes\n")

        archivist.util.exec(['git', 'add', '-v', '--all', '.'], 
                            wd=self.storage_path, progress=progress)
        progress and progress.on_progress("Committing all changes\n")
        
        cmd = ['git', 'commit', '-q', '-m', 'Snapshot']

        if allowEmpty:
            cmd.append('--allow-empty')
        else:
            changes = subprocess.check_output(['git', 'status', '--porcelain'], cwd=self.storage_path)
            if changes.strip() == b'':
                progress and progress.on_progress("Nothing changed, skipping commit\n")
                return
        
        archivist.util.exec(cmd, wd=self.storage_path, progress=progress)

        progress and progress.on_progress("Done\n")


    def _do_sync(self, progress=None):
        archivist.util.exec(['git', 'annex', 'sync', '--content'], 
                            wd=self.storage_path, progress=progress)

    def sync(self, progress=None):        

        clones_uuids = self.clones_uuids

        syncable_folders = self.cabinet.archive.syncable_folders

        syncable_clones = [ x for x in syncable_folders if x.group_uuid == self.group_uuid and x.uuid != self.uuid]

        progress and progress.on_progress("Connecting with all accessible clones\n")

        for clone in syncable_clones :
            archivist.util.exec(['git', 'remote', 'add', '-f', 'archivist.' + clone.uuid, clone.storage_path], 
                                wd=self.storage_path, progress=progress)

        try:

            # in order to sync we need to make sure all changes are commited on all clones
            for clone in syncable_clones :
                clone._do_commit(progress)

            # save all local changes too
            self._do_commit(progress)

            progress and progress.on_progress("Performing sync\n")

            self._do_sync(progress)

            # we need to sync on the remotes to make changes appear also there
            for clone in syncable_clones :
                clone._do_sync(progress)

        finally:

            progress and progress.on_progress("Disconnecting from clones\n")

            for clone in syncable_clones :
                archivist.util.exec(['git', 'remote', 'remove', 'archivist.' + clone.uuid], 
                                    wd=self.storage_path, progress=progress)

        progress and progress.on_progress("Done")


    def _init_annex(cls, dirname, args, progress):
        archivist.util.exec(['git', 'annex', 'init', '--version=6'], 
                wd=dirname, progress=progress)

        # create first commit so that we are sure we can switch to the adjusted branch
        archivist.util.exec(['git', 'commit', '--allow-empty', '-m', 'Created folder', '-q'], 
                wd=dirname, progress=progress)

        # get the current HEAD
        with open(os.path.join(dirname, ".git", "HEAD")) as fp:
            branch = fp.read().strip()

        # if the repo is not in adjusted unlocked mode switch to it
        # it may be in adjusted unlocked mode if git-annex detected
        # a crippled filesystem
        if branch != "ref: refs/heads/adjusted/master(unlocked)":
            archivist.util.exec(['git', 'annex', 'adjust', '--unlock'], 
                    wd=dirname, progress=progress)

        config = configparser.ConfigParser()

        args['type'] = cls.type_name
        config['folder'] = args

        with open(os.path.join(dirname, '.git', 'archivist'), 'w') as configfile:
           config.write(configfile)

    def clone(self, dest_cabinet, dest_name, progress=None):
        progress and progress.on_progress("Cloning folder\n")

        dirname = dest_cabinet.reserve_folder_name(dest_name)

        archivist.util.exec(['git', 'clone', self.storage_path, dirname], 
                            progress=progress)

        args = {'groupUuid' : self.group_uuid}
        type(self)._init_annex(type(self), dirname, args, progress)

        dest_cabinet.get_folder(dest_name).sync(progress)

        progress and progress.on_progress("Done")
    
    @property
    def clones_uuids(self):
        remotes = subprocess.check_output(
                        ["git", "cat-file", "blob", "git-annex:uuid.log"], 
                         cwd=self.storage_path)

        uuids = []

        for remote in remotes.decode("utf-8").strip().split("\n"):
            uuids.append(remote.split(" ", 1)[0])
        
        return uuids

    @property
    def group_uuid(self):
        return self.config['folder']['groupUuid']

    @property
    def uuid(self):
        return subprocess.check_output(["git", "config", "annex.uuid"], cwd=self.storage_path).decode("utf-8").strip()

    @classmethod
    def load(cls, cabinet, name, config):
        return Folder(cabinet, name, config)

    @classmethod
    def create(cls, cabinet, name, args, progress=None):

        dirname = cabinet.reserve_folder_name(name)

        archivist.util.exec(['git', 'init', '.'], 
                wd=dirname, progress=progress)

        args["groupUuid"] = uuid.uuid4()

        cls._init_annex(cls, dirname, args, progress)



RegisterFolderType(Folder)

class EncryptedFolder(Folder):

    type_name = "encrypted"
    creation_args = []
    mount_args = ["password_program"]

    def __init__(self, cabinet, storage_path, config):
        Folder.__init__(self, cabinet, storage_path, config)

    @property
    def access_path(self):
        return self.storage_path + ".Decrypted"

    @property
    def supports_unmount(self):
        return True

    def mount(self, args=None, progress=None):

        if self.is_mounted:
            raise Exception("Already mounted")

        if not os.path.isdir(self.access_path):
            os.makedirs(self.access_path)

        cmd_line = ['encfs', '--standard', '-i', '10' ]

        if args is not None and "password_program" in args:
            cmd_line.append('--extpass=' + args['password_program'])

        cmd_line.extend([self.storage_path, self.access_path])

        archivist.util.exec(cmd_line, progress=progress)

    def unmount(self, progress=None):
        archivist.util.exec(['fusermount', '-u', self.access_path], progress=progress)

        if os.listdir(self.access_path) == []:
            os.rmdir(self.access_path)

    @property
    def is_mounted(self):
        return os.path.ismount(self.access_path)

    @classmethod
    def load(cls, cabinet, name, config):
        return EncryptedFolder(cabinet, name, config)


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

    def reserve_folder_name(self, name):
        """
        Reserves a folder name

        This function checks if a folder name is valid and then
        tries to create it. The function fails with an exception
        if the name is invalid or the folder already exists.

        Returns the absolute path to the folder storage path.
        """
        abs_cabinet_path = os.path.abspath(self.access_path)
        dirname = os.path.abspath(os.path.join(abs_cabinet_path, name))
        
        if os.path.relpath(dirname, abs_cabinet_path) != name:
            raise Exception("Invalid name")

        os.makedirs(dirname)

        return dirname

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

            folder_name = os.path.relpath(dirpath, self.access_path)

            # skip trash folder
            if folder_name.startswith('.Trash'):
                del dirnames[:]
                continue

            folder = self.get_folder(folder_name)

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

    def delete(self):
        config_path = os.path.join(self.archive.cabinets_path, self.name)
        os.unlink(config_path)

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
    def syncable_folders(self):

        syncable_folders = []

        for cabinet in self.cabinets:
            if not cabinet.is_mounted:
                continue

            syncable_folders.extend(cabinet.folders)

        return syncable_folders

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

    def exists(self):
        return os.path.exists(self.path)

    def init(self):
        if os.path.exists(self.path):
            raise Exception("Archive already exists")
        
        os.makedirs(self.path) 
        os.makedirs(os.path.join(self.path, "workdir"))
        os.makedirs(os.path.join(self.path, "cabinets"))
