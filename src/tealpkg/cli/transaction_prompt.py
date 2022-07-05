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


from .colorprint import cprint, Table
from .size import friendly_size


def prompt_confirm():
    status = 0
    ready = False
    while not ready:
        ask = input('Proceed with transaction? [Y/n] ')
        if ask in ('', 'Y', 'y'):
            ready = True
        elif ask in ('n', 'N'):
            status = 2
            ready = True
        #
    #

    return status
#

def prompt_install(package_pairs, upgrade=False):
    total_download = 0
    total_existing = 0
    total_installed = 0

    table = Table(separator_style='separator')
    table.add_column(width=20, spacing=2, proportional=True)
    table.add_column(width=14, spacing=2, proportional=True)
    table.add_column(width=14, spacing=2, proportional=True)
    table.add_column(width=10, spacing=2, proportional=False)
    table.add_column(width=10, spacing=0, proportional=False)

    header = table.add_row()
    header.add_column('NAME', style='table_header', align='left')
    header.add_column('VERSION', style='table_header', align='left')
    header.add_column('REPOSITORY', style='table_header', align='left')
    header.add_column('DOWNLOAD', style='table_header', align='left')
    header.add_column('INSTALLED', style='table_header', align='right')

    table.add_separator()

    for name in sorted(package_pairs):
        package = package_pairs[name].available
        row = table.add_row()
        row.add_column(name, style='pkgname', align='left')
        row.add_column(package.version + '-' + package.build, style='table_data', align='left')
        row.add_column(package.repo, style='table_data', align='left')
        csize = package.csize
        usize = package.usize
        if upgrade:
            total_existing += package_pairs[name].installed.usize
        #
        row.add_column(friendly_size(csize), style='table_data', align='left')
        row.add_column(friendly_size(usize), style='table_data', align='right')
        total_download += csize
        total_installed += usize
    #

    table.add_separator()
    table.render()

    cprint()

    table = Table(separator_style='table_separator')
    table.add_column(width=24, spacing=2, proportional=False)
    table.add_column(width=12, spacing=0, proportional=False)
    row = table.add_row()
    row.add_column('Total Package Size:', style='info_label', align='left')
    row.add_column(friendly_size(total_download), style='table_data', align='right')
    row = table.add_row()
    row.add_column('Total Installed Size:', style='info_label', align='left')
    row.add_column(friendly_size(total_installed), style='table_data', align='right')
    if upgrade:
        row = table.add_row()
        row.add_column('Net Upgrade Size:', style='info_label', align='left')
        row.add_column(friendly_size(total_installed - total_existing), style='table_data', align='right')
    #
    table.render()

    cprint()

    return prompt_confirm()
#


def prompt_remove(package_pairs):
    total_existing = 0

    table = Table(separator_style='separator')
    table.add_column(width=20, spacing=2, proportional=True)
    table.add_column(width=14, spacing=2, proportional=True)
    table.add_column(width=10, spacing=0, proportional=False)
    header = table.add_row()
    header.add_column('NAME', style='table_header', align='left')
    header.add_column('VERSION', style='table_header', align='left')
    header.add_column('SIZE', style='table_header', align='center')
    table.add_separator()

    for name in sorted(package_pairs):
        package = package_pairs[name].installed
        row = table.add_row()
        row.add_column(name, style='pkgname', align='left')
        row.add_column(package.version + '-' + package.build, style='table_data', align='left')
        usize = package.usize
        total_existing += usize
        row.add_column(friendly_size(usize), style='table_data', align='right')
    #

    table.add_separator()
    table.render()

    cprint()

    table = Table(separator_style='table_separator')
    table.add_column(width=24, spacing=2, proportional=False)
    table.add_column(width=10, spacing=0, proportional=False)
    row = table.add_row()
    row.add_column('Total Removed Size:', style='info_label', align='left')
    row.add_column(friendly_size(total_existing), style='table_data', align='right')
    table.render()

    cprint()

    return prompt_confirm()
#
