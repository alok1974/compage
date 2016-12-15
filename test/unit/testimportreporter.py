import os
import sys
import unittest
import tempfile
import shutil
import random
import uuid

from compage import reports, formatters


class Node(object):
    def __init__(self, name=None, parent=None, imports=None, isdir=None):
        super(Node, self).__init__()
        self._name = name
        self._parent = parent
        self._imports = imports
        self._isdir = isdir

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value

    @property
    def imports(self):
        return self._imports

    @imports.setter
    def imports(self, value):
        self._imports = value

    @property
    def isdir(self):
        return self._isdir

    @isdir.setter
    def isdir(self, value):
        self._isdir = value

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other

    def __neq__(self, other):
        return not self.name != other


class Tree(object):
    def __init__(self, site, nodes):
        super(Tree, self).__init__()
        self._site = site
        self._nodes = nodes
        self._root_node = self._get_root_node(self._nodes)

    @property
    def site(self):
        return self._site

    def make_tree(self):
        self._walk(self._site, self._root_node)

    def _get_root_node(self, nodes):
        return sorted(self._nodes, key=lambda n: n.parent)[0]

    def _walk(self, site, parent):
        site = os.path.join(site, str(parent))
        self._make_node(site, parent)
        for node in self._nodes:
            if node.parent == parent:
                self._walk(site, node)

    def _make_node(self, site, node):
        if node.isdir:
            if not os.path.exists(site):
                os.makedirs(site)
        else:
            imports = node.imports or []
            import_string = ''.join(
                map(lambda m: 'import {0}\n'.format(m), imports))

            with open(site, 'w') as fp:
                fp.write(import_string)


def random_tree(package_name):
    nodes = []
    curr_parent = None
    for i in range(random.randint(10, 20)):
        node_info = None
        if i == 0:
            node_info = {
                'name': package_name,
                'parent': None,
                'imports': None,
                'isdir': True,
            }
            # Create a node for __init__.py
            nodes.append(
                Node(
                    name='__init__.py',
                    parent=package_name,
                    imports=None,
                    isdir=False,
                )
            )
        else:
            id = formatters.hex_to_alpha(uuid.uuid4().hex)
            id = id[:5]
            name = '{0}_{1}'.format(package_name, id)
            isdir = bool(random.randint(0, 1))
            if isdir:
                imports = None
                # Create a node for __init__.py
                nodes.append(
                    Node(
                        name='__init__.py',
                        parent=name,
                        imports=None,
                        isdir=False,
                    )
                )
            else:
                imports = [random.choice([m for m in sys.modules.keys()
                                          if not m.startswith('_')])
                           for i in range(random.randint(5, 8))]
                name = '{0}.py'.format(name)

            node_info = {
                'name': name,
                'parent': curr_parent,
                'imports': imports,
                'isdir': isdir,
            }

        nodes.append(Node(**node_info))
        if not(bool(i)) or not bool(random.randint(0, 1)):
            if node_info.get('isdir'):
                curr_parent = node_info.get('name')

    return nodes


def create_package(site, nodes):
    tree = Tree(site, nodes)
    tree.make_tree()
    return tree.site


def create_mock_package(mock_name):
    return create_package(tempfile.mkdtemp(), random_tree(mock_name))


class TestImportReporter(unittest.TestCase):
    def setUp(self):
        self.package_root = create_mock_package('compage')
        self.import_reporter = reports.ImportReporter(
            self.package_root, required_packages=['os'], width=79)

    def tearDown(self):
        if os.path.exists(self.package_root):
            shutil.rmtree(self.package_root)

    def testimportreporter(self):
        print self.import_reporter.import_report()


if __name__ == '__main__':
    unittest.main()
