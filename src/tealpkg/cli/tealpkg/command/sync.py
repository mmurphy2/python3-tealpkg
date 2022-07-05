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


from ..colorprint import cprint
from ..pkgtools import Pkgtools
from ..scripts import ScriptHandler
from ..search import Searcher
from ..transaction import Transaction


def sync(args, config):
    status = 0

    if config.load_all():
        searcher = Searcher(config.repolist, config.package_db, config.file_map, config.exclude_file, args.include, args.exclude)

        query = args.name
        if len(query) == 0:
            query = [ '*' ]
        #

        packages = searcher.find_package(*query, only_upgrades=True)
        if len(packages) > 0:
            pkgtools = Pkgtools(config.installpkg, config.upgradepkg, config.removepkg, args.dry_run, args.quiet, config.log_pkgtools)
            scripts = ScriptHandler(config.scripts, args.dry_run, args.quiet, config.log_scripts)
            transaction = Transaction(pkgtools, config.lockfile, scripts, args.dry_run, args.quiet)
            status = transaction.upgrade(packages)
        else:
            if len(args.name) == 0:
                # Running tealpkg sync by itself is not an error if no updates are available. This way, it can be run with
                # stdout suppressed from cron, without generating spurious error messages.
                cprint('Already up to date.')
            else:
                # If the user is using -q with a specific package set, it might also be a cron job.
                if not args.quiet:
                    # Display an error in the general case.
                    cprint('No matching packages found for update.', style='error', stderr=True)
                    status = 1
                #
            #
        #
    else:
        status = 1
    #

    return status
#
