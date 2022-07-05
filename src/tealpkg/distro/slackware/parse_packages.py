# Function to parse the Slackware PACKAGES.TXT file.
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


import calendar
import pathlib
import time

from tealpkg.core.package import Package
from tealpkg.util.size import parse_size

from .pkgtools import splitpkg


def parse_packages(path_to_packages, repoid='', extract_groups=False, strip_path=0):
    result = {}
    package = None

    with open(path_to_packages, 'r', encoding='utf-8', errors='replace') as fh:
        line = fh.readline()
        while line:
            if line.startswith('PACKAGES.TXT; '):
                timestamp = calendar.timegm(time.strptime(' '.join(line.split()[1:]), '%a %b %d %H:%M:%S %Z %Y'))
            elif line.startswith('PACKAGE NAME: '):
                pkgfile = pathlib.PurePosixPath(line.split()[2])
                info = splitpkg(pkgfile.stem)
                if info:
                    package = Package(info.name, info.version, info.architecture, info.build)
                    package.repo = repoid
                    result[info.name] = package
                #
            elif package:
                if line.startswith('PACKAGE LOCATION: '):
                    pkgpath = pathlib.PurePosixPath(line.split()[2])
                    pkgpath = pathlib.PurePosixPath(*pkgpath.parts[strip_path:])
                    relpath = pkgpath.joinpath(pkgfile)
                    if extract_groups:
                        package.group = relpath.parts[-2]
                    #
                    package.relpath = relpath.as_posix()
                elif line.startswith('PACKAGE SIZE (compressed): '):
                    package.csize = parse_size(' '.join(line.split()[3:]))
                elif line.startswith('PACKAGE SIZE (uncompressed): '):
                    package.usize = parse_size(' '.join(line.split()[3:]))
                elif line.startswith(info.name + ': '):
                    if len(package.desc) == 0:
                        package.short = line.partition('(')[2].rpartition(')')[0].strip()
                    #
                    package.desc.append(line.removeprefix(info.name + ': ').strip())
                elif line == '\n':
                    package = None
                #
            #
            line = fh.readline()
        #
    #

    return (result, timestamp)
#
