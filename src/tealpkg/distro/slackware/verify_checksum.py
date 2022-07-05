# Verifies a file using CHECKSUMS.md5.
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


# TODO: refactor for MVC
# TODO: probably good to load the checksums into a data structure instead of hitting the file every time

import hashlib
import logging
import pathlib

from tealpkg.cli.colorprint import cprint


def verify_checksum(path_to_checksums, path_to_check, entry_name):
    result = False
    compare = ''
    logger = logging.getLogger(__name__)

    checksums_path = pathlib.PosixPath(path_to_checksums)
    if checksums_path.exists():
        logger.debug('Looking for %s in CHECKSUMS.md5', entry_name)
        with open(path_to_checksums, 'r') as fh:
            line = fh.readline()
            while line:
                parts = line.split()
                if len(parts) == 2 and parts[1] == entry_name:
                    compare = parts[0].lower()
                    break
                #
                line = fh.readline()
            #
        #

        if compare:
            check_path = pathlib.PosixPath(path_to_check)
            if check_path.exists():
                with open(path_to_check, 'rb') as fh:
                    md = hashlib.md5()
                    md.update(fh.read())
                    if md.hexdigest().lower() == compare:
                        result = True
                    else:
                        cprint('Incorrect MD5 checksum:', path_to_check, style='error', stderr=True)
                        logger.error('Incorrect MD5 checksum for %s', check_path)
                    #
                #
            else:
                cprint('Missing file:', path_to_check, style='error', stderr=True)
                logger.error('No comparison file: %s', check_path)
        else:
            cprint('Incomplete CHECKSUMS.md5:', path_to_checksums, style='error', stderr=True)
            logger.error('Missing %s from CHECKSUMS.md5', compare)
        #
    else:
        cprint('Missing CHECKSUMS.md5', style='error', stderr=True)
        logger.error('CHECKSUMS.md5 not found: %s', checksums_path)
    #

    return result
#
