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
from ..search import Searcher


def search(args, config):
    status = 0

    config.load_all()
    searcher = Searcher(config.repolist, config.package_db, config.file_map, config.exclude_file, args.include, args.exclude)
    response = searcher.search_package(*args.query)
    status = 0 if len(response) > 0 else 1
    for name in response:
        pair = response[name]
        if pair.available and pair.available.repo:
            cprint(pair.available.repo + '/', style='reponame', end='')
        #
        cprint(name, style='pkgname', end=' ')
        if pair.installed:
            cprint(pair.installed.version, pair.installed.build, style='version', sep='-', end='')
            cprint(' [installed]', style='installed', end='')
            if pair.has_upgrade():
                cprint(' (available: ' + pair.available.version + '-' + pair.available.build + ')', style='available', end='')
            #
        else:
            cprint(pair.available.version, pair.available.build, style='version', sep='-', end='')
        #
        if pair.available and pair.available.group:
            cprint(' (' + pair.available.group + '/)', style='group', end='')
        #
        cprint()
        if pair.installed:
            cprint('    ' + pair.installed.short)
        else:
            cprint('    ' + pair.available.short)
        #
    #

    return status
#
