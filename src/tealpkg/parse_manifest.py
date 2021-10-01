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

import bz2
import pathlib


def parse_manifest(path_to_manifest):
    manifest = {}
    file_map = {}

    name = ''

    with bz2.open(path_to_manifest, 'rt') as fh:
        line = fh.readline()
        while line:
            if line.startswith('|| '):
                lparts = line.split()
                if len(lparts) == 3:
                    pkgfile = pathlib.PurePosixPath(lparts[2])
                    pieces = pkgfile.stem.split('-')
                    name = '-'.join(pieces[0:-3])
                    manifest[name] = {}
                #
            else:
                lparts = line.split()
                if name and (len(lparts) >= 6):
                    entry = {}
                    entry['permissions'] = lparts[0]
                    entry['owner'] = lparts[1].split('/')[0]
                    entry['group'] = lparts[1].split('/')[1]
                    entry['size'] = lparts[2]
                    entry['date'] = lparts[3]
                    entry['time'] = lparts[4]
                    path = '/' + line.partition(entry['time'])[2].strip()

                    if path != '/./' and not path.startswith('/install/'):
                        manifest[name][path] = entry

                        if path in file_map:
                            file_map[path].append(name)
                        else:
                            file_map[path] = [ name ]
                        #
                    #
                #
            #
            line = fh.readline()
        #
    #
    return (manifest, file_map)
#