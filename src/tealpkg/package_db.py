#
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
#

import pathlib

from .package import Package
from .size import parse_size


def load_package_db(path):
    package_map = {}
    file_map = {}

    for item in sorted(pathlib.Path(path).glob('*')):
        parts = item.name.split('-')
        name = '-'.join(parts[0:-3])
        package = Package(name, parts[-3], parts[-2], parts[-1])
        package_map[name] = package

        with open(item.as_posix(), 'r') as fh:
            line = fh.readline()
            in_file_list = False

            while line:
                if line.startswith('COMPRESSED PACKAGE SIZE: '):
                    package.csize = parse_size(line.removeprefix('COMPRESSED PACKAGE SIZE: ').strip())
                elif line.startswith('UNCOMPRESSED PACKAGE SIZE: '):
                    package.usize = parse_size(line.removeprefix('UNCOMPRESSED PACKAGE SIZE: ').strip())
                elif line.startswith(name + ': '):
                    if len(package.desc) == 0:
                        package.short = line.removeprefix(name + ': ').partition('(')[2].rpartition(')')[0].strip()
                    #
                    package.desc.append(line.removeprefix(name + ': ').strip())
                elif line.startswith('FILE LIST:'):
                    in_file_list = True
                elif in_file_list:
                    fpath = '/' + line.strip()
                    if fpath != '/./' and not fpath.startswith('/install/'):
                        package.files.append(fpath)

                        if fpath in file_map:
                            file_map[fpath].append(name)
                        else:
                            file_map[fpath] = [ name ]
                        #
                    #
                #
                line = fh.readline()
            #
        #
    #

    return (package_map, file_map)
#
