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


import shutil
import sys
import textwrap


class ColorPrinter:
    __instance = None

    @staticmethod
    def get_instance():
        if ColorPrinter.__instance is None:
            ColorPrinter.__instance = ColorPrinter()
        #
        return ColorPrinter.__instance
    #
    def __init__(self):
        self.font_map = { 'reset': 0, 'bold': 1, 'faint': 2, 'italic': 3, 'underline': 4, 'slow-blink': 5, 'fast-blink': 6,
                'reverse': 7, 'conceal': 8, 'strikethrough': 9, 'primary-font': 10, 'alt1-font': 11, 'alt2-font': 12,
                'alt3-font': 13, 'alt4-font': 14, 'alt5-font': 15, 'alt6-font': 16, 'alt7-font': 17, 'alt8-font': 18,
                'alt9-font': 19, 'fraktur': 20, 'bold-off': 21, 'normal': 22, 'italic-off': 23, 'underline-off': 24,
                'blink-off': 25, 'inverse-off': 27, 'conceal-off': 28, 'strikethrough-off': 29 }
        self.colormap = { 'black': 0, 'red': 1, 'green': 2, 'yellow': 3, 'blue': 4, 'magenta': 5, 'cyan': 6,
                'white': 7, 'gray': 8, 'bright-red': 9, 'bright-green': 10, 'bright-yellow': 11,
                'bright-blue': 12, 'bright-magenta': 13, 'bright-cyan': 14, 'bright-white': 15 }
        self.styles = { 'default': ('default', 'default', ['reset']) }
        self.use_color = False
        self.color_streams = [ sys.stdout, sys.stderr ]
        self.last_was_status = False
        self.quiet = False
    #
    def map_font(self, font_name, value):
        self.font_map[font_name] = value
    #
    def map_color(self, color_name, value):
        self.colormap[color_name] = value
    #
    def add_style(self, name, foreground, background, *fonteffects):
        self.styles[name] = (foreground, background, fonteffects)
    #
    def set_color(self, fgcolor, bgcolor, *fonteffects, stderr=False):
        stream = sys.stdout
        if stderr:
            stream = sys.stderr
        #

        fgcode = '39'
        if fgcolor in self.colormap:
            fgcode = '38;5;' + str(self.colormap[fgcolor]) + ';'
        #

        bgcode = '49'
        if bgcolor in self.colormap:
            bgcode = '48;5;' + str(self.colormap[bgcolor])
        #

        fontcodes = ''
        for effect in fonteffects:
            if effect in self.font_map:
                fontcodes += str(self.font_map[effect]) + ';'
            #
        #

        print('\033[0;' + fontcodes + fgcode + bgcode + 'm', end='', file=stream)
    #
    def cprint(self, *args, style='default', sep=' ', end='\n', stderr=False, file=sys.stdout, flush=False, is_status=False):
        if self.quiet and not stderr:
            return
        #

        pushed = False
        use_color = self.use_color

        stream = file
        if stderr:
            stream = sys.stderr
        #

        if stream not in self.color_streams or not stream.isatty():
            use_color = False
        #

        if use_color and style in self.styles:
            fgcolor, bgcolor, fonteffects = self.styles[style]
            self.set_color(fgcolor, bgcolor, *fonteffects, stderr=stderr)
            pushed = True
        #

        if is_status and self.last_was_status:
            if stream.isatty():
                print(end='\r', file=stream)
            else:
                print(file=stream)
            #
        elif self.last_was_status:
            print(file=stream)
        #

        print(*args, sep=sep, end=end, file=stream, flush=flush)

        if pushed:
            fgcolor, bgcolor, fonteffects = self.styles['default']
            self.set_color(fgcolor, bgcolor, *fonteffects, stderr=stderr)
        #

        self.last_was_status = is_status
    #
    def get_width(self):
        return shutil.get_terminal_size().columns
    #
    def write_status(self, message, style='default'):
        if not self.quiet:
            spaces = max(0, get_width() - len(message) - 1)
            if not sys.stdout.isatty():
                spaces = 0
            #
            self.cprint(message, spaces * ' ', style=style, sep='', end='', is_status=True)
        #
    #
    def clear_status(self):
        if not self.quiet and self.last_was_status:
            self.write_status('')
            if sys.stdout.isatty():
                print(end='\r')
            #
        #
        self.last_was_status = False
    #
#


