import os
import sys
import unittest
import tempfile
import shutil
import uuid
import random
import collections


from compage import report, logger, formatter, dirutil


class PackageNode(dirutil.FileNode):
    def __init__(self, name, parent, isdir, imports=None):
        self.imports = imports or []
        self.file_contents = self._get_contents()

        super(PackageNode, self).__init__(
            name, parent, isdir, self.file_contents)

    def _get_contents(self):
        return ''.join(
            map(lambda m: 'import {0}\n'.format(m), self.imports))


def validate_min_max(min, max):
    if max < min:
        max = min
    return min, max


def validate_max_imports(max_imports):
    if max_imports > len(sys.modules):
        max_imports = len(sys.modules)
    return max_imports


def is_name_valid(name):
    return (not name.startswith('_')
            and all(map(str.islower, [char for char in name])))


def make_dir_node(node_name, parent, node_class):
    dir_node = node_class(
        name=node_name,
        parent=parent,
        imports=None,
        isdir=True,
    )

    # Make __init__.py Node for dir node
    initpy_node = node_class(
        name='__init__.py',
        parent=dir_node,
        imports=None,
        isdir=False,
    )

    return dir_node, initpy_node


def make_random_file_nodes(
        root,
        min_nodes=10,
        max_nodes=20,
        min_imports=5,
        max_imports=8,
):
    """Creates tree from random nodes"""

    min_imports, max_imports = validate_min_max(min_imports, max_imports)
    max_imports = validate_max_imports(max_imports)
    min_nodes, max_nodes = validate_min_max(min_nodes, max_nodes)

    # Make root node and __init__.py inside it
    root_node, initpy_node = make_dir_node(root, None, PackageNode)
    nodes = [root_node, initpy_node]

    curr_parent = root_node
    module_names = [m for m in sys.modules.keys() if is_name_valid(m)]
    num_nodes = random.randint(min_nodes, max_nodes)
    for i in range(num_nodes):
        name = formatter.hex_to_alpha(uuid.uuid4().hex[:5])

        # Randomize dir creation
        isdir = bool(random.randint(0, 1))

        if isdir:
            dir_node, initpy_node = make_dir_node(
                name, curr_parent, PackageNode)
            nodes += [dir_node, initpy_node]
        else:
            num_imports = random.randint(min_imports, max_nodes)
            # Randomize modules for import statement
            imports = [random.choice(module_names) for i in range(num_imports)]
            name = '{0}.py'.format(name)

            nodes.append(
                PackageNode(
                    name=name,
                    parent=curr_parent,
                    imports=imports,
                    isdir=isdir,
                )
            )

        # Randomize going up or down the tree
        # by selecting a random upstream dir
        curr_parent = random.choice([n for n in nodes if n.isdir])

    return nodes


def create_mock_package(package_name):
    temp_site = tempfile.mkdtemp()
    nodes = make_random_file_nodes(
        package_name,
        min_nodes=100,
        max_nodes=50,
        min_imports=20,
        max_imports=15,
    )

    file_tree = dirutil.FileTree(temp_site, nodes)
    file_tree.make_tree()

    return temp_site


class TestReport(unittest.TestCase):
    def setUp(self):
        self.package_name = 'mock_package'
        self.package_root = create_mock_package(self.package_name)
        self.import_reporter = report.ImportReporter(
            self.package_root, required_packages=['os'], width=79)

    def tearDown(self):
        if os.path.exists(self.package_root):
            shutil.rmtree(self.package_root)
            msg = 'Removed package \'{0}\'from site "{1}"'.format(
                self.package_name, self.package_root)
            logger.Logger.info(msg)

    def testimportreporter(self):
        print self.import_reporter.modules
        # print self.import_reporter.import_report()
        # print self.import_reporter.rank_report()


if __name__ == '__main__':
    unittest.main()
