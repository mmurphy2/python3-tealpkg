#!/bin/bash
#
# Generates man page groff files from MarkDown. This script is only needed
# whenever man pages are updated.
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


which pandoc >/dev/null 2>&1
if [[ $? -ne 0 ]]; then
    echo "Pandoc is required for generating the man pages" >&2
    exit 1
fi

whatami=$(readlink -e "$0")
whereami=$(dirname "${whatami}")
top_level=$(dirname "${whereami}")

mkdir -p "${top_level}/man/man5"
mkdir -p "${top_level}/man/man8"

cd "${whereami}"
for page in *.8.md; do
    pandoc "${page}" -s -t man -o "${top_level}/man/man8/${page%.md}"
done

for page in *.5.md; do
    pandoc "${page}" -s -t man -o "${top_level}/man/man5/${page%.md}"
done
