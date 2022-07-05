#!/usr/bin/env python3
#
# Outer driver program: implements multicall functionality
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


import os.path
import sys

from tealpkg import VERSION
from tealpkg.cli.tealpkg import main as tealpkg_main


MULTICALL_MAP = {
    'tealpkg': tealpkg_main,
}


status = 0

if '--version' in sys.argv or '-V' in sys.argv:
    print('tealpkg version', VERSION)
    print()
    print('Copyright 2021-2022 Coastal Carolina University. MIT licensed.')
else:
    whatami = os.path.basename(sys.argv[0])
    if whatami in MULTICALL_MAP:
        status = MULTICALL_MAP[whatami]
    else:
        status = tealpkg_main()
    #
#

sys.exit(status)
