"""Generic node object and node utility functions"""
import os
import sys
import random
import uuid


from compage import formatters


class Node(object):
    def __init__(self, name=None, parent=None, imports=None, isdir=None):
        super(Node, self).__init__()
        self.name = name
        self.parent = parent
        self.imports = imports
        self.isdir = isdir
        self.site = self._get_site()

    def _get_site(self):
        parent = self.parent._get_site() if self.parent is not None else ''
        return os.path.join(parent, self.name)

    def __eq__(self, other):
        return self.name == other.name

    def __neq__(self, other):
        return not self.name != other.name

    def __repr__(self):
        return "Node('{0}')".format(self.name)


def root_node(self):
    return self._root_node


def get_root_node(self):
    for node in self.nodes:
        if node.parent is None:
            return node


def get_leaf_nodes(self):
    for node in self.nodes:
        if not [child for child in self.get_children(node)]:
            yield node


def walk(self, tree_node):
    """Depth first iterator"""
    yield tree_node
    for child in self._get_children(tree_node):
            for node in self.walk(child):
                yield node


def get_children(self, tree_node):
    for node in self.nodes:
        if node.parent == tree_node:
                yield node


def create_random_tree(
        tree_name, min_nodes=10, max_nodes=20, min_imports=5, max_imports=8):
    """Creates tree from random nodes"""
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
