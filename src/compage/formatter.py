"""Various Pretty formatters"""

import collections
import json
import textwrap
import functools
import re


__all__ = [
    'FormattedDict',
    'wrap',
    'format_iterable',
    'format_header',
    'format_output',
    'camel_case_to_snake_case',
    'hex_to_alpha'
]


class FormattedDict(collections.defaultdict):
    """Wrapper for pretty formatting the default dict using json.dumps"""
    def __init__(self, default_factory):
        super(FormattedDict, self).__init__(
            default_factory)

    def __str__(self):
        return self._format()

    def __repr__(self):
        return self._format()

    def _format(self):
        return json.dumps(self, indent=4)


def wrap(to_wrap, width=70):
    """Preserve new line char in textwrap"""
    out = []
    for line in to_wrap.split('\n'):
        if not line:
            out.append('')
        wrapped = textwrap.wrap(line, width=width)
        for wrapped_line in wrapped:
            out.append(wrapped_line)
    return '\n'.join(out)


def format_iterable(iterable, format_char="'"):
    """Adds a format char around the members of an iterable"""
    def _add_char(sub):
        return '{char}{sub}{char}'.format(char=format_char, sub=sub)
    return ', '.join(map(_add_char, iterable))


def format_header(
        msg,
        format_char="-",
        top=True,
        bottom=True,
        width=70,
        auto_length=False,
        ):
    """Creates a header using a fomat character"""
    header = []

    width = len(msg) if auto_length else width

    sep = "{sep}".format(sep=format_char * width)
    msg = "{msg}".format(msg=msg)

    if top:
        header.append(sep)

    header.append(msg)

    if bottom:
        header.append(sep)

    return '\n'.join(header)


def format_output(string_list, width=70):
    """Creates a text wrapped string from a list of strings"""
    formatted_output = map(
        functools.partial(wrap, width=width),
        string_list,
    )
    output_string = '\n'.join(formatted_output)
    return output_string


# stackoverflow: http://stackoverflow.com/questions/1175208/
# elegant-python-function-to-convert-camelcase-to-camel-case
def camel_case_to_snake_case(name):
    "Converts `camelCase` to `camel_case`"
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def hex_to_alpha(hex):
    """Converts hex string to alpha string, 'f718b' -> 'fhbib'"""
    char_table = dict([(str(i), char) for i, char in enumerate('abcdefghij')])
    out = []
    for s in hex:
        if unicode(s, 'utf-8').isnumeric():
            s = char_table[s]
        out.append(s)
    return ''.join(out)
