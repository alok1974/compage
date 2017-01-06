"""Generic Node and Tree Objects"""
import uuid
import collections

from compage import formatter, exception


__all__ = ['Node', 'Tree']


class Node(object):
    """The node object, holds parent information"""
    __slots__ = ('_name', '_parent', '_uid')

    def __init__(self, name, parent=None, uid=None):
        if not self._valid_parent(parent):
            msg = "parent '{0}' should be of type {1} or None".format(
                parent, Node)
            raise exception.NodeCreationError(msg)

        super(Node, self).__init__()
        self._name = name
        self._parent = parent
        self._uid = uid or uuid.uuid4().hex[:8]

    @property
    def name(self):
        return self._name

    @property
    def parent(self):
        return self._parent

    @property
    def uid(self):
        return self._uid

    @property
    def short_info(self):
        return "{0}({1}|{2})".format(
            self.__class__.__name__,
            self.name,
            self.uid[:5],
        )

    def _valid_parent(self, parent):
        return parent is None or isinstance(parent, Node)

    def __eq__(self, other):
        if other is None:
            return False
        return self.uid == other.uid

    def __neq__(self, other):
        return not self == other

    def __repr__(self):
        return "{0}({1}|{2}|parent='{3}|{4}')".format(
            self.__class__.__name__,
            self.name,
            self.uid,
            self.parent.name if self.parent else None,
            self.parent.uid if self.parent else None,
        )


class Tree(object):
    """Provides queries on the given node objects"""
    def __init__(self, nodes):
        if not self._unique(nodes):
            msg = "Some of the nodes have same uids, unable to create tree"
            raise exception.TreeCreationError(msg)

        super(Tree, self).__init__()
        self._parent_child_map, self._uid_map = self._get_maps(nodes)
        self._setup_render_chars()

    @classmethod
    def from_dict(cls, tree_dict, node_cls=None):
        """
        Creates a Tree from dictionary

        Args:
            tree_dict (dict)
                A nested dictionary specifying the tree stucture.
                All keys must be strings and leaf nodes should have `{}` as
                value.

                For example, a tree like

                |__ root
                    |
                    |__ node1
                    |
                    |__ node2
                    |   |
                    |   |__node3
                    |   |
                    |   |__node4
                    |
                    |__node5

                should have a tree_dict as
                {
                    'root': {
                        'node1': {},
                        'node2': {
                            'node3': {},
                            'node4': {},
                        },
                        'node5': {},
                    },
                }

            node_cls (class, optional):
                A class for creating nodes. If not given the default
                nodeutil.Node class is used for node creation.

            Returns:
                `Tree` object

        """
        cls.node_cls = node_cls or Node
        nodes = cls._create_nodes_from_dict(tree_dict)
        return cls(nodes)

    @property
    def nodes(self):
        return self._uid_map.values()

    @property
    def root_nodes(self):
        """All root nodes, i.e. nodes with `None` as parent"""
        return [self._uid_map[uid]
                for uid in self._parent_child_map.get(None, [])]

    def find(self, attr_name, attr_value):
        """Finds nodes with the given node attribute and value"""
        if attr_name == 'uid':
            yield self._uid_map[attr_value]
        else:
            for node in self.nodes:
                if getattr(node, attr_name) == attr_value:
                    yield node

    def get_leaf_nodes(self):
        """Get all leaf nodes i.e, nodes with no children"""
        for uid, node in self._uid_map.iteritems():
            if uid not in self._parent_child_map:
                yield node

    def walk(self, tree_node, get_level=False):
        """
        Depth first iterator for the given node

        Args:
            tree_node (Node):
                The `Node` object to start walking from

            get_level (bool, optional):
                If `True` will return the level of the node

        Returns:
            Node and optionally the depth level of the node. `0` is
            the first level.
        """
        for node, level in self._walk(tree_node):
            if get_level:
                yield node, level
            else:
                yield node

    def get_children(self, tree_node):
        """Iterator for immediate children of the given node"""
        for child_uid in self._parent_child_map.get(tree_node.uid, []):
            yield self._uid_map[child_uid]

    def get_lineage(self, tree_node):
        """
        Iterator for all parents of the given node starting
        from the parent of the node to the top ancestor
        """
        if tree_node.parent is None:
            return

        yield tree_node.parent

        for parent in self.get_lineage(tree_node.parent):
            yield parent

    def get_hierarchy(self, tree_node):
        """
        Return a list of nodes representing the hierarchy
        from the top parent to the node
        """
        return list(reversed(list(self.get_lineage(tree_node)))) + [tree_node]

    def to_dict(self, repr_as=None):
        """
        Returns the tree as a dictionary

        Args:
            repr_as (str, optional):
                For displaying information, this can be set to attribute name
                of the node like - name, uid, short_info, parent etc.
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
        return formatter.FormattedDict(self._nested_dict(n_tree))

    def render(self):
        """Returns the tree structure as a string"""
        out = []
        levels = []
        for root_node in sorted(self.root_nodes, key=lambda n: n.name):
            for node, level in self.walk(root_node, get_level=True):
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

    def _setup_render_chars(self):
        # characters for rendering tree
        self._pipe_char = '|'
        self._node_end_char = '_'
        self._indentation_char = ' '
        self._indent = 4
        self._indentation = self._indent * self._indentation_char
        self._node_char = '{0}{1} '.format(
            self._pipe_char, self._node_end_char * max([1, self._indent - 1]))

    def _walk(self, tree_node, level=0):
        yield tree_node, level
        for child in sorted(
                list(self.get_children(tree_node)), key=lambda n: n.name):
            for node, node_level in self._walk(child, level + 1):
                yield node, node_level

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
                node_map.setdefault(uid, cls.node_cls(name=name_map[uid]))
            for child_uid in uid_dict[uid]:
                node_map.setdefault(
                    child_uid,
                    cls.node_cls(
                        name=name_map[child_uid], parent=node_map[uid]),
                )
            cls._create_nodes_recursively(
                uid_dict[uid], name_map, node_map, parent_uid=uid)

    def _get_maps(self, nodes):
        _parent_child_map = {}
        _uid_map = {}
        for node in nodes:
            parent_uid = node.parent.uid if node.parent is not None else None
            _parent_child_map.setdefault(parent_uid, []).append(node.uid)
            _uid_map[node.uid] = node
        return _parent_child_map, _uid_map

    def _unique(self, nodes):
        uids = [node.uid for node in nodes]
        return len(uids) == len(list(set(uids)))

    def __eq__(self, other):
        return self.to_dict(repr_as='uid') == other.to_dict(repr_as='uid')

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return formatter.FormattedDict(self.to_dict(repr_as='name')).__repr__()
