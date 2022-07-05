# Implementation of the tealpkg "info" and "list" commands
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


import textwrap

from tealpkg.cli.colorprint import cprint, get_width
from tealpkg.core.search import Searcher
from tealpkg.distro.slackware.tagfile import write_tagfile
from tealpkg.util.size import friendly_size


def print_info(name, package_pair):
    status = 0

    package = package_pair.available
    state = 'available'
    if package_pair.installed:
        package = package_pair.installed
        state = 'installed'
    #

    cprint('Name:               ', style='info_label', end='')
    cprint(name, style='info_item')
    cprint('Summary:            ', style='info_label', end='')
    cprint(package.short, style='info_item')
    cprint('Status:             ', style='info_label', end='')
    cprint(state, style='info_item')
    cprint('Version:            ', style='info_label', end='')
    cprint(package.version, package.build, sep='-', style='info_item')
    if package_pair.has_upgrade():
        cprint('Available Upgrade:  ', style='info_label', end='')
        cprint(package_pair.available.version, package_pair.available.build, sep='-', style='info_item')
    #
    cprint('Architecture:       ', style='info_label', end='')
    cprint(package.arch)
    cprint('Repository:         ', style='info_label', end='')
    if package_pair.available and package_pair.available.repo:
        cprint(package_pair.available.repo, style='info_item')
    else:
        cprint('(not available)', style='info_item')
    #
    cprint('Description:        ', style='info_label', end='')
    indt = '                    '
    lines = textwrap.wrap(' '.join(package.desc[1:]), width=get_width(), initial_indent=indt, subsequent_indent=indt)
    if len(lines) > 0:
        counter = 0
        for line in lines:
            if counter == 0:
                cprint(line.strip(), style='info_item')
            else:
                cprint(line, style='info_item')
            #
            counter += 1
        #
    else:
        cprint('(not available)', style='info_item')
    #
    cprint('Files:              ', style='info_label', end='')
    if len(package.files) > 0:
        cprint()
        for item in package.files:
            cprint(indt, item, style='info_item', sep='')
        #
    else:
        cprint('(none)', style='info_item')
    #
    csize = friendly_size(package.csize)
    usize = friendly_size(package.usize)
    spaces = len(usize) - len(csize)
    cprint('Package Size:       ', style='info_label', end='')
    cprint(max(spaces, 0) * ' ', csize, style='info_item', sep='')
    cprint('Installed Size:     ', style='info_label', end='')
    cprint(abs(min(spaces, 0)) * ' ', usize, style='info_item', sep='')

    return status
#


def info_list(args, config):
    config.load_package_db()
    config.load_repos()
    searcher = Searcher(config.repolist, config.package_db, config.file_map, config.exclude_file, args.include, args.exclude)

    query = args.names
    if len(query) == 0:
        query = [ '*' ]
    #

    installed = True
    available = True
    only_upgrades = False
    only_extras = False

    if args.limit == 'available':
        installed = False
    elif args.limit == 'extras':
        only_extras = True
    elif args.limit == 'installed':
        available = False
    elif args.limit == 'upgrades':
        only_upgrades = True
    #

    if available:
        config.load_metadata()
    #

    package_pairs = searcher.find_package(*query, installed=installed, available=available, only_upgrades=only_upgrades, \
            only_extras=only_extras)

    if args.command == 'list':
        if args.tagfile:
            write_tagfile(args.tagfile, sorted(package_pairs), args.tagaction)
        else:
            for name in sorted(package_pairs):
                cprint(name, style='list_item')
            #
        #
    else:
        for name in sorted(package_pairs):
            print_info(name, package_pairs[name])
        #
    #
#
