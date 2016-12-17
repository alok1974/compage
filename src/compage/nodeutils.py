"""Generic node object and node utility functions"""


class Node(object):
    def __init__(self, name, parent):
        super(Node, self).__init__()
        self._name = name
        self._parent = parent
        self._child = None
        self._lineage = self._create_lineage()
        if parent is not None:
            parent.child = self

    @property
    def name(self):
        return self._name

    @property
    def parent(self):
        return self._parent

    @property
    def lineage(self):
        return self._lineage

    def _create_lineage(self):
        if self.parent is not None:
            return tuple(
                [node for node in self.parent._create_lineage()] + [self])
        else:
            return (None, self)

    def __eq__(self, other):
        return self.name == other.name

    def __neq__(self, other):
        return not self.name != other.name

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return "Node('{0}')".format(self.name)


def get_root_nodes(nodes):
    return [node for node in nodes if node.parent is None]


def get_leaf_nodes(nodes):
    for node in nodes:
        if not [child for child in get_children(node, nodes)]:
            yield node


def walk(start_node, nodes):
    """Depth first iterator"""
    yield start_node
    for child in get_children(start_node, nodes):
            for node in walk(child, nodes):
                yield node


def get_children(parent_node, nodes):
    for node in nodes:
        if node.parent is None:
            continue
        elif node.parent == parent_node:
            yield node


def _test():
    import random
    node_names = [char for char in '0123456789']
    nodes = []
    curr_parent = None
    for index, node_name in enumerate(node_names):
        if index == 0:
            curr_parent = None

        node = Node(node_name, curr_parent)
        nodes.append(node)

        # Select a random parent for this node
        curr_parent = random.choice(nodes)

    root_nodes = get_root_nodes(nodes)
    print 'root: {0}'.format(root_nodes)
    for node in walk(root_nodes[0], nodes):
        print '.'.join([str(n) for n in node.lineage if n])


if __name__ == '__main__':
    _test()
