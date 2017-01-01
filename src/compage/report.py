"""Various Reporters"""
from compage import introspection, formatter

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
        return sorted(self._import_data.keys())

    def import_report(self):
        if self._report is None:
            self._report = self._get_report()
        return self._report

    def rank_report(self):
        if self._rank is None:
            self._rank = self._get_rank()
        return self._rank

    def module_report(self, module_name):
        return formatter.format_output(
            self._get_module_report(module_name), width=self._width)

    def _get_import_data(self, package_root):
        import_data = introspection.ImportFinder(package_root).import_data
        for name in self._ignore:
            import_data.pop(name, None)
        return import_data

    def _get_report(self):
        out = []
        report_header = '\nImport Report'
        out.append(report_header)
        for module_name in sorted(self._import_data.keys()):
            out += self._get_module_report(module_name, has_header=True)

        if not self._required_packages:
            return formatter.format_output(out, width=self._width)

        required_extras = sorted(
            set(self._required_packages).difference(self._import_data.keys()))
        if required_extras:
            msg = 'Following packages are required but never imported:'
            out.append(formatter.format_header(msg=msg, width=self._width))
            out.append(formatter.format_iterable(required_extras))
        return formatter.format_output(out, width=self._width)

    def _get_module_report(self, module_name, has_header=False):
        out = []
        if not has_header:
            report_header = ("\nImport Report for '{0}'").format(module_name)
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
        out.append(formatter.format_header(msg=msg, width=self._width))

        for file_path in sorted(module_data.keys()):
            import_data = module_data[file_path]
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
