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


import fnmatch

from ..colorprint import cprint
from ..search import Searcher


def provides(args, config):
    status = 0

    config.load_all()
    searcher = Searcher(config.repolist, config.package_db, config.file_map, config.exclude_file, args.include, args.exclude)

    for query in args.file:
        found = searcher.search_file(query)
        if len(found) > 0:
            cprint(query, style='heading')
            for name in sorted(found):
                cprint('    ' + name, style='pkgname')
                fquery = query
                if fquery[0] not in ('/', '*'):
                    fquery = '*' + fquery
                #
                package = found[name].installed
                if not package:
                    package = found[name].available
                #
                for filename in fnmatch.filter(package.files, fquery):
                    cprint('        ' + filename, style='list_item')
                #
            #
        else:
            status=1
    #####

    return status
#
