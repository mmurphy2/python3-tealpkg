# Configuration handler
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
#

# TODO: too many things going on here. Refactoring needed.

import configparser
import fnmatch
import logging
import os
import pathlib
import re
import tempfile

from urllib.parse import urlparse, urlunparse

from tealpkg.cli.colorprint import clear_status, cprint, get_printer, write_status
from tealpkg.distro.slackware.package_db import load_package_db
from tealpkg.util.compute_time import compute_time

from .repository import Repository


class Configuration:
    def __init__(self, config_file, force_enable=[], force_disable=[], force_expire=-1, debug=False):
        preload = { 'CWD': pathlib.Path.cwd().as_posix(), 'HOME': pathlib.Path.home().as_posix(), 'TMP': tempfile.gettempdir() }
        self.parser = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
        self.parser.read_dict({'path': preload})
        self.parser.read(config_file)

        self.scripts = self.parser.get('path', 'scripts', fallback='/etc/tealpkg/scripts')
        self.log_scripts = self.parser.getboolean('settings', 'log_scripts', fallback=False)
        self.log_pkgtools = self.parser.getboolean('settings', 'log_pkgtools', fallback=False)

        loglevel = logging.INFO
        if debug:
            loglevel = logging.DEBUG
        #

        logpath = self.parser.get('path', 'user_log', fallback=pathlib.Path.home().joinpath('.cache/tealpkg/log').as_posix())
        if os.geteuid() == 0:
            logpath = self.parser.get('path', 'log_file', fallback='/var/log/tealpkg/tealpkg.log')
        #
        logparent = pathlib.PosixPath(logpath).parent
        logparent.mkdir(mode=0o755, parents=True, exist_ok=True)
        logging.basicConfig(filename=logpath, encoding='utf-8', level=loglevel)
        self.log = logging.getLogger(__name__)

        self.gpg_keys = self.parser.get('path', 'user_gpg', fallback=pathlib.Path.home().joinpath('.cache/tealpkg/gpg').as_posix())
        if os.geteuid() == 0:
            self.gpg_keys = self.parser.get('path', 'gpg_keys', fallback='/etc/tealpkg/gpg')
        #
        pathlib.PosixPath(self.gpg_keys).mkdir(mode=0o755, parents=True, exist_ok=True)

        self.repobase = self.parser.get('path', 'repositories', fallback='/etc/tealpkg/repos')
        self.repo_force_enable = force_enable
        self.repo_force_disable = force_disable
        self.repo_force_expire = force_expire
        self.repolist = []
        self.disabled_repos = []

        self.cache_dir = self.parser.get('path', 'user_cache', fallback=pathlib.Path.home().joinpath('.cache/tealpkg/cache').as_posix())
        if os.geteuid() == 0:
            self.cache_dir = self.parser.get('path', 'cache_directory', fallback='/var/cache/tealpkg')
        #
        pathlib.PosixPath(self.cache_dir).mkdir(mode=0o755, parents=True, exist_ok=True)

        self.package_db = {}
        self.file_map = {}

        self.installpkg = self.parser.get('command', 'installpkg', fallback='/sbin/upgradepkg --install-new --reinstall')
        self.upgradepkg = self.parser.get('command', 'upgradepkg', fallback='/sbin/upgradepkg')
        self.removepkg = self.parser.get('command', 'removepkg', fallback='/sbin/removepkg')

        self.exclude_file = None
        if 'exclude' in self.parser['path']:
            path = pathlib.PosixPath(self.parser['path']['exclude'])
            if path.exists():
                self.exclude_file = path.as_posix()
        #####

        p = get_printer()
        p.use_color = self.parser.getboolean('settings', 'use_color', fallback=True)
        if 'style' in self.parser:
            for key in self.parser['style']:
                parts = self.parser['style'][key].split(',')
                fgcolor = parts[0].strip()
                bgcolor = 'default'
                if len(parts) > 1:
                    bgcolor = parts[1].strip()
                #
                fonteffects = []
                for effect in parts[2:]:
                    fonteffects.append(effect.strip())
                #
                p.add_style(key, fgcolor, bgcolor, *fonteffects)
        #####

        if 'color' in self.parser:
            for key in self.parser['color']:
                color = int(self.parser['color'][key])
                p.map_color(key, color)
            #
        #

        if 'font' in self.parser:
            for key in self.parser['font']:
                font = int(self.parser['font'][key])
                p.map_font(key, font)
            #
        #

        self.lockfile = self.parser.get('path', 'transaction_lock', fallback='/run/lock/tealpkg')
    #
    def load_package_db(self):
        write_status('Loading package database...', style='loadstatus')
        self.package_db, self.file_map = load_package_db(self.parser['path']['package_db'])
        clear_status()
    #
    def load_repos(self):
        self.repolist = []

        for path in pathlib.PosixPath(self.repobase).glob('*.ini'):
            preload = { 'distribution': self.parser['settings']['distribution'], 'release': self.parser['settings']['release'],
                    'architecture': self.parser['settings']['architecture'] }
            self.log.debug('Reading repository configuration %s', path.as_posix())
            parser = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
            parser.read_dict({'repo': preload})
            parser.read(path)

            repoid = parser['repo']['id']
            name = parser['repo']['name']
            enabled = parser.getboolean('repo', 'enabled', fallback=False)
            priority = parser.getint('repo', 'priority', fallback=99)
            manifest = parser.get('repo', 'manifest', fallback='MANIFEST.bz2')
            self.log.debug('Repository manifest %s priority %d', manifest, priority)

            # Expire time
            expire = 3600
            if 'metadata_expire' in parser['repo']:
                expire = compute_time(parser['repo']['metadata_expire'])
            #
            if self.repo_force_expire >= 0:
                expire = self.repo_force_expire
            #
            self.log.debug('Metadata expiration %d seconds', expire)

            # Maximum age before declaring the mirror out of date
            max_age = 0
            if 'max_age' in parser['repo']:
                max_age = compute_time(parser['repo']['max_age'])
            #

            # Base list of mirrors
            mirrors = []
            if 'baseurl' in parser['repo']:
                mirrors.append(parser['repo']['baseurl'])
            #
            if 'mirrorlist' in parser['repo']:
                listfile = path.with_name(parser['repo']['mirrorlist'])
                if listfile.exists():
                    with open(listfile, 'r') as fh:
                        line = fh.readline()
                        while line:
                            line = fh.readline()
                            mirrordata = line.partition('#')[0].strip()
                            if mirrordata:
                                mirrors.append(mirrordata)
                            #
                        #
                    #
                else:
                    cprint('Mirrorlist not found:', listfile.as_posix(), style='error', stderr=True)
                    self.log.error('Mirrorlist file not found: %s', listfile.as_posix())
                #
            #

            # Mirror list
            mirrorlist = []
            for mirror in mirrors:
                tup = urlparse(mirror)
                mirror_path = pathlib.PurePosixPath(tup.path).joinpath(parser.get('repo', 'subdirectory', fallback=''))
                mirrorlist.append(urlunparse( ( tup.scheme, tup.netloc, mirror_path.as_posix(), tup.params, tup.query, tup.fragment) ))
            #
            self.log.debug('Mirrorlist: %s', mirrorlist)

            # GPG fingerprint and (optional) URL
            gpg_fp = parser.get('repo', 'fingerprint', fallback=None)
            gpg_url = parser.get('repo', 'gpgkey', fallback=None)

            # Group name extraction (mostly for the official main Slackware repo)
            extract_groups = parser.getboolean('repo', 'extract_groups', fallback=False)

            # Sub-repositories of a main repository (e.g. Slackware's extra) may need the first path component
            # stripped from the relative path when parsing PACKAGES.TXT.
            strip_path = parser.getint('repo', 'strip_path', fallback=0)

            for item in self.repo_force_disable:
                if fnmatch.fnmatchcase(repoid, item):
                    self.log.debug('Forcing repository disabled: %s', repoid)
                    enabled = False
            #####

            for item in self.repo_force_enable:
                if fnmatch.fnmatchcase(repoid, item):
                    self.log.debug('Forcing repository enabled: %s', repoid)
                    enabled = True
            #####

            if enabled and len(mirrorlist) < 1:
                cprint('Repository', repoid, 'has no mirrors defined and is disabled', style='warning')
                self.log.error('No mirrors have been configured for: %s', repoid)
                enabled = False
            #

            repo = Repository(self.cache_dir, repoid, name, mirrorlist, manifest, self.gpg_keys, gpg_url, gpg_fp, \
                              enabled, priority, expire, extract_groups, strip_path, max_age)
            #

            if enabled:
                self.log.info('Enabled repository %s: %s', repoid, name)
                self.repolist.append(repo)
            else:
                self.disabled_repos.append(repo)
            #
        #

        self.repolist.sort(key=lambda r: r.priority)
        self.disabled_repos.sort(key=lambda r: r.priority)
        self.log.debug('Final repository list: %s', self.repolist)
    #
    def load_metadata(self):
        result = True

        for repo in self.repolist:
            write_status('Loading repository metadata for ' + repo.name + '...', style='loadstatus')
            self.log.debug('Loading metadata for repository: %s', repo.repoid)
            repo.load_gpg()
            check = repo.load_metadata()
            if not check:
                cprint('Failed to load metadata for repository', repo.repoid, style='error', stderr=True)
                self.log.error('Failed to load metadata for repository %s', repo.repoid)
                result = False
            #
        #
        clear_status()

        return result
    #
    def load_all(self):
        self.load_package_db()
        self.load_repos()
        return self.load_metadata()
    #
#
