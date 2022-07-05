# Implements the tealpkg "remove" command
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


from tealpkg.cli.colorprint import cprint
from tealpkg.core.search import Searcher
from tealpkg.core.transaction import Transaction
from tealpkg.core.transaction.scripts import ScriptHandler
from tealpkg.distro.slackware.pkgtools import Pkgtools


def remove(args, config):
    status = 0

    config.load_package_db()
    searcher = Searcher([], config.package_db, config.file_map)
    packages = searcher.find_package(*args.name, installed=True, available=False)
    if len(packages) > 0:
        pkgtools = Pkgtools(config.installpkg, config.upgradepkg, config.removepkg, args.dry_run, args.quiet, config.log_pkgtools)
        scripts = ScriptHandler(config.scripts, args.dry_run, args.quiet, config.log_scripts)
        transaction = Transaction(pkgtools, config.lockfile, scripts, args.dry_run, args.quiet)
        status = transaction.remove(packages)
    else:
        cprint('No matching packages found.', style='error', stderr=True)
        status = 1
    #

    return status
#
