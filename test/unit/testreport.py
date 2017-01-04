import os
import unittest
import tempfile
import shutil
import collections


from compage import report, logger, formatter, packageutil


class TestImportReporter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.log_msg = False
        cls.package_name = 'mock_package'
        cls.package_root = tempfile.mkdtemp()
        cls.width = 79
        cls.required_packages = []

        cls.mock_package = packageutil.Package.from_random(
            site=cls.package_root,
            package_name=cls.package_name,
            min_max_nodes=(10, 20),
            min_max_imports=(5, 8),
        )

        cls.file_tree = cls.mock_package.file_tree
        cls.import_map = cls.mock_package.import_map
        cls.file_paths = cls.mock_package.file_paths

        cls.import_reporter = report.ImportReporter(
            cls.package_root,
            required_packages=cls.required_packages,
            width=cls.width,
        )

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.package_root):
            shutil.rmtree(cls.package_root)

            msg = 'Removed package \'{0}\'from site "{1}"'.format(
                cls.package_name, cls.package_root)

            if cls.log_msg:
                logger.Logger.info(msg)

    def _get_module_report(self, module_name, has_header=False):
        out = []
        import_data = {}
        for file_name, imports in self.import_map.iteritems():
            for index, import_name in enumerate(imports):
                if import_name == module_name:
                    import_data.setdefault(
                        self.file_paths.get(file_name), []).append(index + 1)

        if not has_header:
            report_header = ("\nImport Report for '{0}'").format(module_name)
            out.append(report_header)

        required = None
        if self.required_packages:
            if module_name in self._required_packages:
                required = '\nIn Required: Yes'
            else:
                required = '\nIn Required: No'
        else:
            required = ''
        msg = "Module Name: '{0}'{1}".format(module_name, required)
        out.append(formatter.format_header(msg=msg, width=self.width))

        for file_path in sorted(import_data.keys()):
            out.append('"{0}"'.format(file_path))
            for lineno in import_data[file_path]:
                line = 'import {0}\n'.format(module_name)
                msg = "line {0}:\n{1}".format(lineno, line)
                out.append(msg)

        return out

    def _get_import_report(self):
        out = []
        report_header = '\nImport Report'
        out.append(report_header)
        for module_name in sorted(self.import_reporter.modules):
            out += self._get_module_report(module_name, has_header=True)

        if not self.required_packages:
            return formatter.format_output(out, width=self.width)

        required_extras = sorted(
            set(self.required_packages).difference(
                self.import_reporter.modules))
        if required_extras:
            msg = 'Following packages are required but never imported:'
            out.append(formatter.format_header(msg=msg, width=self.width))
            out.append(formatter.format_iterable(required_extras))
        return formatter.format_output(out, width=self.width)

    def test_modules(self):
        expected_modules = []
        for modules in self.import_map.values():
            for module in modules:
                expected_modules.append(module)
        expected_modules = sorted(list(set(expected_modules)))
        self.assertEqual(self.import_reporter.modules, expected_modules)

    def test_import_report(self):
        self.assertEqual(
            self.import_reporter.import_report(), self._get_import_report())

    def test_rank_report(self):
        ranks = collections.defaultdict(int)
        for modules in self.import_map.values():
            for module in modules:
                ranks[module] += 1

        for module_name, import_count in self.import_reporter.rank_report():
            self.assertEqual(import_count, ranks.get(module_name))

    def test_module_report(self):
        for module in self.import_reporter.modules:
            test_module_report = formatter.format_output(
                self._get_module_report(module),
                width=self.width,
            )

            reporter_module_report = self.import_reporter.module_report(module)
            self.assertEqual(reporter_module_report, test_module_report)


if __name__ == '__main__':
    unittest.main()
