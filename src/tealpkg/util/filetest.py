# File mode tests. These functions are designed to replicate the convenient
# -x, -r, and -w options of test(1).
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


# TODO: at present, this code does not produce correct results when an ACL is in use


import getpass
import grp
import os
import pathlib
import stat


def test_file_mode(path, permission='read'):
    result = False

    u_const = stat.S_IRUSR
    g_const = stat.S_IRGRP
    o_const = stat.S_IROTH

    if permission == 'write':
        u_const = stat.S_IWUSR
        g_const = stat.S_IWGRP
        o_const = stat.S_IWOTH
    elif permission == 'execute':
        u_const = stat.S_IXUSR
        g_const = stat.S_IXGRP
        o_const = stat.S_IXOTH
    elif permission != 'read':
        raise Exception('Invalid permission type: ' + str(permission))
    #

    check_path = pathlib.PosixPath(path)
    try:
        if check_path.exists():
            user = getpass.getuser()
            uid = os.getuid()
            gid = os.getgid()

            s = check_path.stat()
            owner = s.st_uid
            group = s.st_gid
            mode = s.st_mode

            if owner == uid:
                if mode & u_const:
                    result = True
                #
            else:
                group_matched = False
                for name in grp.getgrgid(gid).gr_mem:
                    if name == user:
                        group_matched = True
                        if mode & stat_const:
                            result = True
                        #
                        break
                #####

                if not group_matched:
                    if mode & o_const:
                        result = True
        #############
    except PermissionError as e:
        pass   # just return False
    #

    return result
#

def is_executable(path):
    return test_file_mode(path, 'execute')
#

def is_readable(path):
    return test_file_mode(path, 'read')
#

def is_writable(path):
    return test_file_mode(path, 'write')
#
