# Implementation of the tealpkg "clean" command
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


from tealpkg.cli.colorprint import cprint


def clean(args, config):
    status = 0
    # TODO check that we have permissions to clean, then be sure to adjust status
    config.repo_force_enable = [ '*' ]  # cleaning works on all repositories, enabled or not
    config.load_repos()
    clean_metadata = True
    clean_packages = True
    if args.clean_what == 'metadata':
        clean_packages = False
    elif args.clean_what == 'packages':
        clean_metadata = False
    #
    for repo in config.repolist:
        cprint('Cleaning repository', repo.repoid)
        repo.clean(clean_metadata, clean_packages)
    #

    return status
#
