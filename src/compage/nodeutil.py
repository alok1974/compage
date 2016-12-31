"""Generic Node and Tree Objects"""
import uuid
import collections

from compage import formatter, exception


__all__ = ['Node', 'Tree']


class Node(object):
    """The node object, holds parent information"""
    def __init__(self, name, parent=None):
        super(Node, self).__init__()
        self._name = name

        if parent is not None and not isinstance(parent, Node):
            msg = "parent '{0}' should be of type {1} or None".format(
                parent, Node)
            raise exception.NodeCreationError(msg)

        self._parent = parent
        self._nid = uuid.uuid4().hex[:8]

    @property
    def name(self):
        return self._name

    @property
    def parent(self):
        return self._parent

    @property
    def nid(self):
        return self._nid

    @property
    def short_info(self):
        return "{0}({1}|{2})".format(
            self.__class__.__name__,
            self.name,
            self.nid[:5],
        )

    def __eq__(self, other):
        if other is None:
            return False
        return self.nid == other.nid

    def __neq__(self, other):
        return not self == other

    def __repr__(self):
        return "{0}({1}|{2}|parent='{3}|{4}')".format(
            self.__class__.__name__,
            self.name,
            self.nid,
            self.parent.name if self.parent else None,
            self.parent.nid if self.parent else None,
        )


