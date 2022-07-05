# Transaction locking code.
#
# Copyright 2021-2022 Coastal Carolina University
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.


import os
import pathlib


class TransactionLock:
    def __init__(self, lockfile):
        self.path = pathlib.PosixPath(lockfile)
    #
    def check_lock(self):
        result = False
        if self.path.exists():
            this_pid = os.getpid()
            check_pid = 0
            with open(self.path, 'r') as fh:
                check_pid = int(fh.read().strip())
            #
            if this_pid == check_pid:
                # We already hold the lock
                result = True
            else:
                # See if we have a stale lock
                # TODO: improve this logic
                procpath = pathlib.PosixPath('/proc').joinpath(str(check_pid))
                if procpath.exists():
                    data = ''
                    with open(procpath.joinpath('status')) as fh:
                        data = fh.read()
                    #
                    if 'python' not in data:
                        # pid has been reused, so it should be safe to clean up the lock file
                        result = True
                        self.path.unlink(missing_ok=True)
                    #
                else:
                    # Stale lock: clean it up
                    result = True
                    self.path.unlink(missing_ok=True)
            #####
        else:
            # Not locked, so we're good to proceed
            result = True
        #
        return result
    #
    def lock(self):
        result = False
        if self.check_lock():
            with open(self.path, 'w') as fh:
                pid = os.getpid()
                fh.write(str(pid) + '\n')
            #

            # We really shouldn't have a close race condition with this application, since it is anticipated that the
            # system administrator will run it manually (or perhaps via cron, but even then not especially frequently).
            result = self.check_lock()
            if result:
                self.in_transaction = True
            #
        #

        return result
    #
    def unlock(self):
        result = False

        # Check that we're the process holding the lock
        if self.check_lock():
            self.path.unlink(missing_ok=True)
            result = True
            self.in_transaction = False
        #

        return result
    #
#
