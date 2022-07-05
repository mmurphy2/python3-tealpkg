# Implements the tealpkg "repolist" command
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


from tealpkg.cli.table import Table


def repolist(args, config):
    status = 0
    config.load_repos()

    table = Table(separator_style='separator')
    table.add_column(width=16, spacing=2)
    table.add_column(width=30, spacing=2)
    table.add_column(width=3, spacing=2, proportional=False)
    table.add_column(width=7, spacing=2, proportional=False)
    table.add_column(width=8, spacing=0, proportional=False)
    header = table.add_row()
    header.add_column('ID', style='table_header', align='left')
    header.add_column('NAME', style='table_header', align='left')
    header.add_column('GPG', style='table_header', align='left')
    header.add_column('ENABLED', style='table_header', align='left')
    header.add_column('PRIORITY', style='table_header', align='left')
    table.add_separator()
    if args.repolist_what in (None, 'all', 'enabled'):
        for repo in config.repolist:
            row = table.add_row()
            row.add_column(repo.repoid, style='repo_id', align='left')
            row.add_column(repo.name, style='table_data', align='left')
            if repo.gpg_fp:
                row.add_column('yes', style='gpg_enabled', align='left')
            else:
                row.add_column('NO', style='gpg_disabled', align='left')
            #
            row.add_column('yes', style='enabled', align='center')
            row.add_column(str(repo.priority), style='priority', align='center')
    #####

    if args.repolist_what in (None, 'all', 'disabled'):
        for repo in config.disabled_repos:
            row = table.add_row()
            row.add_column(repo.repoid, style='repo_id', align='left')
            row.add_column(repo.name, style='table_data', align='left')
            if repo.gpg_fp:
                row.add_column('yes', style='gpg_enabled', align='left')
            else:
                row.add_column('NO', style='gpg_disabled', align='left')
            #
            row.add_column('no', style='disabled', align='center')
            row.add_column(str(repo.priority), style='priority', align='center')
        #
    #
    table.render()

    return status
#
