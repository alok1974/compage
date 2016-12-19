"""Generic node object and node utility functions"""
import uuid
import collections

from compage import exception


__all__ = ['Node', 'Tree']


# From https://gist.github.com/hrldcpr/2012250
def nested_tree():
    return collections.defaultdict(nested_tree)


def add(nested_tree, path):
    for node in path:
        nested_tree = nested_tree[node]


def dicts(t):
    return {k: dicts(t[k]) for k in t}


class Node(object):
    """The node object, holds parent information"""
    def __init__(self, name, parent):
        super(Node, self).__init__()
        self._name = name

        if parent is not None and not isinstance(parent, Node):
            msg = "parent '{0}' should be of type {1} or None".format(
                parent, Node)
            raise exception.NodeCreationError(msg)

        self._parent = parent
        self._id = uuid.uuid4().hex[:8]

    @property
    def name(self):
        return self._name

    @property
    def parent(self):
        return self._parent

    @property
    def id(self):
        return self._id

    def __eq__(self, other):
        return self.id == other.id

    def __neq__(self, other):
        return not self == other

    def __repr__(self):
        return "{0}({1}|{2}|parent='{3}|{4}')".format(
            self.__class__.__name__,
            self.name, self.id,
            self.parent.name if self.parent else None,
            self.parent.id if self.parent else None,
        )


class Tree(object):
    """Provides queries on the given node objects"""
    def __init__(self, nodes):
        super(Tree, self).__init__()
        self.nodes = nodes
        self._num_nodes = len(self.nodes)
        self._root_nodes = self._get_root_nodes()

    @property
    def root_nodes(self):
        return self._root_nodes

    def _get_root_nodes(self):
        """Get all root nodes i.e, nodes with `None` as parent"""
        return [node for node in self.nodes if node.parent is None]

    def get_leaf_nodes(self):
        """Get all leaf nodes i.e, nodes with no children"""
        visited = []
        for node in self.nodes:
            if not [child for child in self.get_children(node)]:
                if self._is_visited(visited, node):
                    continue
                yield node
                self._add_to_visited(visited, node)

    def walk(self, tree_node):
        """Depth first iterator for the given node"""
        visited = []
        yield tree_node
        for child in self.get_children(tree_node, self.nodes):
            for node in self.walk(child):
                if self._is_visited(visited, node):
                    continue
                yield node
                self._add_to_visited(visited, node)

    def get_children(self, tree_node):
        """Iterator for children of the given node"""
        visited = []
        for node in self.nodes:
            if node.parent is None:
                continue
            elif node.parent == tree_node:
                if self._is_visited(visited, node):
                    continue
                yield node
                self._add_to_visited(visited, node)

    def get_lineage(self, tree_node):
        """
        Iterator for all parents of the given node
        starting from immediate parent
        """
        visited = []
        yield tree_node.parent
        if tree_node.parent is not None:
            for parent in self.get_lineage(tree_node.parent):
                if self._is_visited(visited, parent):
                    continue
                yield parent
                self._add_to_visited(visited, parent)

    def get_hierarchy(self, tree_node):
        """Return heirarchy of the node with the top ancestor to the node"""
        lineage = [l for l in self.get_lineage(tree_node) if l]
        return [node for node in reversed(lineage)] + [tree_node]

    def to_dict(self):
        """Returns the tree as a dictionary"""
        n_tree = nested_tree()
        for node in self.nodes:
            heirarchy = [node.name for node in self.get_hierarchy(node)]
            add(n_tree, heirarchy)
        return dicts(n_tree)

    def _is_visited(self, visited, node):
        if node is not None:
            return node.id in visited
        return False

    def _add_to_visited(self, visited, node):
        if node is not None:
            visited.append(node.id)


if __name__ == '__main__':
    import random
    from compage import formatter
    import pprint

    def make_nodes(num_nodes=15):
        node_names = [str(i).zfill(2) for i in range(num_nodes)]
        nodes = []
        curr_parent = None
        for index, node_name in enumerate(node_names):
            if index == 0:
                curr_parent = None

            node = Node(node_name, curr_parent)
            nodes.append(node)

            # Select a random parent for this node
            curr_parent = random.choice(nodes)
        return nodes

    def test_get_lineage(nodes):
        tree = Tree(nodes)
        out = []
        for node in nodes:
            out.append('node: {0}'.format(node))
            out.append(
                'lineage: {0}'.format([n for n in tree.get_lineage(node) if n])
            )
            out.append('')

        print formatter.format_output(out, width=79)

    def test_to_dict(nodes):
        tree = Tree(nodes)
        return tree.to_dict()

    nodes = make_nodes(100)
    tree = Tree(nodes)
    s = pprint.pformat(test_to_dict(nodes))
    print s
