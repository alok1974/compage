"""Generic node object and node utility functions"""
import uuid


from compage import exception


__all__ = ['Node', 'Tree']


class Node(object):
    """The node object, knows which parent node it is connected to"""
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

    def get_root_nodes(self):
        """Get all root nodes i.e, nodes with `None` as parent"""
        return [node for node in self.nodes if node.parent is None]

    def get_leaf_nodes(self):
        """Get all leaf nodes i.e, nodes with no children"""
        visited = []
        for node in self.nodes:
            if not [child for child in self.get_children(node, self.nodes)]:
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

    def _is_visited(self, visited, node):
        if node is not None:
            return node.id in visited
        return False

    def _add_to_visited(self, visited, node):
        if node is not None:
            visited.append(node.id)
