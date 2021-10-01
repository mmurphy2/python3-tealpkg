#!/usr/bin/env python3
#
# TealPkg: A flexible frontend for pkgtools
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


import logging
import os
import sys

from tealpkg.arguments import handle_arguments
from tealpkg.colorprint import cprint, get_printer
from tealpkg.command import dispatch
from tealpkg.config import Configuration
from tealpkg import VERSION


status = 0
args = handle_arguments()

if args.version:
    print(VERSION)
else:
    config = Configuration(args.config, args.enablerepo, args.disablerepo, args.force_expire, args.debug)
    printer = get_printer()
    printer.quiet = args.quiet

    if args.command is None:
        if args.force_expire >= 0:
            # Refresh metadata
            config.load_repos()
            status = 0 if config.load_metadata() else 1
        else:
            cprint(sys.argv[0], 'no command specified', style='error', stderr=True)
            status = 2
        #
    else:
        try:
            status = dispatch(args, config)
        except BrokenPipeError as e:
            # From the Python docs: gracefully deal with SIGPIPE
            # See "Note on SIGPIPE" in https://docs.python.org/3/library/signal.html#module-signal
            devnull = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull, sys.stdout.fileno())
            status = 1
        #
    #
#

sys.exit(status)