class Row:
    def __init__(self):
        self.columns = []   # (text, style, align)
    #
    def add_column(self, text, style='default', align='left'):
        self.columns.append( (text, style, align) )
    #
    def render_column(self, number, width):
        if number < len(self.columns):
            text, style, align = self.columns[number]

            if len(text) > width:
                text = textwrap.shorten(text, width)
            #

            padding = max(width - len(text), 0)
            lpad = 0
            rpad = padding  # left alignment

            if align == 'right':
                lpad = padding
                rpad = 0
            elif align == 'center':
                lpad = padding // 2
                rpad = lpad
                if padding % 2 == 1:
                    # Odd width: put the extra space on the right
                    rpad += 1
            #####

            cprint(lpad * ' ', text, rpad * ' ', sep='', style=style, end='')
        #
    #
#


class Table:
    def __init__(self, separator_style='default'):
        self.get_width = ColorPrinter.get_instance().get_width
        self.columns = []        # column number: { 'width': w, 'spacing': s, 'proportional': p }
        self.min_width = 0
        self.rows = []
        self.separator_style = separator_style
        self.propcount = 0
    #
    def add_column(self, width, spacing=1, proportional=True):
        self.columns.append({'width': width, 'spacing': spacing, 'proportional': proportional})
        self.min_width += width + spacing
        if proportional:
            self.propcount += 1
        #
    #
    def add_row(self):
        row = Row()
        self.rows.append(row)
        return row
    #
    def add_separator(self):
        self.rows.append('-')
    #
    def render(self):
        width = get_width()
        if self.propcount > 0 and width > self.min_width:
            avail = width - self.min_width
            add = avail // self.propcount
        #

        # Leave a blank line prior to the start of the table
        cprint()

        for row in self.rows:
            if row == '-':
                cprint(width * '\u2500', style=self.separator_style)
            else:
                index = 0
                for entry in self.columns:
                    cwidth = entry['width']
                    spacing = entry['spacing']

                    if entry['proportional']:
                        cwidth += add
                    #
                    row.render_column(index, cwidth)
                    cprint(' ' * spacing, sep='', end='')
                    index += 1
                #
                cprint()
        #####
    #
#


class StatusLine:
    def __init__(self):
        self.enabled = False
        self.quiet = False
        self.last_height = 0
        self.last_width = 0
    #
    def check_size(self):
        size = shutil.get_terminal_size()
        if size.lines != self.last_height or size.columns != self.last_width:
            self.disable()
            self.enable()
        #
    #
    def enable(self):
        if not self.enabled and not self.quiet:
            self.enabled = True
            size = shutil.get_terminal_size()
            self.last_width = size.columns
            height = size.lines
            self.last_height = height
            print('\n\n')   # 2 sacrifical blank lines to be eaten during the split
            print('\033[0;', height - 2, 'r', sep='', end='')   # split the screen, leaving the bottom 2 lines for status
            print('\033[', height - 1, ';1H', sep='', end='')   # move to the first line of the status bar
            cprint('\u2500' * (size.columns), style='separator', end='\n')  # produce the separator
            print('\033[1F', end='')      # move back up above the status bar
    #####
    def disable(self):
        if self.enabled and not self.quiet:
            size = shutil.get_terminal_size()
            print('\033[s', end='')  # save the cursor
            print('\033[', size.lines - 1, ';1H', sep='', end='') # move to the separator line
            print(' ' * size.columns, end='')   # clear the separator
            print('\033[1E', end='')  # move down to the status line
            print(' ' * size.columns, end='')   # clear the status line
            print('\033[;r\033[u', end='') # end the split, then restore the cursor
            self.enabled = False
    #####
    def enter(self):
        if self.enabled and not self.quiet:
            self.check_size()
            size = shutil.get_terminal_size()
            print('\033[', size.lines, ';1H', sep='', end='')   # Move to the status line (bottom line)
    #####
    def leave(self):
        if self.enabled and not self.quiet:
            print('\033[2F', end='')   # Move up 2 lines (to the line before the status line)
    #####
#


def get_printer():
    return ColorPrinter.get_instance()
#

def cprint(*args, style='default', sep=' ', end='\n', stderr=False, file=sys.stdout, flush=False):
    inst = get_printer()
    inst.cprint(*args, style=style, sep=sep, end=end, stderr=stderr, file=file, flush=flush)
#

def get_width():
    inst = get_printer()
    return inst.get_width()
#

def write_status(message, style='default'):
    inst = get_printer()
    inst.write_status(message, style)
#

def clear_status():
    inst = get_printer()
    inst.clear_status()
#
