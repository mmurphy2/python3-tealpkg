# PyCURL-based file downloader
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
# TODO: consider dropping PyCURL dependency and using Python native code for downloading


import pathlib
import pycurl
import traceback

from urllib.parse import urlparse

from tealpkg.cli.colorprint import cprint
from tealpkg.cli.progress_bar import ProgressBar


class Downloader:
    '''
    PyCURL-based downloader with a progress bar.
    '''
    def __init__(self):
        '''
        Constructor.
        '''
        self.progress_bar = ProgressBar('FIXME')
    #
    def progress(self, dl_total, downloaded, ul_total, uploaded):
        '''
        Callback function for pycurl, which updates the progress bar.

        dl_total    --  total number of bytes to download
        downloaded  --  total number of bytes downloaded so far
        ul_total    --  total number of bytes to upload (unused)
        uploaded    --  total number of bytes uploaded so far (unused)
        '''
        self.progress_bar.print_progress(downloaded, dl_total)
    #
    def download(self, url, output_path=None):
        '''
        Downloads the specified URL, displaying a progress bar during the process.

        Displays the average download speed (in Mbps) at the end of a successful download. Returns the path to the
        downloaded file if successful, or None if an error occurs.

        url           --   URL of the file to download (must be supported by curl)
        output_path   --   output path (directory or filename) for the downloaded file (None for current directory)
        '''
        target = None

        if output_path:
            target = pathlib.PosixPath(output_path)
        else:
            target = pathlib.Path.cwd()
        #

        if target.is_dir():
            name = pathlib.PurePosixPath(urlparse(url).path).name
            target = target.joinpath(name)
        #

        self.progress_bar.label = target.name
        result = None
        try:
            c = pycurl.Curl()
            c.setopt(c.NOPROGRESS, False)
            c.setopt(c.XFERINFOFUNCTION, self.progress)
            with open(target, 'wb') as fh:
                c.setopt(c.URL, url)
                c.setopt(c.FOLLOWLOCATION, True)
                c.setopt(c.WRITEDATA, fh)
                c.perform()
            #

            code = c.getinfo(c.RESPONSE_CODE)
            if code == 200:
                speed = str(int(round(c.getinfo(c.SPEED_DOWNLOAD) * 8 / 1000000, 0)))   # Mbps
                message = str(speed) + ' Mbps'
                self.progress_bar.print_complete(message, True)
                result = target.as_posix()
            else:
                dispcode = str(code)
                self.progress_bar.print_complete(dispcode, False)
            #
        except Exception as e:
            self.progress_bar.print_label()
            cprint('Download failed due to Python exception', stderr=True, style='error')
            traceback.print_exc()
        finally:
            c.close()
        #

        return result
    #
#
