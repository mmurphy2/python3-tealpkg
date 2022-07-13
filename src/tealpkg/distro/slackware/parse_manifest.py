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
import os
import pathlib
import sqlite3

from .pkgtools import splitpkg


def parse_manifest(path_to_manifest, output_database_path):
    manifest = {}
    file_map = {}

    info = None

    if os.path.lexists(output_database_path):
        os.remove(output_database_path)
    #

    db = sqlite3.connect(output_database_path)
    cursor = db.cursor()

    cursor.execute('''CREATE TABLE 'manifest' (
        'package' TEXT,
        'path' TEXT,
        'owner' TEXT,
        'group' TEXT,
        'permissions' TEXT,
        'size' TEXT,
        'date' TEXT,
        'time' TEXT);''')
    #
    db.commit()

    with bz2.open(path_to_manifest, 'rt') as fh:
        for line in fh:
            fields = line.split(maxsplit=5)
            if len(fields) == 3 and fields[0] == '||' and fields[1] == 'Package:':
                pkgfile = pathlib.PurePosixPath(fields[2])
                info = splitpkg(pkgfile.stem)
            else:
                if info and len(fields) == 6:
                    path = '/' + fields[5].rstrip()
                    if path != '/./' and not path.startswith('/install/'):
                        owner, group = fields[1].split('/')
                        cursor.execute('''INSERT OR REPLACE INTO "manifest" VALUES (?, ?, ?, ?, ?, ?, ?, ?);''',
                                       (info.name, path, owner, group, fields[0], fields[2], fields[3], fields[4]))
                        #
                    #
                #
            #
        #
    #
    db.commit()
    db.close()
#


# Unit testing code
if __name__ == '__main__':
    import sys
    import time

    start = time.time()
    parse_manifest(sys.argv[1], sys.argv[2])
    end = time.time()

    print(end - start)
#
