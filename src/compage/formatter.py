"""Various Pretty formatters"""

import os
import collections
import json
import textwrap
import functools
import re


# import compage.nodeutil as nodeutil

__all__ = [
    'FormattedDict',
    'FormattedDefaultDict',
    'wrap',
    'format_iterable',
    'format_header',
    'format_output',
    'camel_case_to_snake_case',
    'hex_to_alpha',
    'tree'
]


class FormattedDict(dict):
    def __repr__(self):
        return self._format()

    def _format(self):
        return json.dumps(self, indent=4)


class FormattedDefaultDict(FormattedDict, collections.defaultdict):
    """Wrapper for pretty formatting the default dict using json.dumps"""
    def __init__(self, default_factory):
        super(FormattedDefaultDict, self).__init__(
            default_factory)


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


def tree(root_dir, line_spacing=1, show_hidden=False):
    if not os.path.exists(root_dir) or not os.path.isdir(root_dir):
        msg = 'Error opening,  "{0}" does not exist or is not a directory.'
        return msg.format(root_dir)
    from compage import nodeutil
    nodes = []
    first_iteration = True
    for root, dirs, files in os.walk(root_dir):
            if not show_hidden:
                dirs[:] = filter(lambda x: not x.startswith('.'), dirs)
                files[:] = filter(lambda x: not x.startswith('.'), files)

            root_name = root or root_dir
            parent = os.path.basename(os.path.abspath(root_name))

            if first_iteration:
                parent_node = nodeutil.Node(parent, None)
                first_iteration = False
                nodes.append(parent_node)
            else:
                parent_node = filter(lambda n: n.name == parent, nodes)[-1]

            children = sorted(dirs + files)
            for child in children:
                child_node = nodeutil.Node(child, parent=parent_node)
                nodes.append(child_node)
    return nodeutil.Tree(nodes).render(line_spacing=line_spacing)
