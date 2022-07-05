# Transaction wrapper for installing/upgrading/removing packages.
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

# TODO: refactor to MVC

import collections
import logging
import os
import signal
import sys

from tealpkg.cli.colorprint import cprint
from tealpkg.cli.progress_bar import ProgressBar
from tealpkg.cli.status_line import StatusLine
from tealpkg.cli.transaction_prompt import prompt_install, prompt_remove

from .lock import TransactionLock


# When using SIGHUP protection to guard against an SSH connection (running tealpkg) dropping in the
# middle of a transaction, we need to set stdout and stderr to /dev/null to prevent exceptions
# whenever data are written to the streams. This way, the transaction can run to completion, instead
# of leaving the system in a partially-modified state.
def sighup(signum, frame):
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, sys.stdout.fileno())
    os.dup2(devnull, sys.stderr.fileno())
#


class Transaction:
    def __init__(self, pkgtools, lockfile, scripts=None, dry_run=False, quiet=False, prompt=True):
        self.pkgtools = pkgtools
        self.lock = TransactionLock(lockfile)
        self.scripts = scripts
        self.dry_run = dry_run
        self.quiet = quiet
        self.prompt = prompt
        self.status_line = StatusLine()
        self.log = logging.getLogger(__name__)
    #
    def enable_status(self):
        if not self.quiet:
            self.status_line.enable()
        #
    #
    def disable_status(self):
        if not self.quiet:
            self.status_line.disable()
        #
    #
    def progress_bar(self, label, current, final):
        if not self.quiet:
            self.status_line.enter()
            progress_bar = ProgressBar(label)
            progress_bar.print_progress(current, final)
            self.status_line.leave()
        #
    #
    def resolve_install(self, package_pairs):
        ok = True
        install_map = collections.OrderedDict()

        total_size = 0
        for name in package_pairs:
            total_size += package_pairs[name].available.csize
        #

        completed_size = 0
        self.enable_status()
        for name in sorted(package_pairs):
            package = package_pairs[name].available
            self.progress_bar('Obtaining ' + name, completed_size, total_size)
            fp = package.filepath
            completed_size += package.csize
            path = fp.resolve()
            if not path:
                cprint('Could not resolve file for', name, style='error', stderr=True)
                self.log.error('Cannot install or upgrade %s: path not resolved', name)
                ok = False
            else:
                install_map[name] = path
            #
        #
        self.status_line.disable()

        if not ok:
            install_map = {}
        #

        return install_map
    #
    def begin_transaction(self):
        ok = self.lock.lock()
        if ok:
            signal.signal(signal.SIGHUP, sighup)
        #
        return ok
    #
    def end_transaction(self):
        ok = self.lock.unlock()
        signal.signal(signal.SIGHUP, signal.SIG_DFL)
        return ok
    #
    def install(self, package_pairs, upgrade=False):
        status = 0

        if self.prompt:
            status = prompt_install(package_pairs, upgrade)
        #

        if status == 0:
            install_map = self.resolve_install(package_pairs)
            if install_map:
                # TODO: move this logic into distro
                # Certain packages should be upgraded first. Per the Slackware 15.0 UPGRADE.TXT
                # file (as of July 17, 2021), these are: aaa_glibc-solibs, pkgtools, tar, xz,
                # findutils. We need to do these in reverse order, as the OrderedDict allows
                # us to move things easily to the beginning of the list.
                for name in ('findutils', 'xz', 'tar', 'pkgtools', 'aaa_glibc-solibs'):
                    if name in install_map:
                        install_map.move_to_end(name, last=False)
                #####

                if self.begin_transaction():
                    self.enable_status()
                    try:
                        insindex = 0
                        for name in install_map:
                            if upgrade:
                                self.log.info('Upgrading: %s', name)
                            else:
                                self.log.info('Installing: %s', name)
                            #

                            disp = 'Upgrading' if upgrade else 'Installing'
                            self.progress_bar(disp + ' ' + name, insindex, len(install_map))

                            if not self.quiet:
                                cprint()
                                cprint(disp, style='action', end=' ')
                                cprint(name, style='target', end='')
                                cprint('...', style='default')
                            #

                            if upgrade:
                                check = self.pkgtools.upgrade(install_map[name])
                            else:
                                check = self.pkgtools.install(install_map[name])
                            #

                            if check != 0:
                                cprint('Operation error when processing', name, style='error', stderr=True)
                                status = check
                            #

                            insindex += 1
                        #
                    finally:
                        self.disable_status()
                    #

                    if self.scripts:
                        operation = 'upgrade' if upgrade else 'install'
                        check = self.scripts.run_scripts(operation, package_pairs)
                        if check != 0:
                            status = check
                        #
                    #

                    if not self.end_transaction():
                        cprint('Failed to release transaction lock', style='error', stderr=True)
                        status = 1
                    #

                    if not self.quiet:
                        for name in install_map:
                            for entry in package_pairs[name].available.files:
                                if entry.endswith('.new') and os.path.exists(entry):
                                    cprint('NEW:', entry, style='warning')
                    #############
                else:
                    cprint('Could not acquire transaction lock: is tealpkg already running?', style='error', stderr=True)
                    status = 1
                #

                if status == 0:
                    self.log.info('Transaction completed successfully')
                else:
                    self.log.error('Transaction failed with status %d', status)
        #########

        return status
    #
    def upgrade(self, package_pairs):
        return self.install(package_pairs, upgrade=True)
    #
    def remove(self, package_pairs):
        status = 0

        if self.prompt:
            status = prompt_remove(package_pairs)
        #

        if status == 0:
            if self.begin_transaction():
                self.enable_status()
                try:
                    rindex = 0
                    for name in sorted(package_pairs):
                        self.progress_bar('Removing ' + name, rindex, len(package_pairs))
                        self.log.info('Removing: %s', name)

                        if not self.quiet:
                            cprint('Removing', style='action', end=' ')
                            cprint(name, style='target', end='')
                            cprint('...', style='default')
                        #

                        check = self.pkgtools.remove(name)
                        if check != 0:
                            status = check
                        #

                        rindex += 1
                    #
                finally:
                    self.disable_status()
                #

                if self.scripts:
                    check = self.scripts.run_scripts('remove', package_pairs)
                    if check != 0:
                        status = check
                    #
                #

                if not self.end_transaction():
                    cprint('Failed to release transaction lock', style='error', stderr=True)
                    status = 1
                #
            else:
                cprint('Could not acquire transaction lock: is tealpkg already running?', style='error', stderr=True)
                status = 1
            #

            if status == 0:
                self.log.info('Transaction completed successfully')
            else:
                self.log.error('Transaction failed with status %d', status)
            #
        #

        return status
    #
#
