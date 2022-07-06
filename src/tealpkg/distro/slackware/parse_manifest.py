# Function for parsing the Slackware MANIFEST.bz2 file.
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


import bz2
import pathlib

from .pkgtools import splitpkg


def parse_manifest(path_to_manifest):
    manifest = {}
    file_map = {}

    info = None

    with bz2.open(path_to_manifest, 'rt') as fh:
        line = fh.readline()
        while line:
            fields = line.split(maxsplit=5)
            if len(fields) == 3 and fields[0] == '||' and fields[1] == 'Package:':
                pkgfile = pathlib.PurePosixPath(fields[2])
                info = splitpkg(pkgfile.stem)
                if info:
                    manifest[info.name] = {}
                #
            else:
                if info and len(fields) == 6:
                    path = '/' + fields[5].rstrip()
                    if path != '/./' and not path.startswith('/install/'):
                        owner, group = fields[1].split('/')
                        entry = {
                            'permissions': fields[0],
                            'owner': owner,
                            'group': group,
                            'size': fields[2],
                            'date': fields[3],
                            'time': fields[4],
                        }

                        manifest[info.name][path] = entry

                        if path in file_map:
                            file_map[path].append(info.name)
                        else:
                            file_map[path] = [ info.name ]
                        #
                    #
                #
            #
            line = fh.readline()
        #
    #
    return (manifest, file_map)
#


# Unit testing code
if __name__ == '__main__':
    import sys
    import time

    manifest, file_map = parse_manifest(sys.argv[1])
    print(manifest)
    print(file_map)
#
