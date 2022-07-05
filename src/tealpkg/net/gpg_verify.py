# Verifies files using GPG.
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

import gpg
import tempfile

from tealpkg.cli.colorprint import cprint


class GPGException(Exception):
    pass
#


class GPGVerifier:
    '''
    Basic GPG verifier, which checks a GPG signature against an existing public key.
    '''
    def __init__(self, gpg_key, gpg_fp):
        '''
        Constructor.

        gpg_key   --  path to the GPG public key file to import
        gpg_fp    --  fingerprint of the GPG key (for verification)
        '''
        self.context = None
        self.temp = tempfile.TemporaryDirectory()

        try:
            with open(gpg_key, 'rb') as fh:
                keydata = fh.read()
            #
        except Exception as e:
            cprint(e, stderr=True, style='error')
            raise GPGException('Unable to load GPG public key file: ' + gpg_key)
        else:
            try:
                self.context = gpg.Context(home_dir=self.temp.name)
                result = self.context.key_import(keydata)
                if result.imported == 1:
                    fpr = result.imports[0].fpr.lower()
                    if fpr != gpg_fp.lower().replace(':', '').replace(' ', ''):
                        raise GPGException('Downloaded key does not match expected fingerprint')
                    #
                else:
                    raise GPGException('Failed to import GPG key from: ' + gpg_key)
                #
            except Exception as e:
                cprint(e, stderr=True, style='error')
                raise GPGException('Exception occurred while importing GPG key from: ' + gpg_key)
            #
        #
    #
    def verify(self, data_file, signature_file):
        '''
        Verifies a data file using an existing GPG context and a detached signature file. Returns True iff the
        signature can be verified using the public key(s) present in the GPG context.

        data_file       --  path to the file that is to be checked
        signature_file  --  path to the detached signature file for the data_file
        '''
        result = True
        signed_data = None
        signature = None

        try:
            signed_data = open(data_file, 'rb')
            signature = open(signature_file, 'rb')
            self.context.verify(signed_data, signature)
        except gpg.errors.BadSignatures:
            cprint('Bad GPG signature for downloaded file:', data_file, style='error', stderr=True)
            result = False
        except (gpg.errors.MissingSignatures, gpg.errors.GPGMEError):
            cprint('Missing valid GPG signature for downloaded file:', data_file, style='error', stderr=True)
            result = False
        except FileNotFoundError:
            cprint('Package or signature file not found for:', data_file, style='error', stderr=True)
            result = False
        finally:
            if signed_data:
                signed_data.close()
            #
            if signature:
                signature.close()
            #
        #

        return result
    #
#
