# Functions for reading and writing Slackware installation tagfiles.
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


import time


def parse_tagfile(filepath, optional=False):
    result = []
    pick = [ 'ADD' ]
    if optional:
        pick.append('OPT')
    #

    with open(filepath, 'r') as fh:
        line = fh.readline()
        while line:
            stripped = line.partition('#')[0].strip()
            pieces = stripped.split(':')
            if len(pieces) == 2 and pieces[1].strip().upper() in pick:
                result.append(pieces[0].strip())
            #
            line = fh.readline()
        #
    #

    return result
#


def write_tagfile(outpath, names, action='ADD'):
    header = '# Tagfile generated ' + time.strftime('%a %b %d %H:%M:%S %Z %Y', time.gmtime())
    with open(outpath, 'w') as fh:
        fh.write(header + '\n')
        for name in names:
            fh.write(name + ': ' + action.upper() + '\n')
        #
    #
#
