# Subprocess wrapper that can log the output of external commands.
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


import logging
import subprocess
import sys
import tempfile
import time


def log_run(args, quiet=False, log_output=False):
    status = 1

    with tempfile.NamedTemporaryFile() as temp:
        with open(temp.name, 'w') as wfh, open(temp.name, 'r') as rfh:
            # For the subprocess, set start_new_session=True to make a setsid call prior to the exec. This
            # way, the subprocess doesn't receive SIGHUP if tealpkg is run via SSH and the connection drops.
            proc = subprocess.Popen(args, stdout=wfh, stderr=subprocess.STDOUT, text=True, bufsize=1, \
                                    start_new_session=True)
            while proc.poll() is None:
                if not quiet:
                    sys.stdout.write(rfh.read())
                #
                time.sleep(0.1)
            #
            status = proc.returncode
            if not quiet:
                # Capture any remaining that was written while sleeping
                sys.stdout.write(rfh.read())
            #
        #

        if log_output:
            data = ''
            with open(temp.name, 'r') as fh:
                data = fh.read()
            #

            logger = logging.getLogger(__name__)
            logger.info('Executed: %s', ' '.join(args))
            logger.info(data)
        #
    #

    return status
#
