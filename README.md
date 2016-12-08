# archivist

** This tool is not ready for use yet **

## Introduction

The `archivist` tool helps synchronize your files across devices and back them 
up.

To simplify the management of files the tool introduces three concepts:

 - **Folders**: presents itself as a directory in your filesystem. It can be 
    synchronized with others and backed up. Folders can be plain or encrypted.
    If you want to access an encrypted folder you first need to provide a 
    password.

 - **Cabinet**: contains a collection of folders and provides a storage space 
    for them. A cabinet can be stored in a local directory, on a removable 
    device or on a remote server.

 - **Archive**: contains a map of all the user cabinets. By default the archive 
    is stored in the user home directory. The archive doesn't actually contains 
    the cabinets, only information on where they can be found.

The folders support the following operations:

 - **Snapshot**: creates a backup of the current contents of the folder.

 - **Mount**: unlocks encrypted folders making them accessible. Plain folders
    are always mounted.

 - **Unmount**: locks encrypted folders making them in-accessible

 - **Clone**: creates a clone of a folder, when you perform a sync of a folder,
    all currently accessible clones will be synchronized.

 - **Sync**: synchronizes the folder with all its clones. All changes done to 
    the folder and all its clones are merged and applied to all.

The cabinets support the following operations:

 - **Mount**: makes the cabinet accessible, useful to access cabinets on remote 
    computers. Local cabinets are always mounted.

 - **Unmount**: disconnects mounted cabinets

 - **Create folder**: creates a folder (either encrypted or plain) in the
     cabinet

 - **Sync all folders**: perform synchronization of all the folders in the 
    cabinet

 - **Snapshot all folders**: perform a snapshot of all the folders in the 
    cabinet

The archive supports the following operations:

 - **Add a cabinet**: insert information on how to reach a cabinet in the 
   archive

## How to use

You can test the tool with the following commands:

```
PYTHONPATH="."
bin/archivist --help
```

The GUI (it is a tray icon) can be started as follows:

```
PYTHONPATH="."
bin/archivist gui
```

## License

The license information can be found in `COPYING`. The software is Copyright 2016 Lorenzo Keller (lorenzo@nodo.ch)

## Implementation

The `archivist` tool uses the following technologies:

 - **Language**: the tool is written in Python 3
 - **Synchronization and backup**: the tool relies on `git-annex` (v6)
 - **Encrypted folders**: the tool relies on `encfs`
 - **Remote cabinets**: the tool relies on `sshfs`
 - **GUI**: the tool relies on Gtk
