import unittest
import uuid


from compage import nodeutil, exception


class TestNode(unittest.TestCase):
    def setUp(self):
        self.parent_node = nodeutil.Node('parent', None)
        self.parent_nid = self.parent_node.nid
        self.node_nid = uuid.uuid4().hex
        self.node = nodeutil.Node('node', self.parent_node)
        self.node_nid = self.node.nid

    def tearDown(self):
        pass

    def test_node_init_01(self):
        with self.assertRaises(exception.NodeCreationError):
            nodeutil.Node('node', 'not a valid parent')

    def test_node_init_02(self):
        self.assertTrue(isinstance(self.node, nodeutil.Node))

    def test_name(self):
        self.assertEqual(self.node.name, 'node')

    def test_parent(self):
        self.assertEqual(self.node.parent, self.parent_node)

    def test_nid(self):
        node = nodeutil.Node(name='node', parent=None, nid='foo')
        self.assertEqual(node.nid, 'foo')

    def test_short_info(self):
        self.assertEqual(
            self.node.short_info, "Node(node|{0})".format(self.node_nid[:5]))

    def test_eq(self):
        other_node = nodeutil.Node(
            'node', parent=self.parent_node, nid=self.node_nid)
        self.assertEqual(self.node, other_node)

    def test_neq(self):
        other_node = nodeutil.Node('node', self.parent_node, nid='foo')
        self.assertNotEqual(self.node, other_node)

    def test_repr(self):
        self.assertEqual(
            repr(self.node),
            "Node(node|{0}|parent='parent|{1}')".format(
                self.node_nid,
                self.parent_nid,
                ),
        )


class TestTree(unittest.TestCase):
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

    def test_tree_init(self):
        chars = 'abcdefghijkl'
        nodes = [nodeutil.Node(name=char, nid='nid') for char in chars]
        with self.assertRaises(exception.TreeCreationError):
            nodeutil.Tree(nodes)

    def test_from_dict(self):
        other_tree = nodeutil.Tree.from_dict(self.tree_dict)
        self.assertEqual(
            other_tree.to_dict(repr_as='name'),
            self.tree.to_dict(repr_as='name'),
        )

    def test_root_nodes(self):
        root_nodes = sorted([node.name for node in self.tree.root_nodes])
        self.assertEqual(root_nodes, ['a', 'f'])

    def test_find(self):
        node_names = [node.name for node in self.tree.nodes]
        for node_name in node_names:
            node = list(self.tree.find(
                attr_name='name',
                attr_value=node_name,
                ),
            )[0]
            self.assertEqual(node.name, node_name)

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

    def test_walk_with_level(self):
        for root_node in sorted(self.tree.root_nodes, key=lambda n: n.name):
            node_level_string = ','.join(
                sorted(
                    ['{0}:{1}'.format(node.name, level)
                     for node, level in self.tree.walk(
                        root_node,
                        get_level=True,
                        )
                     ],
                ),
            )
            if root_node.name == 'a':
                expected_string = 'a:0,b:1,c:2,d:1,e:2,h:2,i:3,j:3'
            else:
                expected_string = 'f:0,g:1'
            self.assertEqual(node_level_string, expected_string)

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
            children = [child.name for child in self.tree.get_children(node)]
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
                ['/{0}'.format(node.name)
                 for node in self.tree.get_hierarchy(node)]
            )
            self.assertEqual(hierarchy, hierarchy_map.get(node.name))

    def test_to_dict(self):
        self.assertEqual(self.tree.to_dict(repr_as='name'), self.tree_dict)

    def test_render(self):
        expected_string = (
            '|___ a\n'
            '|    |\n'
            '|    |___ b\n'
            '|    |    |\n'
            '|    |    |___ c\n'
            '|    |\n'
            '|    |___ d\n'
            '|        |\n'
            '|        |___ e\n'
            '|        |\n'
            '|        |___ h\n'
            '|            |\n'
            '|            |___ i\n'
            '|            |\n'
            '|            |___ j\n'
            '|\n'
            '|___ f\n'
            '    |\n'
            '    |___ g'
        )

        self.assertEqual(self.tree.render(), expected_string)

    def test_eq(self):
        other_nodes = []
        for node in self.tree.nodes:
            other_nodes.append(nodeutil.Node(
                name=node.name, parent=node.parent, nid=node.nid))
        other_tree = nodeutil.Tree(other_nodes)
        self.assertEqual(self.tree, other_tree)

    def test_neq(self):
        # This will generate a tree different nid for each node
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
