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


import argparse


CONF_FILE='/etc/tealpkg/tealpkg.ini'


def handle_arguments():
    ap = argparse.ArgumentParser(prog='tealpkg', description='Package synchronization tool for Slackware Linux')

    # Options
    ap.add_argument('-c', '--config', default=CONF_FILE, help='Specify configuration file')
    ap.add_argument('-d', '--debug', action='store_true', help='Set log level to DEBUG')
    ap.add_argument('-D', '--dry-run', action='store_true', help='Do not actually change packages on the system')
    ap.add_argument('-i', '--include', action='extend', default=[], nargs=1, help='Include presently excluded package')
    ap.add_argument('-q', '--quiet', action='store_true', help='Suppress standard output (implies -y)')
    ap.add_argument('-x', '--exclude', action='extend', default=[], nargs=1, help='Exclude presently included package')
    ap.add_argument('-y', '--yes', action='store_false', dest='prompt', help='Do not prompt for confirmation')
    ap.add_argument('--enablerepo', action='extend', default=[], nargs=1, help='Enables a repository')
    ap.add_argument('--disablerepo', action='extend', default=[], nargs=1, help='Disables a repository')
    ap.add_argument('--refresh', action='store_const', dest='force_expire', const=0, default=-1, help='Force metadata update')
    ap.add_argument('--version', action='store_true', help='Display version information and exit')

    subparsers = ap.add_subparsers(dest='command', help='command help')

    # Commands
    parser_check_update = subparsers.add_parser('check-update', help='Checks for updates')

    parser_clean = subparsers.add_parser('clean', help='Removes downloaded files')
    parser_clean.add_argument('clean_what', choices=['all', 'metadata', 'packages'], help='Select items to clean')

    parser_info = subparsers.add_parser('info', help='Displays package information')
    parser_info_group = parser_info.add_mutually_exclusive_group()
    parser_info_group.add_argument('--available', action='store_const', dest='limit', const='available', \
            default='all', help='Displays information about available packages')
    parser_info_group.add_argument('--extras', action='store_const', dest='limit', const='extras', \
            help='Displays information about packages not found in repos')
    parser_info_group.add_argument('--installed', action='store_const', dest='limit', const='installed', \
            help='Displays information about installed packages')
    parser_info_group.add_argument('--upgrades', action='store_const', dest='limit', const='upgrades', \
            help='Displays information about package updates')
    parser_info.add_argument('names', nargs='*', default=[], help='Package names')

    parser_install = subparsers.add_parser('install', help='Installs a package')
    parser_install.add_argument('--optional', action='store_true', help='Include optional packages when using tagfiles')
    parser_install.add_argument('--reinstall', action='store_true', help='Reinstall packages that are already installed')
    parser_install.add_argument('--tagfile', action='store_true', help='Specify a tagfile instead of a package name')
    parser_install.add_argument('name', nargs='+', help='Name of package to install')

    parser_list = subparsers.add_parser('list', help='List information about packages')
    parser_list.add_argument('--save', action='store', dest='tagfile', help='Write list to a tagfile')
    parser_list.add_argument('--action', action='store', dest='tagaction', default='ADD', help='Action (ADD/OPT/SKP) for packages in tagfile')
    parser_list_group = parser_list.add_mutually_exclusive_group()
    parser_list_group.add_argument('--available', action='store_const', dest='limit', const='available', \
            help='Lists any available package that is not currently installed')
    parser_list_group.add_argument('--extras', action='store_const', dest='limit', const='extras', \
            help='Lists any installed package that is not available in repositories')
    parser_list_group.add_argument('--installed', action='store_const', dest='limit', const='installed', \
            help='Lists any installed package')
    parser_list_group.add_argument('--upgrades', action='store_const', dest='limit', const='upgrades', \
            help='Lists packages that have updates available')
    parser_list.add_argument('names', nargs='*', default=[], help='Package names')

    parser_provides = subparsers.add_parser('provides', help='Finds a package that provides a file')
    parser_provides.add_argument('file', nargs='+', help='File to search')

    parser_remove = subparsers.add_parser('remove', help='Removes installed packages')
    parser_remove.add_argument('name', nargs='+', help='Name of package to remove')

    parser_repolist = subparsers.add_parser('repolist', help='Lists enabled repositories')
    pr_group = parser_repolist.add_mutually_exclusive_group()
    pr_group.add_argument('--enabled', action='store_const', const='enabled', dest='repolist_what', help='enabled repositories')
    pr_group.add_argument('--disabled', action='store_const', const='disabled', dest='repolist_what', help='disabled repositories')
    pr_group.add_argument('--all', action='store_const', const='all', dest='repolist_what', help='all repositories')

    parser_search = subparsers.add_parser('search', help='Searches for packages')
    parser_search.add_argument('query', nargs='+', help='Search query')

    parser_sync = subparsers.add_parser('sync', help='Synchronize installed packages')
    parser_sync.add_argument('name', nargs='*', help='Name of package to synchronize')

    parser_update = subparsers.add_parser('update', help='Alias for sync')
    parser_update.add_argument('name', nargs='*', help='Name of package to synchronize')

    parser_upgrade = subparsers.add_parser('upgrade', help='Alias for sync')
    parser_upgrade.add_argument('name', nargs='*', help='Name of package to synchronize')

    parser_whatprovides = subparsers.add_parser('whatprovides', help='Alias for provides')
    parser_whatprovides.add_argument('file', nargs='+', help='File to search')

    args = ap.parse_args()
    return args
#
