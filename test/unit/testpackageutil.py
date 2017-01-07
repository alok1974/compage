import os
import shutil
import unittest
import tempfile
import pkgutil
import random


from compage import logger, packageutil


AVAILABLE_MODULES = [module
                     for _, module, _ in pkgutil.iter_modules()
                     if not module.startswith('_')
                     and str(module[0]).lower()
                     ]


def random_modules():
    return [random.choice(AVAILABLE_MODULES)
            for i in range(random.randint(10, 15))]


def walk_package_os(site, package_name):
    out = []
    root_dir = os.path.join(site, package_name)
    for root, dirs, files in os.walk(root_dir):
        # Forcing os.walk to recurse alphabetically
        # as this is the behaviour expected from
        # Tree.walk()
        dirs.sort()

        root_name = root or root_dir
        parent = os.path.basename(os.path.abspath(root_name))
        out.append(parent)

        children = sorted(dirs + files)
        out.append(children)

    return out


def walk_package(package):
    out = []
    file_tree = package.file_tree
    root_node = file_tree.root_nodes[0]
    for node in file_tree.walk(root_node):
        if not node.isdir:
            continue

        parent = node.name
        out.append(parent)

        children = sorted([n.name for n in file_tree.get_children(node)])
        out.append(children)

    return out


def walk_package_random(
        site, package_name, min_max_nodes, min_max_imports, log_msg=False):
    return walk_package(packageutil.Package.from_random(
        site, package_name, min_max_nodes, min_max_imports, log_msg=log_msg))


def walk_packge_dir_tree(site, dir_tree, import_map, log_msg=False):
    return walk_package(packageutil.Package.from_dir_tree(
        site, dir_tree, import_map, log_msg=log_msg))


class TestPacakge(unittest.TestCase):
    def setUp(self):
        self.log_msg = False
        self.site = tempfile.mkdtemp()
        self.package_name = 'mock_package'
        self.maxDiff = None

    def tearDown(self):
        if os.path.exists(self.site):
            shutil.rmtree(self.site)
            msg = '\nRemoved site "{0}"\n'.format(self.site)

            if self.log_msg:
                logger.Logger.info(msg)

    def setup_dir_tree_data(self):
        self.files = [
            'file_01.py',
            'file_02.py',
            'file_03.py',
            'file_04.py',
            'file_05.py',
        ]

        self.file_gen = (file for file in self.files)
        self.dir_tree = {
            '{0}'.format(self.package_name): {
                '__init__.py': {},
                'dir_01': {
                    '__init__.py': {},
                    next(self.file_gen): {},
                    'dir_02': {
                        '__init__.py': {},
                        next(self.file_gen): {},
                        'dir_03': {
                            '__init__.py': {},
                            next(self.file_gen): {},
                            next(self.file_gen): {},
                        },
                    },
                },
                'dir_04': {
                    '__init__.py': {},
                    next(self.file_gen): {},
                },
            },
        }

        self.import_map = dict(
            [(file, random_modules()) for file in self.files])

    def setup_random_tree_data(self):
        self.min_max_nodes = (50, 80)
        self.min_max_imports = (5, 8)

    def test_from_dir_tree(self):
        self.setup_dir_tree_data()
        dir_tee_package_data = walk_packge_dir_tree(
            self.site,
            self.dir_tree,
            self.import_map,
            self.log_msg,
        )

        os_package_data = walk_package_os(self.site, self.package_name)
        self.assertEqual(dir_tee_package_data, os_package_data)

    def test_from_random(self):
        self.setup_random_tree_data()
        random_package_data = walk_package_random(
            self.site,
            self.package_name,
            self.min_max_nodes,
            self.min_max_imports,
            self.log_msg,
        )

        os_package_data = walk_package_os(self.site, self.package_name)
        self.assertEqual(random_package_data, os_package_data)


if __name__ == '__main__':
    unittest.main()
