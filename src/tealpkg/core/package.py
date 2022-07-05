# Basic representations of packages and package pairs.
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


import pathlib


class Package:
    def __init__(self, name, version, arch, build):
        self.name = name
        self.version = version
        self.arch = arch
        self.build = build
        self.desc = []
        self.files = []
        self.short = ''
        self.csize = 0
        self.usize = 0
        self.relpath = None
        self.group = ''
        self.filepath = None
        self.repo = ''
    #
#


class PackagePair:
    def __init__(self, name):
        self.name = name
        self.available = None
        self.installed = None
    #
    def has_upgrade(self):
        result = False

        if self.installed and self.available:
            if self.installed.version != self.available.version or self.installed.build != self.available.build:
                result = True
            #
        #

        return result
    #
#
