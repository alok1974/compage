import os
import re
import json
import collections
import textwrap
import functools


FROM_REGEX = r"from (.*) import (.*)"
IMPORT_REGEX = r"import (.*)"

# TODO: Add more regex patterns for imports like
# from foo import (
#   bar,
#   baz,
#   etc,
# )

# TODO: Write unit test


class AggregateImports(object):
    def __init__(
        self,
        packageRoot,
        requiredPackages=None,
        ignore=None,
        width=70,
            ):
        super(AggregateImports, self).__init__()
        self._packageRoot = packageRoot
        self._requiredPackages = requiredPackages or []
        self._ignore = ignore or []
        self._width = width
        self._cache = {}
        self._cachedProperties = {
            '_importData': self._getImportData,
            '_pretty': self._getPretty,
        }

    @property
    def pretty(self):
        return self._pretty

    @property
    def importData(self):
        return self._importData

    @property
    def packageRoot(self):
        return self._packageRoot

    @property
    def requiredPackages(self):
        return self._requiredPackages

    @property
    def width(self):
        return self._width

    @property
    def ignore(self):
        return self._ignore

    @ignore.setter
    def ignore(self, value):
        self.ignore = value

    def __getattr__(self, name):
        if name in self._cachedProperties:
            return self._getCachedProperty(name)

    def _getCachedProperty(self, name):
        if name not in self._cache:
            self._cache[name] = self._cachedProperties[name]()
        return self._cache[name]

    def _getImportData(self):
        importData = self._formattedDict(list)
        for dirpath, dirnames, filenames in os.walk(self._packageRoot):
            for filename in filenames:
                # Filter out non python source files
                if not filename.endswith('.py'):
                    continue

                fp = os.path.join(dirpath, filename)
                with open(fp, 'r') as f:
                    for index, line in enumerate(f.readlines()):
                        # Filter out any comments
                        if not line.split('#')[0].strip():
                            continue

                        if 'from ' in line:
                            regexToUse = FROM_REGEX

                        # Filter out lines where 'import' is used as
                        # a word and not as a python keyword
                        elif line.split('import')[0].strip():
                            continue
                        else:
                            regexToUse = IMPORT_REGEX

                        matches = re.findall(regexToUse, line)
                        if not matches:
                            continue

                        match = matches[0]
                        package = None
                        module = None
                        if isinstance(match, tuple):
                            module, imports = match
                            parts = map(str.strip, imports.split(','))
                            modules = map(
                                lambda part: '{0}.{1}'.format(module, part),
                                parts,
                            )
                        else:
                            modules = [match]

                        for module in modules:
                            module = map(str.strip, module.split(' as '))[0]
                            try:
                                package, module = module.split('.', 1)
                            except ValueError:
                                package, module = module, None

                            if package in self.ignore:
                                continue

                            line_no = index + 1
                            importData[package].append(
                                (module, fp, line.split('\n')[0], line_no))

        return importData

    def _getPretty(self):
        out = []
        for p in self.requiredPackages:
            if p in self.importData:
                msg = ("'{0}' is a required "
                       "package with following import data:").format(p)

                out.append(self._fromatHeader(msg=msg, width=self.width))
                for data in self.importData[p]:
                    module, fp, line, line_no = data
                    msg = "line {0} in {1}:".format(line_no, fp)
                    out.append(msg)
                    out.append(line)
                    out.append('')

        required = set(self.requiredPackages)
        imported = set(self.importData.keys())

        requiredExtras = required.difference(imported)
        importedExtras = imported.difference(required)

        if requiredExtras:
            msg = 'Following packages are required but never imported:'
            out.append(self._fromatHeader(msg=msg, width=self.width))
            out.append(self._formatIterable(requiredExtras))

        out.append('')

        if importedExtras:
            msg = 'Following are imported but are not in required:'
            out.append(self._formatHeader(msg=msg, width=self.width))
            out.append(self._formatIterable(importedExtras))

        out = map(functools.partial(self._wrap, width=self.width), out)

        return '\n'.join(out)

    # Wrapper for pretty formatting the default dict using json.dumps
    class _formattedDict(collections.defaultdict):
        def __init__(self, default_factory):
            super(AggregateImports._formattedDict, self).__init__(
                default_factory)

        def __str__(self):
            return self._format()

        def __repr__(self):
            return self._format()

        def _format(self):
            return json.dumps(self, indent=4)

    def _formatIterable(self, iterable, formatChar="'"):
        def _addChar(sub):
            return '{char}{sub}{char}'.format(char=formatChar, sub=sub)
        return ', '.join(map(_addChar, iterable))

    def _formatHeader(self, msg, formatChar="-", width=70):
        return '{sep}\n{msg}\n{sep}'.format(
            msg=msg, sep='{0}'.format(formatChar * width))

    # Preserve new line char in textwrap
    def _wrap(self, toWrap, width=70):
        out = []
        for line in toWrap.split('\n'):
            if not line:
                out.append('')
            wrapped = textwrap.wrap(line, width=width)
            for wrappedLine in wrapped:
                out.append(wrappedLine)
        return '\n'.join(out)


def main():
    packageRoot = os.path.abspath('{0}/..'.format(__file__))
    ai = AggregateImports(packageRoot, width=79)
    print ai.importData
    print ai.pretty


if __name__ == '__main__':
    main()
