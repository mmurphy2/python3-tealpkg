# Individual commands in the tealpkg command-line interface
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


import os

from .check_update import check_update
from .clean import clean
from .info_list import info_list
from .install import install
from .provides import provides
from .remove import remove
from .repolist import repolist
from .search import search
from .sync import sync

from tealpkg.cli.colorprint import cprint


COMMAND_MAP = {   # command: (function, needs_root)
        'check-update': (check_update, False),
        'clean': (clean, False),
        'info': (info_list, False),
        'install': (install, True),
        'list': (info_list, False),
        'provides': (provides, False),
        'remove': (remove, True),
        'repolist': (repolist, False),
        'search': (search, False),
        'sync': (sync, True),
        'update': (sync, True),
        'upgrade': (sync, True),
        'whatprovides': (provides, False),
}


def dispatch(args, config):
    func, needs_root = COMMAND_MAP[args.command]

    if needs_root and os.geteuid() != 0:
        cprint('You must be root to run this command', style='error', stderr=True)
        return 2
    #

    return func(args, config)
#
