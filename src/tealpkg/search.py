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


import fnmatch

from .package import PackagePair


class Searcher:
    def __init__(self, repolist, package_db, file_map, exclude_file=None, include=[], exclude=[]):
        self.repolist = repolist
        self.package_db = package_db
        self.file_map = file_map
        self.include = include
        self.exclude = exclude

        # Load the exclude file
        if exclude_file:
            with open(exclude_file, 'r') as fh:
                line = fh.readline()
                while line:
                    exclude = line.partition('#')[0].strip()
                    if exclude and exclude not in self.exclude:
                        self.exclude.append(exclude)
                    #
                    line = fh.readline()
        #########
    #
    def is_included(self, name):
        result = True

        for item in self.exclude:
            if fnmatch.fnmatchcase(name, item):
                result = False
                break
        #####

        if not result:
            for item in self.include:
                if fnmatch.fnmatchcase(name, item):
                    result=True
                    break
        #########

        return result
    #
    def search_file(self, filepath, installed=True, available=True):
        result = {}
        pkgnames = set()

        if len(filepath) > 0:
            if filepath[0] not in ('/', '*'):
                filepath = '*' + filepath
            #

            if installed:
                keys = fnmatch.filter(self.file_map, filepath)
                for key in keys:
                    for name in self.file_map[key]:
                        pkgnames.add(name)
            #############

            if available:
                for repo in self.repolist:
                    avail = repo.find_file(filepath)
                    for name in avail:
                        pkgnames.add(name)
        #################

        if len(pkgnames) > 0:
            result = self.find_package(*pkgnames, installed=installed, available=available)
        #

        return result
    #
    def search_package(self, *queryset, fields=['name', 'short'], installed=True, available=True):
        found = []

        for query in queryset:
            if installed:
                for name in self.package_db:
                    if name not in found:
                        package = self.package_db[name]
                        for field in fields:
                            if hasattr(package, field):
                                if query.lower() in str(getattr(package, field)).lower():
                                    found.append(name)
                                    break
            #################
            if available:
                for repo in self.repolist:
                    for name in repo.packages:
                        if name not in found:
                            package = repo.packages[name]
                            for field in fields:
                                if hasattr(package, field):
                                    if query.lower() in str(getattr(package, field)).lower():
                                        found.append(name)
                                        break
        #####################

        return self.find_package(*found, installed=installed, available=available)
    #
    def find_package(self, *globs, installed=True, available=True, only_upgrades=False, only_extras=False):
        found = {}

        for glob in globs:
            if installed:
                names = fnmatch.filter(self.package_db, glob)
                for name in names:
                    pair = PackagePair(name)
                    pair.installed = self.package_db[name]
                    found[name] = pair
                #
            #

            if available:
                masked_names = set()
                for repo in self.repolist:
                    packages = repo.find_package(glob)
                    for name in packages:
                        package = packages[name]
                        if self.is_included(name) and name not in masked_names:
                            if name in found:
                                if only_extras:
                                    del found[name]
                                else:
                                    found[name].available = package
                                #####
                            else:
                                if not (only_extras or only_upgrades):
                                    found[name] = PackagePair(name)
                                    found[name].available = package
                        #########
                        # Masking names prevents the same name from being found again in a lower-priority repository
                        masked_names.add(name)
        #################

        # For upgrades, prune packages that have no available upgrades
        if only_upgrades:
            for name in list(found):
                if not found[name].has_upgrade():
                    del found[name]
        #########

        return found
    #
    def find_all_upgrades(self):
        result = self.find_package(*list(self.package_db), only_upgrades=True)
        return result
    #
#
