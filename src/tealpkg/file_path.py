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


import logging
import pathlib
import time

from urllib.parse import urlparse, urlunparse

from .progress_bar import ProgressBar


class FilePath:
    '''
    Abstract representation of a file path, which may be located on a remote server. Upon resolving the path, the
    file is downloaded (if necessary) and optionally verified with GPG.
    '''
    def __init__(self, mirrorlist, relpath, cache_dir, gpg, downloader, verify=True, filename=None, quiet=False):
        '''
        Constructor.

        mirrorlist  --   list of mirrors on which the remove file may be found (local or remote)
        relpath     --   relative path of the file within a mirror
        cache_dir   --   directory into which downloaded files are cached
        gpg         --   GPGVerifier instance for validating downloaded files
        verify      --   Boolean that enables GPG verification of the filename/URL + .asc as detached signature
        filename    --   local name of the file, if renamed from the URL
        downloader  --   Downloader instance to use for downloading the file, if necessary
        quiet       --   suppresses local, cache, and verification status messages
        '''
        self.mirrorlist = mirrorlist
        self.relpath = relpath
        self.cache_dir = cache_dir
        self.gpg = gpg
        self.relpath = relpath
        self.verify = verify
        if not self.gpg:
            self.verify = False
        #
        self.filename = filename
        self.downloader = downloader
        self.progress_bar = ProgressBar(quiet=quiet)
        self.log = logging.getLogger(__name__)
    #
    def resolve(self, download_if_older_than=-1):
        '''
        Resolves the file path to a local path on the system, or to None if the file cannot be resolved. The file
        will be downloaded into the cache directory if it is not already present on the local system. If GPG verification
        is enabled, the detached signature will also be downloaded, if necessary. Should GPG verification file, both the
        file and its detached signature are removed if they were downloaded (but not if the files were already local).

        Returns the path to the resolved file if resolution (and optional verification) succeeds. Returns None if the
        file cannot be found, the file cannot be downloaded, or a requested optional verification fails.

        The special download_if_older_than flag can be used to force re-downloading existing files (primarily for
        refreshing metadata). If the file exists locally, but its modification time was more than download_if_older_than
        seconds ago, the file will be re-downloaded. A value of download_if_older_than < 0 disables this feature.

        download_if_older_than  --  optional number of seconds before a file has expired
        '''
        local = False
        result = None
        path = None

        for mirror in self.mirrorlist:
            url = pathlib.PurePosixPath(mirror).joinpath(self.relpath).as_posix()
            self.log.debug('URL is %s', url)

            urlparts = urlparse(url)
            name = pathlib.PurePosixPath(urlparts.path).name
            if self.filename:
                name = self.filename
            #
            self.progress_bar.label = name

            if urlparts.scheme in ('', 'file'):
                local = True
                path = pathlib.PosixPath(urlparts.path)
                if path.exists():
                    result = urlparts.path
                    self.progress_bar.print_complete('Local', True)
                else:
                    self.progress_bar.print_complete('Not Found', False)
                #
            else:
                path = pathlib.PosixPath(self.cache_dir)
                path.mkdir(parents=True, exist_ok=True)
                path = path.joinpath(name)

                need_download = not path.exists()
                if not need_download and download_if_older_than >= 0:
                    mtime = path.stat().st_mtime
                    if (mtime + download_if_older_than) < time.time():
                        need_download = True
                    #
                #

                if need_download:
                    result = self.downloader.download(url, path)

                    if result is None:
                        # Remove any downloaded file, since the download failed
                        path.unlink(missing_ok=True)
                    #
                else:
                    result = path.as_posix()
                    self.progress_bar.print_complete('In Cache', True)
                #
            #

            if result and self.verify:
                sig_path = path.with_name(name + '.asc')

                sig_name = sig_path.as_posix()
                if not local and (not sig_path.exists() or need_download):
                    url = urlunparse( (urlparts.scheme, urlparts.netloc, urlparts.path + '.asc', urlparts.params, \
                            urlparts.query, urlparts.fragment) )
                    sig_name = self.downloader.download(url, sig_name)

                    if sig_name is None:
                        # Clean up any empty signature file
                        sig_path.unlink(missing_ok=True)
                    #
                #

                if sig_name:
                    if self.gpg.verify(result, sig_name):
                        self.progress_bar.print_complete('GPG', True, on_success='Verified')
                    else:
                        # Remove both the download and the signature file, since they appear to be corrupt, but only if
                        # we downloaded them first
                        if not local:
                            path.unlink(missing_ok=True)
                            sig_path.unlink(missing_ok=True)
                        #

                        result = None
                        self.progress_bar.print_complete('GPG', False, on_failure='Corrupt')
                    #
                else:
                    # Couldn't get the signature, so invalidate the result
                    result = None
                    self.progress_bar.print_complete('GPG', False, on_failure='No Signature')
                #
            #

            if result:
                break
            #
        #

        return result
    #
#
