# Concept of a repository from which software may be obtained.
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

# TODO: the Slackware-specific parts of this code need to be moved into distro
# TODO: also refactor to MVC pattern

import fnmatch
import logging
import pathlib
import pickle
import time

from urllib.parse import urlparse, urlunparse

from tealpkg.cli.colorprint import cprint
from tealpkg.distro.slackware.parse_manifest import parse_manifest
from tealpkg.distro.slackware.parse_packages import parse_packages
from tealpkg.distro.slackware.verify_checksum import verify_checksum
from tealpkg.net.downloader import Downloader
from tealpkg.net.file_path import FilePath
from tealpkg.net.gpg_verify import GPGVerifier


class Repository:
    def __init__(self, cache_dir, repoid, name, mirrorlist, manifest_path, gpg_path=None, gpg_url=None, gpg_fp=None,
            enabled=False, priority=99, expire=3600, extract_groups=False, strip_path=0, max_age=0):
        cache_path = pathlib.PosixPath(cache_dir).joinpath(repoid)
        cache_path.mkdir(mode=0o755, parents=True, exist_ok=True)
        self.cache_dir = cache_path.as_posix()
        self.repoid = repoid
        self.name = name
        self.mirrorlist = mirrorlist
        self.manifest_path = manifest_path
        self.gpg_path = gpg_path
        self.gpg_url = gpg_url
        self.gpg_fp = gpg_fp
        self.enabled = enabled
        self.priority = priority
        self.expire = expire
        self.extract_groups = extract_groups
        self.strip_path = strip_path
        self.max_age = max_age

        self.log = logging.getLogger(__name__)
        self.gpg = None
        self.downloader = Downloader()

        self.timestamp = 0
        self.packages = {}
        self.manifest = {}
        self.file_map = {}
        self.groups = {}
    #
    def __repr__(self):
        return '<Repository ' + self.repoid + ' priority ' + str(self.priority) + ' expire ' + str(self.expire) + '>'
    #
    def mtime(self, filename):
        result = 0
        path = pathlib.PosixPath(self.cache_dir).joinpath(filename)
        if path.exists():
            result = path.stat().st_mtime
        #
        return result
    #
    def load_gpg(self):
        if self.gpg_fp:
            mirrorlist = self.mirrorlist
            relpath = './GPG-KEY'
            if self.gpg_url:
                parts = urlparse(self.gpg_url)
                path = pathlib.PurePosixPath(parts.path)
                url = urlunparse( (parts.scheme, parts.netloc, path.parent.as_posix(), parts.params, parts.query, parts.fragment) )
                mirrorlist = [ url ]
                relpath = './' + path.name
            #
            resolved = FilePath(mirrorlist, relpath, self.gpg_path, None, self.downloader, verify=False, quiet=True, \
                    filename=self.repoid).resolve()
            self.gpg = GPGVerifier(resolved, self.gpg_fp)
        else:
            cprint('WARNING: GPG verification disabled for ' + self.repoid + ' (' + self.name + ')', style='warning', stderr=True)
        #
    #
    def clean(self, metadata, packages):
        cache = pathlib.PosixPath(self.cache_dir)

        if metadata:
            for item in ('CHECKSUMS.md5', 'CHECKSUMS.md5.asc', 'MANIFEST.bz2', 'PACKAGES.TXT', '__filemap__.pickle',
                    '__manifest__.pickle'):
                # Leave the __timestamp__ to provide anti-rollback protection
                cache.joinpath(item).unlink(missing_ok=True)
        #####

        if packages:
            for item in cache.glob('*.t?z'):
                item.unlink(missing_ok=True)
            #
            for item in cache.glob('*.t?z.asc'):
                item.unlink(missing_ok=True)
            #
        #
    #
    def load_metadata(self):
        result = True

        manifest_mod = self.mtime('MANIFEST.bz2')

        checksums = FilePath(self.mirrorlist, './CHECKSUMS.md5', self.cache_dir, self.gpg, self.downloader, \
                quiet=True).resolve(self.expire)
        packages = FilePath(self.mirrorlist, './PACKAGES.TXT', self.cache_dir, self.gpg, self.downloader, \
                verify=False, quiet=True).resolve(self.expire)
        manifest_relpath = './' + self.manifest_path
        manifest = FilePath(self.mirrorlist, manifest_relpath, self.cache_dir, self.gpg, self.downloader, \
                verify=False, quiet=True).resolve(self.expire)

        self.log.debug('CHECKSUMS.md5: %s', checksums)
        self.log.debug('PACKAGES.TXT: %s', packages)
        self.log.debug('MANIFEST.bz2: %s', manifest)

        last_stamp = 0
        stamp_path = pathlib.PosixPath(self.cache_dir).joinpath('__timestamp__')
        if stamp_path.exists():
            with open(stamp_path.as_posix(), 'r') as fh:
                last_stamp = int(fh.read().strip())
            #
        #
        self.log.debug('Last timestamp was: %d', last_stamp)

        # TODO log below here
        if checksums and packages and manifest:
            if verify_checksum(checksums, packages, './PACKAGES.TXT'):
                if verify_checksum(checksums, manifest, manifest_relpath):
                    new_packages, timestamp = parse_packages(packages, self.repoid, self.extract_groups, self.strip_path)

                    if timestamp < last_stamp:
                        cprint('Repository rollback detected for', self.repoid, style='warning', stderr=True)
                        result = False
                    elif self.max_age > 0 and (time.time() - timestamp) > self.max_age:
                        cprint('Outdated mirror detected for', self.repoid, style='warning', stderr=True)
                        result = False
                    else:
                        self.packages = new_packages

                        mj_path = pathlib.PosixPath(self.cache_dir).joinpath('__manifest__.pickle')
                        fm_path = pathlib.PosixPath(self.cache_dir).joinpath('__filemap__.pickle')

                        if self.mtime('MANIFEST.bz2') != manifest_mod or not mj_path.exists() or not fm_path.exists():
                            self.manifest, self.file_map = parse_manifest(manifest)
                            with open(mj_path, 'wb') as fh:
                                pickle.dump(self.manifest, fh)
                            #
                            with open(fm_path, 'wb') as fh:
                                pickle.dump(self.file_map, fh)
                            #
                        else:
                            with open(mj_path, 'rb') as fh:
                                self.manifest = pickle.load(fh)
                            #
                            with open(fm_path, 'rb') as fh:
                                self.file_map = pickle.load(fh)
                            #
                        #

                        # Load package file lists from the manifest
                        for name in self.manifest:
                            if name in self.packages:
                                for path in sorted(self.manifest[name]):
                                    self.packages[name].files.append(path)
                                #
                        #####

                        if timestamp != last_stamp:
                            with open(stamp_path, 'w') as fh:
                                fh.write(str(timestamp) + '\n')
                            #
                        #

                        if self.extract_groups:
                            for pkg in self.packages:
                                group = self.packages[pkg].group
                                if group:
                                    if group in self.groups:
                                        self.groups[group].append(pkg)
                                    else:
                                        self.groups[group] = [ pkg ]
                        #############
                    #
                else:
                    cprint('MANIFEST.bz2 checksum verification failed for', self.repoid, style='error', stderr=True)
                    result = False
                #
            else:
                cprint('PACKAGES.TXT checksum verification failed for', self.repoid, style='error', stderr=True)
                result = False
            #
        else:
            cprint('Metadata download failed for', self.repoid, style='error', stderr=True)
            result = False
        #

        return result
    #
    def find_package(self, glob):
        result = {}
        matches = []

        if '/' in glob:
            groups = fnmatch.filter(self.groups, glob[0:-1])
            for group in groups:
                for name in self.groups[group]:
                    if name not in matches:
                        matches.append(name)
            #########
        else:
            matches = fnmatch.filter(self.packages, glob)
        #

        for name in matches:
            package = self.packages[name]
            package.filepath = FilePath(self.mirrorlist, package.relpath, self.cache_dir, self.gpg, self.downloader)
            result[name] = package
        #
        return result
    #
    def find_file(self, filepath):
        result = []
        match_keys = fnmatch.filter(self.file_map, filepath)
        for key in match_keys:
            for name in self.file_map[key]:
                if name not in result:
                    result.append(name)
        #########

        return result
    #
#
