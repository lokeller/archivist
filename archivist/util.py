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


import subprocess
import threading
import os
import io
import queue

class ProgressMonitor():
    """
    Monitors the progress of a command
    """
    def on_error(message):
        pass
    def on_progress(message):
        pass

def exec(command, wd=None, progress=None):
    """
    Execute a command and while returning each line of stdout and stderr to 
    a progress monitor.
 
    The function blocks until the command exits.

    The progress monitor receives every line of stdout and stderr 
    (with new line character  included).

    The progress monitor calls are executed in the same thread as the the
    exec function is executed.

    The function raises an exception subprocess.CalledProcessError if the
    command doesn't exit with 0 return code.
    """

    fdout = None if progress is None else subprocess.PIPE

    proc = subprocess.Popen(command, bufsize=1, # line buffering
                                cwd=wd, stdout=fdout, stderr=fdout)


    # this queue contains all the tasks that the threads that read stderr and
    # stdout would like to run in the execution context of the exec() function
    tasks = queue.Queue(100)

    # these are the threads that will read stderr and stdout
    threads = []

    # this function starts a thread that will schedule callback to be called
    # each time a line is present on fd

    # DESIGN: it is maybe possible to get rid of these threads
    # and use select instead but it is not clear how to handle text decoding
    def start_thread(fd, callback):

        # this function calls a callback once for each line that it can read
        def process():
            try:
                with io.TextIOWrapper(fd, encoding="utf-8") as stream:
                    for line in stream:
                        # schedule a call to the callback
                        tasks.put( lambda line=line: callback(line))
            finally:
                # just before exiting we put an empty task in the list
                # so that exec() can notice we are done
                tasks.put(None)
                
        # create and start the thread
        t = threading.Thread(target=process)
        t.start()
        threads.append(t)

    if progress is not None:
        start_thread(proc.stdout, progress.on_progress)
        start_thread(proc.stderr, progress.on_error)

    # execute all tasks that the threads ask us to notify
    finished = 0
    while finished < len(threads):
        task = tasks.get()
        if task is None:
            finished = finished+1
        else:
            task()

    # wait for the threads to be completely shutdown
    for t in threads: t.join()

    # wait until the process is done (it may run for a while after it closes 
    # stdout/stderr)
    proc.wait()

    if proc.returncode != 0:
        raise subprocess.CalledProcessError(proc.returncode, command)
