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
        self.name = name
        self.parent = parent
        self.imports = imports
        self.isdir = isdir
        self.site = self._get_site()

    def __eq__(self, other):
        return self.name == other.name

    def __neq__(self, other):
        return not self.name != other.name

    def _get_site(self):
        parent = self.parent._get_site() if self.parent is not None else ''
        return os.path.join(parent, self.name)

    def __repr__(self):
        return "Node('{0}')".format(self.name)


class Tree(object):
    def __init__(self, site, nodes):
        super(Tree, self).__init__()
        self.site = site
        self.nodes = nodes
        self.root_node = self._get_root_node(self.nodes)

    def make_tree(self):
        for node in self.nodes:
            self._make(node)

    def _get_root_node(self, nodes):
        return sorted(self.nodes, key=lambda n: n.parent)[0]

    def _walk(self, tree_node):
        yield tree_node
        for child in self._get_children(tree_node):
                for node in self._walk(child):
                    yield node

    def _get_children(self, tree_node):
        for node in self.nodes:
            if node.parent == tree_node:
                yield node

    def _make(self, node):
        node_path = os.path.join(self.site, node.site)
        if node.isdir:
            if not os.path.exists(node_path):
                os.makedirs(node_path)
        else:
            imports = node.imports or []
            import_string = ''.join(
                map(lambda m: 'import {0}\n'.format(m), imports))

            with open(node_path, 'w') as fp:
                fp.write(import_string)


def random_tree(
        tree_name, min_nodes=10, max_nodes=20, min_imports=5, max_imports=8):
    # Make Root Node
    root_node = Node(
        name=tree_name,
        parent=None,
        imports=None,
        isdir=True
    )

    # Make __init__.py Node for Root Node
    root_initpy_node = Node(
        name='__init__.py',
        parent=root_node,
        imports=None,
        isdir=False,
    )

    nodes = [root_node, root_initpy_node]
    curr_parent = root_node
    for i in range(random.randint(min_nodes, max_nodes)):
        name = formatters.hex_to_alpha(uuid.uuid4().hex[:5])

        # Randomize dir creation
        isdir = bool(random.randint(0, 1))

        if isdir:
            imports = None
        else:
            imports = [random.choice([m for m in sys.modules.keys()
                                      if not m.startswith('_')])
                       for i in range(random.randint(min_imports, max_nodes))]
            name = '{0}.py'.format(name)

        node = Node(
            name=name,
            parent=curr_parent,
            imports=imports,
            isdir=isdir,
        )

        nodes.append(node)

        # Create __init__.py node if node is a dir
        if isdir:
            nodes.append(
                Node(
                    name='__init__.py',
                    parent=node,
                    imports=None,
                    isdir=False,
                )
            )

        # Randomize going up or down the tree
        if bool(random.randint(0, 1)) and node.isdir:
            curr_parent = node

    return nodes


def create_package(site, nodes):
    tree = Tree(site, nodes)
    tree.make_tree()
    return tree.site


def create_mock_package(mock_name, min_nodes=50, max_nodes=100,
                        min_imports=20, max_imports=50):
    return create_package(
        tempfile.mkdtemp(),
        random_tree(
            mock_name,
            min_nodes=min_nodes,
            max_nodes=max_nodes,
            min_imports=min_imports,
            max_imports=max_imports,
        ),
    )


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
        print self.import_reporter.rank_report()


if __name__ == '__main__':
    unittest.main()
