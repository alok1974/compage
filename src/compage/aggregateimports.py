"""Reports on the imports of a package"""
import os
from compage.introspection import ImportScanner
from compage.formatters import (
    FormattedDict,
    format_header,
    format_iterable,
    format_output
)


# TODO: Write unit test


class AggregateImports(object):
    def __init__(
        self,
        package_root,
        required_packages=None,
        ignore=None,
        width=70,
            ):
        super(AggregateImports, self).__init__()
        self._package_root = package_root
        self._required_packages = required_packages or []
        self._ignore = ignore or []
        self._width = width
        self._imports = None
        self._report = None
        self._dependency_report = None

    @property
    def imports(self):
        if self._imports is None:
            self._imports = self._get_imports()
        return self._imports

    def report(self):
        if self._report is None:
            self._report = self._get_report()
        return self._report

    def module_report(self, module_name):
        return format_output(
            self._get_module_report(module_name), width=self._width)

    def dependency_report(self):
        if self._dependency_report is None:
            self._dependency_report = self._get_dependency_report()
        return self._dependency_report

    def _get_imports(self):
        imports = {}
        for dirpath, dirnames, filenames in os.walk(self._package_root):
            for filename in filenames:
                # Filter out non python source files
                if not filename.endswith('.py'):
                    continue
                file_path = os.path.join(dirpath, filename)
                file_imports = ImportScanner(file_path).imports
                for (lineno, line, name, _) in file_imports:
                    top_level_name = name.split('.', 1)[0]
                    if top_level_name in self._ignore:
                        continue
                    imports.setdefault(
                        top_level_name,
                        FormattedDict(list),
                    )[file_path].append((lineno, line))
        return imports

    def _get_report(self):
        report_header = '\n\nAggregate Imports: Import Report'
        out = [report_header]
        for module_name in self.imports:
            out += self._get_module_report(module_name, has_header=True)
        return format_output(out, width=self._width)

    def _get_module_report(self, module_name, has_header=False):
        out = []
        if not has_header:
            report_header = ("\n\nAggregate Import :"
                             " Module Report for '{0}'").format(module_name)
            out.append(report_header)

        msg = "'{0}' has the following import data".format(
            module_name)
        out.append(format_header(msg=msg, width=self._width))
        module_data = self.imports.get(module_name)
        if module_data:
            for file_path, import_data in module_data.items():
                out.append('"{0}"'.format(file_path))
                for (lineno, line) in import_data:
                    msg = "line {0}:\n{1}".format(lineno, line)
                    out.append(msg)
        else:
            msg = "No data found for module '{0}'".format(module_name)
            out.append(msg)

        return out

    def _get_dependency_report(self):
        report_header = '\n\nAggregate Import: Dependency Report'
        out = [report_header]
        for p in self._required_packages:
            if p in self.imports:
                msg = ("'{0}' is a required "
                       "package with following import data:").format(p)

                out.append(
                    format_header(msg=msg, width=self._width))
                for data in self.imports[p]:
                    (file_path, lineno, line) = data
                    msg = "line {0} in {1}:".format(lineno, file_path)
                    out.append(msg)
                    out.append(line.split('\n', 1)[0])
                    out.append('')

        required = set(self._required_packages)
        imported = set(self.imports.keys())

        required_extras = sorted(required.difference(imported))
        imported_extras = sorted(imported.difference(required))

        if required_extras:
            msg = 'Following packages are required but never imported:'
            out.append(format_header(msg=msg, width=self._width))
            out.append(format_iterable(required_extras))

        out.append('')

        if imported_extras:
            msg = 'Following are imported but are not in required:'
            out.append(format_header(msg=msg, width=self._width))
            out.append(format_iterable(imported_extras))

        return format_output(out, width=self._width)


def main():
    package_root = '/Users/alok/github/nbCodeLines'
    ai = AggregateImports(package_root, width=79)
    print ai.report()
    print ai.module_report('gui')
    print ai.dependency_report()


if __name__ == '__main__':
    main()
