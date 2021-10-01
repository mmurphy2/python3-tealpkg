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
import shlex
import subprocess
import time

from .colorprint import cprint
from .run import log_run

INSTALLPKG = '/sbin/upgradepkg --install-new'
UPGRADEPKG = '/sbin/upgradepkg'
REMOVEPKG = '/sbin/removepkg'


class Pkgtools:
    def __init__(self, installpkg=INSTALLPKG, upgradepkg=UPGRADEPKG, removepkg=REMOVEPKG, dry_run=False, quiet=False, log_output=False):
        self.installpkg = shlex.split(installpkg)
        self.upgradepkg = shlex.split(upgradepkg)
        self.removepkg = shlex.split(removepkg)
        self.dry_run = dry_run
        self.quiet = quiet
        self.log_output = log_output
        self.log = logging.getLogger(__name__)
    #
    def run(self, args):
        status = 0

        if self.dry_run:
            cprint('DRY RUN:', ' '.join(args), style='notice')
            time.sleep(1)
        else:
            status = log_run(args, self.quiet, self.log_output)
            if status != 0:
                self.log.error('Process returned error code: %d', status)
            #
        #

        return status
    #
    def install(self, package_path):
        return self.run(self.installpkg + [ package_path ])
    #
    def upgrade(self, package_path):
        return self.run(self.upgradepkg + [ package_path ])
    #
    def remove(self, package_name):
        return self.run(self.removepkg + [ package_name ])
    #
#
