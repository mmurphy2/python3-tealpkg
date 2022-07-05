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


import math


def parse_size(size_string):
    '''
    Parses a size string, as is found in the PACKAGES.TXT file in a Slackware repository or in the package database
    files. Returns the number of bytes corresponding to the string (which itself is an approximation of the actual
    package size).

    size_string   --   size string to parse (e.g. 125.2 K)
    '''
    accumulator = ''
    dp = False
    index = 0
    unit = None

    # Iterate through the string, accumulating digits and an optional decimal point. Stop when the first
    # non-digit, non-whitespace character is reached. Assume that character represents the unit.
    while index < len(size_string) and unit is None:
        char = size_string[index]
        if char.isdigit():
            accumulator += char
        elif char == '.' and not dp:
            dp = True
            accumulator += char
        elif not char.isspace():
            unit = char.lower()
        #

        index += 1
    #

    result = 0
    if len(accumulator) > 0:
        result = float(accumulator)
    #

    # Store sizes in units of bytes
    if unit == 'k':
        result = result * 2**10
    elif unit == 'm':
        result = result * 2**20
    elif unit == 'g':
        result = result * 2**30
    elif unit == 't':
        result = result * 2**40
    #

    return result
#


def friendly_size(size):
    '''
    For a given size (in bytes), returns a friendly, human-readable string representation. Prefixes are added for sizes
    in the kibiscale through tebiscale. The word HUGE is simply returned for anything pebiscale or higher (a package
    of such a size would be impractical, anyway). Decimal values are rounded to 2 digits.

    size   --   number of bytes for which to make a friendly representation
    '''
    friendly = '0 B'

    if size > 0:
        magnitude = math.log2(size)
        if magnitude < 10:
            friendly = str(int(size)) + ' B'
        elif magnitude < 20:
            friendly = str(round(size / 2**10, 2)) + ' KiB'
        elif magnitude < 30:
            friendly = str(round(size / 2**20, 2)) + ' MiB'
        elif magnitude < 40:
            friendly = str(round(size / 2**30, 2)) + ' GiB'
        elif magnitude < 50:
            friendly = str(round(size / 2**40, 2)) + ' TiB'
        else:
            friendly = 'HUGE'
        #
    #

    return friendly
#