class Tree(object):
    """Provides queries on the given node objects"""
    def __init__(self, nodes):
        super(Tree, self).__init__()
        self.nodes = nodes
        self._num_nodes = len(self.nodes)
        self._root_nodes = self._get_root_nodes()

        # characters for rendering tree
        self._pipe_char = '|'
        self._node_end_char = '_'
        self._indentation_char = ' '
        self._indent = 4
        self._indentation = self._indent * self._indentation_char
        self._node_char = '{0}{1} '.format(
            self._pipe_char, self._node_end_char * max([1, self._indent - 1]))

    @classmethod
    def from_dict(cls, d):
        nodes = cls._create_nodes_from_dict(d)
        return cls(nodes)

    @property
    def root_nodes(self):
        return self._root_nodes

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
        for child in self.get_children(tree_node):
            for node in self.walk(child):
                if self._is_visited(visited, node):
                    continue
                yield node
                self._add_to_visited(visited, node)

    def walk_with_level(self, tree_node, level=0):
        """Depth first iterator for the given node"""
        visited = []
        yield tree_node, level
        for child in sorted(
                self.get_children(tree_node), key=lambda n: n.name):
            for node, this_level in self.walk_with_level(child, level + 1):
                if self._is_visited(visited, node):
                    continue
                yield node, this_level
                self._add_to_visited(visited, node)

    def get_children(self, tree_node):
        """Iterator for immediate children of the given node"""
        visited = []
        for node in self.nodes:
            if node.parent == tree_node:
                if self._is_visited(visited, node):
                    continue
                yield node
                self._add_to_visited(visited, node)

    def get_lineage(self, tree_node):
        """
        Iterator for all parents of the given node
        starting from immediate parent
        """
        if tree_node.parent is None:
            return

        visited = []
        yield tree_node.parent
        for parent in self.get_lineage(tree_node.parent):
            if self._is_visited(visited, parent):
                continue
            yield parent
            self._add_to_visited(visited, parent)

    def get_hierarchy(self, tree_node):
        """Return heirarchy of the node with the top ancestor to the node"""
        lineage = [l for l in self.get_lineage(tree_node) if l]
        return [node for node in reversed(lineage)] + [tree_node]

    def to_dict(self, repr_as=None):
        """
        Returns the tree as a dictionary

        Args:
            `repr_as` (str, optional):
                For displaying information, this can be set to attribute name
                of the node like - name, nid, short_info, parent etc.
                Default is `Node` objects.

        Returns:
            A tree structured dictionary of the `Node` objects.

        """
        def repr_func(node):
            if repr_as is not None:
                return getattr(node, repr_as)
            else:
                return node
        n_tree = self._nested_tree()
        for node in self.nodes:
            heirarchy = map(repr_func, [n for n in self.get_hierarchy(node)])
            self._add_to_nested_tree(n_tree, heirarchy)
        return self._nested_dict(n_tree)

    def render(self):
        """Returns the tree structure as a string"""
        out = []
        levels = []
        for root_node in sorted(self.root_nodes, key=lambda n: n.name):
            for node, level in self.walk_with_level(root_node):
                for index, (lv, out_string) in enumerate(
                        zip(reversed(levels), reversed(out))):
                    if lv == level - 1:
                        break
                    if lv > level:
                        new_out_string = self._add_level_to_string(
                            level,
                            out_string,
                        )
                        out[len(out) - 1 - index] = new_out_string
                levels.append(level)
                out.append('{0}{1}{2}'.format(
                    self._indentation * level,
                    self._node_char,
                    node.name,
                    ),
                )
        return '\n'.join(self._add_spacing(out))

    def _add_spacing(self, lines):
        out = []
        for index, string in enumerate(lines):
            out.append(string)
            if index + 1 < len(lines):
                spacer = []
                for char in lines[index + 1]:
                    if char != self._pipe_char:
                        spacer.append(self._indentation_char)
                    else:
                        spacer.append(self._pipe_char)
                spacer_string = ''.join(spacer).rstrip(self._indentation_char)
                out.append(spacer_string)
        return out

    def _add_level_to_string(self, level, string):
        string_levels = string.split(self._indentation)
        string_levels[level] = self._pipe_char
        return (self._indentation).join(string_levels)

    def _get_root_nodes(self):
        """Get all root nodes i.e, nodes with `None` as parent"""
        return [node for node in self.nodes if node.parent is None]

    def _is_visited(self, visited, node):
        if node is not None:
            return node.nid in visited
        return False

    def _add_to_visited(self, visited, node):
        if node is not None:
            visited.append(node.nid)

    # From https://gist.github.com/hrldcpr/2012250
    def _nested_tree(self):
        return collections.defaultdict(self._nested_tree)

    def _add_to_nested_tree(self, nested_tree, path):
        for node in path:
            nested_tree = nested_tree[node]

    def _nested_dict(self, nested_tree):
        return {k: self._nested_dict(nested_tree[k]) for k in nested_tree}

    @classmethod
    def _create_nodes_from_dict(cls, d):
        uid_tree, name_map = cls._make_uid_tree(d)
        node_map = {}
        cls._create_nodes_recursively(uid_tree, name_map, node_map)
        return node_map.values()

    @classmethod
    def _make_uid_tree(cls, d):
        uid_tree = {}
        name_map = {}
        cls._recurse_uid_tree(d, uid_tree, name_map)
        return uid_tree, name_map

    @classmethod
    def _recurse_uid_tree(cls, d, uid_tree, name_map):
        for k, v in d.items():
            new_k = uuid.uuid4().hex[:8]
            name_map[new_k] = k
            uid_tree[new_k] = {}
            cls._recurse_uid_tree(v, uid_tree[new_k], name_map)

    @classmethod
    def _create_nodes_recursively(
            cls, uid_dict, name_map, node_map, parent_uid=None):
        for uid in uid_dict:
            if parent_uid is None:
                node_map.setdefault(uid, Node(name=name_map[uid]))
            for child_uid in uid_dict[uid]:
                node_map.setdefault(
                    child_uid,
                    Node(name=name_map[child_uid], parent=node_map[uid]),
                )
            cls._create_nodes_recursively(
                uid_dict[uid], name_map, node_map, parent_uid=uid)

    def __eq__(self, other):
        return self.to_dict(repr_as='nid') == other.to_dict(repr_as='nid')

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return formatter.FormattedDict(self.to_dict(repr_as='name')).__repr__()
