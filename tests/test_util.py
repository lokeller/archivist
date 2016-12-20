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



import sync.util

import unittest

import subprocess

class TestProgressMonitor(sync.util.ProgressMonitor):
    def __init__(self, test, expect_out, expect_err):
        self.test = test
        self.expect_err = expect_err
        self.expect_out = expect_out

    def on_error(self, message):
        self._on_data(self.expect_err, message)

    def on_progress(self, message):
        self._on_data(self.expect_out, message)

    def _on_data(self, expected, message):

        if expected is None:
            self.test.fail("Call not expected")
        else:
            self.test.assertEqual(expected[0] + '\n', message)
            del expected[0]

class TestUtils(unittest.TestCase):

    def test_exec_callbacks_stdout(self):

        data = ["a", "b", "c"]

        sync.util.exec(["echo", "-e", r"\n".join(data)], 
                        progress=TestProgressMonitor(self, data, None))

    def test_exec_callbacks_stderr(self):

        data = ["a", "b", "c"]

        sync.util.exec(["sh", "-c", "echo -e " + r"\\n".join(data) + " >&2"], 
                        progress=TestProgressMonitor(self, None, data))

    def test_exec_fail(self):

        try:

            sync.util.exec(["false"]) 
            self.fail("Return code not zero didn't generate exception")

        except subprocess.CalledProcessError:
            pass
