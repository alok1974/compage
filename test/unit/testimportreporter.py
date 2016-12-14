import os
import unittest


from compage.importreporter import ImportReporter


class TestImportReporter(unittest.TestCase):
    def setUp(self):
        self.package_root = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
        self.import_reporter = ImportReporter(self.package_root, required_packages=['os'], width=79)

    def tearDown(self):
        pass

    def testimportreporter(self):
        print self.import_reporter.rank_report()


if __name__ == '__main__':
    unittest.main()

