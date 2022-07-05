# Parses a string expression of elapsed time.
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


def compute_time(timestr):
    '''
    Returns the total number of seconds represented by the given time string. Raises
    a ValueError if the time string is invalid. Valid components of time strings are
    decimal digits (0-9), whitespace, or time unit values.

    Supported time unit values are:

    y : years
    b : 30-day months
    f : 14 days (fortnights)
    w : 7 days (weeks)
    d : days
    h : hours
    m : minutes
    s : seconds

    A numeric value without a time unit implies seconds.

    timestr   --   input time string
    '''
    total = 0
    accumulator = ''

    for char in timestr:
        if char.isdigit():
            accumulator += char
        elif not char.isspace():
            value = 0
            if len(accumulator) > 0:
                value = int(accumulator)
                accumulator = ''
            #

            char = char.lower()
            if char == 'y':
                total += 365 * 86400 * value
            elif char == 'b':
                total += 30 * 86400 * value
            elif char == 'f':
                total += 14 * 86400 * value
            elif char == 'w':
                total += 7 * 86400 * value
            elif char == 'd':
                total += 86400 * value
            elif char == 'h':
                total += 3600 * value
            elif char == 'm':
                total += 60 * value
            elif char == 's':
                total += value
            else:
                raise ValueError('Invalid time specifier: ' + char)
            #
        #
    #

    # Anything left in the accumulator is treated as seconds
    if len(accumulator) > 0:
        total += int(accumulator)
    #

    return total
#
