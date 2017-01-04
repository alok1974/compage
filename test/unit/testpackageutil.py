import os
import shutil
import unittest
import tempfile


from compage import logger, packageutil


class TestPacakge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.log_msg = True
        cls.site = tempfile.mkdtemp()
        cls.package_name = 'random_package'
        cls.dir_tree = {
            'mock_package': {
                '__init__.py': {},
                'dir_01': {
                    '__init__.py': {},
                    'file_01.py': {},
                    'dir_02': {
                        '__init__.py': {},
                        'file_02.py': {},
                        'dir_03': {
                            '__init__.py': {},
                            'file_03.py': {},
                            'file_04.py': {},
                        },
                    },
                },
                'dir_04': {
                    '__init__.py': {},
                    'file_05.py': {},
                },
            },
        }

        cls.import_map = {
            'file_01.py': ['os', 'sys', 'math', 'shutil'],
            'file_02.py': ['os', 'sys', 'shutil'],
            'file_03.py': ['sys', 'math', 'shutil'],
            'file_04.py': ['collections', 'abc', '_weakref'],
            'file_05.py': ['genericpath', 'errno', 'warnings', 'signal'],
            '__init__.py': [],
        }

        cls.min_max_nodes = (20, 50)
        cls.min_max_imports = (5, 8)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.site):
            shutil.rmtree(cls.site)
            msg = 'Removed site "{0}"'.format(cls.site)

            if cls.log_msg:
                logger.Logger.info(msg)

    def test_package_creation(self):
        packageutil.Package.from_dir_tree(
            self.site,
            self.dir_tree,
            self.import_map,
            log_msg=self.log_msg,
        )

        packageutil.Package.from_random(
            self.site,
            self.package_name,
            min_max_nodes=self.min_max_nodes,
            min_max_imports=self.min_max_imports,
            log_msg=self.log_msg,
        )


if __name__ == '__main__':
    unittest.main()
