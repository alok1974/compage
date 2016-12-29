import random
from compage import nodeutil, exception
import unittest


def make_random_nodes(num_nodes):
    node_names = [str(i).zfill(2) for i in range(num_nodes)]
    nodes = []
    curr_parent = None
    for index, node_name in enumerate(node_names):
        if index == 0:
            curr_parent = None

        node = nodeutil.Node(node_name, curr_parent)
        nodes.append(node)

        # Select a random parent for this node
        curr_parent = random.choice(nodes)
    return nodes


class TestNode(unittest.TestCase):
    def setUp(self):
        self.parent_node = nodeutil.Node('parent', None)
        self.parent_nid = self.parent_node.nid
        self.node = nodeutil.Node('node', self.parent_node)
        self.node_nid = self.node.nid

    def tearDown(self):
        pass

    def test_node_creation_01(self):
        with self.assertRaises(exception.NodeCreationError):
            nodeutil.Node('node', 'not a valid parent')

    def test_node_creation_02(self):
        self.assertTrue(isinstance(self.node, nodeutil.Node))

    def test_name(self):
        self.assertEqual(self.node.name, 'node')

    def test_parent(self):
        self.assertEqual(self.node.parent, self.parent_node)

    def test_nid(self):
        self.assertEqual(self.node.nid, self.node_nid)

    def test_short_info(self):
        self.assertEqual(
            self.node.short_info, "Node(node|{0})".format(self.node_nid[:5]))

    def test_eq(self):
        self.assertEqual(self.node, self.node)

    def test_neq(self):
        node = nodeutil.Node('node', self.parent_node)
        self.assertNotEqual(node, self.node)

    def test_repr(self):
        self.assertEqual(
            repr(self.node),
            "Node(node|{0}|parent='parent|{1}')".format(
                self.node_nid,
                self.parent_nid,
                ),
        )


class TestNodeutil(unittest.TestCase):
    def setUp(self):
        self.tree_dict = {
            'a': {
                'b': {
                    'c': {}
                },
                'd': {
                    'e': {},
                    'h': {
                        'i': {},
                        'j': {},
                    }
                },
            },
            'f': {
                'g': {}
            },
        }

        self.tree = nodeutil.Tree.from_dict(self.tree_dict)

    def tearDown(self):
        pass

    def test_root_nodes(self):
        root_nodes = sorted([node.name for node in self.tree.root_nodes])
        self.assertEqual(root_nodes, ['a', 'f'])

    def test_get_leaf_nodes(self):
        leaf_nodes = sorted([node.name for node in self.tree.get_leaf_nodes()])
        self.assertEqual(leaf_nodes, ['c', 'e', 'g', 'i', 'j'])

    def test_walk(self):
        for root_node in sorted(self.tree.root_nodes, key=lambda n: n.name):
            node_names_string = ''.join(
                sorted([node.name for node in self.tree.walk(root_node)]))
            if root_node.name == 'a':
                expected_string = 'abcdehij'
            else:
                expected_string = 'fg'
            self.assertEqual(node_names_string, expected_string)

    def test_get_children(self):
        children_map = {
            'a': ['b', 'd'],
            'b': ['c'],
            'c': [],
            'd': ['e', 'h'],
            'e': [],
            'f': ['g'],
            'g': [],
            'h': ['i', 'j'],
            'i': [],
            'j': [],
        }

        for node in self.tree.nodes:
            children = sorted(
                [child.name for child in self.tree.get_children(node)])
            self.assertEqual(children, children_map.get(node.name))

    def test_get_lineage(self):
        lineage_map = {
            'a': [],
            'b': ['a'],
            'c': ['b', 'a'],
            'd': ['a'],
            'e': ['d', 'a'],
            'f': [],
            'g': ['f'],
            'h': ['d', 'a'],
            'i': ['h', 'd', 'a'],
            'j': ['h', 'd', 'a'],
        }

        for node in sorted(self.tree.nodes, key=lambda n: n.name):
            lineage = [n.name for n in self.tree.get_lineage(node)]
            self.assertEqual(lineage, lineage_map.get(node.name))

    def test_get_hierarchy(self):
        hierarchy_map = {
            'a': '/a',
            'b': '/a/b',
            'c': '/a/b/c',
            'd': '/a/d',
            'e': '/a/d/e',
            'f': '/f',
            'g': '/f/g',
            'h': '/a/d/h',
            'i': '/a/d/h/i',
            'j': '/a/d/h/j',
        }

        for node in sorted(self.tree.nodes, key=lambda n: n.name):
            hierarchy = ''.join(
                sorted(
                    ['/{0}'.format(node.name)
                     for node in self.tree.get_hierarchy(node)],
                ),
            )
            self.assertEqual(hierarchy, hierarchy_map.get(node.name))

    def test_to_dict(self):
        self.assertEqual(self.tree.to_dict(repr_as='name'), self.tree_dict)

    def test_eq(self):
        tree = self.tree
        self.assertEqual(tree, self.tree)

    def test_neq(self):
        tree = nodeutil.Tree.from_dict(self.tree_dict)
        self.assertNotEqual(tree, self.tree)

    def test_repr(self):
        expected_string = (
            '{\n'
            '    "a": {\n'
            '        "b": {\n'
            '            "c": {}\n'
            '        }, \n'
            '        "d": {\n'
            '            "h": {\n'
            '                "i": {}, \n'
            '                "j": {}\n'
            '            }, \n'
            '            "e": {}\n'
            '        }\n'
            '    }, \n'
            '    "f": {\n'
            '        "g": {}\n'
            '    }\n'
            '}'
        )

        self.assertEqual(self.tree.__repr__(), expected_string)


if __name__ == '__main__':
    unittest.main()
