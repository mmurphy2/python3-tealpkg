# Copyright 2021 Coastal Carolina University
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


import logging
import pathlib
import subprocess
import tempfile
import time

from .colorprint import cprint
from .filetest import is_executable
from .run import log_run


class ScriptHandler:
    def __init__(self, script_path, dry_run=False, quiet=False, log_script_output=False):
        self.script_path = pathlib.PosixPath(script_path)
        self.dry_run = dry_run
        self.quiet = quiet
        self.log_script_output = log_script_output
        self.log = logging.getLogger(__name__)
    #
    def run(self, args):
        status = 0

        if self.dry_run:
            cprint('DRY RUN:', ' '.join(args), style='notice')
            time.sleep(1)
        else:
            status = log_run(args, self.quiet, self.log_script_output)
            if status != 0:
                self.log.error('Process returned error code: %d', status)
            #
        #

        return status
    #
    def find_scripts(self):
        script_list = []
        resolved_set = set()

        for item in self.script_path.glob('*'):
            resolved = item.resolve()
            if resolved not in resolved_set:
                if resolved.is_file() and is_executable(resolved):
                    script_list.append(item)
                #
                resolved_set.add(resolved)
        #####

        script_list.sort(key=lambda p: p.name)
        return script_list
    #
    def run_scripts(self, operation, package_pairs):
        status = 0
        script_list = self.find_scripts()
        if len(script_list) > 0:
            with tempfile.TemporaryDirectory() as tempdir:
                base = pathlib.PosixPath(tempdir)
                with open(base.joinpath('packages'), 'w') as fh:
                    for name in sorted(package_pairs):
                        package = package_pairs[name].available
                        if operation == 'remove':
                            package = package_pairs[name].installed
                        #
                        fh.write(name + ' ' + package.version + ' ' + package.arch + ' ' + package.build + '\n')
                #####

                sindex = 0
                for script in script_list:
                    cprint('Running script', style='action', end=' ')
                    cprint(script.name, style='target', end='')
                    cprint('...', style='default')
                    args = [ script.as_posix(), operation, base.joinpath('packages').as_posix() ]
                    check = self.run(args)
                    if check != 0:
                        status = check
                    #
                    sindex += 1
                #
        #

        return status
    #
#
