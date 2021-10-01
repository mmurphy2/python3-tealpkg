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


import os


from ..colorprint import cprint
from ..pkgtools import Pkgtools
from ..scripts import ScriptHandler
from ..search import Searcher
from ..tagfile import parse_tagfile
from ..transaction import Transaction


def install(args, config):
    status = 0
    prune = []
    if config.load_all():
        searcher = Searcher(config.repolist, config.package_db, config.file_map, config.exclude_file, args.include, args.exclude)
        all_names = args.name
        if args.tagfile:
            all_names = []
            for tagfile in args.name:
                if os.path.exists(tagfile):
                    pkgnames = parse_tagfile(tagfile, optional=args.optional)
                    for item in pkgnames:
                        if item not in all_names:
                            all_names.append(item)
                    #####
                else:
                    cprint('File not found:', tagfile, style='error')
                    status = 1
            #####
        #

        package_pairs = searcher.find_package(*all_names)
        if len(package_pairs) > 0:
            for name in sorted(package_pairs):
                if package_pairs[name].installed:
                    if args.reinstall:
                        if package_pairs[name].has_upgrade():
                            cprint(name, 'is already installed but cannot be reinstalled due to available upgrade', style='error', stderr=True)
                            status = 1
                        else:
                            cprint(name, 'is already installed: reinstalling', style='warning', stderr=True)
                        #
                    else:
                        cprint(name, 'is already installed', style='error', stderr=True)
                        prune.append(name)
                    #
            #####

            for name in prune:
                del package_pairs[name]
            #

            if status == 0 and len(package_pairs) > 0:
                pkgtools = Pkgtools(config.installpkg, config.upgradepkg, config.removepkg, args.dry_run, args.quiet, config.log_pkgtools)
                scripts = ScriptHandler(config.scripts, args.dry_run, args.quiet, config.log_scripts)
                transaction = Transaction(pkgtools, config.lockfile, scripts, args.dry_run, args.quiet)
                status = transaction.install(package_pairs)
            #
        else:
            cprint('No matching packages found.', style='error', stderr=True)
            status = 1
        #
    else:
        status = 1
    #

    return status
#
