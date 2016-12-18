"""Various Reporter Objects"""
from compage import introspection
from compage.formatter import (
    format_header,
    format_iterable,
    format_output
)

__all__ = ['ImportReporter']


class ImportReporter(object):
    def __init__(
            self, package_root, required_packages=None, ignore=None, width=70):

        super(ImportReporter, self).__init__()
        self._package_root = package_root
        self._required_packages = required_packages or []
        self._ignore = ignore or []
        self._width = width
        self._import_data = self._get_import_data(self._package_root)
        self._report = None
        self._rank = None
        self._module_reports = {}

    @property
    def modules(self):
        return self._import_data.keys()

    def import_report(self):
        if self._report is None:
            self._report = self._get_report()
        return self._report

    def rank_report(self):
        if self._rank is None:
            self._rank = self._get_rank()
        return self._rank

    def module_report(self, module_name):
        return format_output(
            self._get_module_report(module_name), width=self._width)

    def _get_import_data(self, package_root):
        import_data = introspection.ImportFinder(package_root).import_data
        for name in self._ignore:
            import_data.pop(name, None)
        return import_data

    def _get_report(self):
        out = []
        report_header = '\n\nImport Report'
        out.append(report_header)
        for module_name in self._import_data:
            out += self._get_module_report(module_name, has_header=True)

        if not self._required_packages:
            return format_output(out, width=self._width)

        required_extras = sorted(
            set(self._required_packages).difference(self._import_data.keys()))
        if required_extras:
            msg = 'Following packages are required but never imported:'
            out.append(format_header(msg=msg, width=self._width))
            out.append(format_iterable(required_extras))
        return format_output(out, width=self._width)

    def _get_module_report(self, module_name, has_header=False):
        out = []
        if not has_header:
            report_header = ("\n\nImport Report for '{0}'").format(module_name)
            out.append(report_header)

        if module_name not in self._module_reports:
            self._module_reports[module_name] = self._generate_module_report(
                module_name)
        out += self._module_reports.get(module_name)

        return out

    def _generate_module_report(self, module_name):
        out = []
        module_data = self._import_data.get(module_name)
        if not module_data:
            msg = "No data found for module '{0}'".format(module_name)
            out.append(msg)
            return out

        required = None
        if self._required_packages:
            if module_name in self._required_packages:
                required = '\nIn Required: Yes'
            else:
                required = '\nIn Required: No'
        else:
            required = ''

        msg = "Module Name: '{0}'{1}".format(
            module_name, required)
        out.append(format_header(msg=msg, width=self._width))

        for file_path, import_data in module_data.items():
            out.append('"{0}"'.format(file_path))
            for (lineno, line) in import_data:
                msg = "line {0}:\n{1}".format(lineno, line)
                out.append(msg)

        return out

    def _get_rank(self):
        _rank = []
        for module_name, import_data in self._import_data.iteritems():
            import_count = sum(map(len, import_data.values()))
            _rank.append((module_name, import_count))
        return sorted(_rank, key=lambda x: x[1], reverse=True)
