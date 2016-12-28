import random
from compage import formatter, nodeutil, exception
import pprint
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


# class TestNodeutil(unittest.TestCase):
#     def setUp(self):
#         self.nodes = make_random_nodes(10)
#         self.tree_from_random_nodes = nodeutil.Tree(self.nodes)
#         self.tree_dict = {
#             '00': {
#                 '01': {
#                     '04': {
#                         '10': {},
#                     },
#                     '05': {
#                         '11': {
#                             '12': {},
#                         },
#                     },
#                 },
#                 '02': {
#                     '07': {
#                         '13': {},
#                     },
#                 },
#                 '03': {
#                     '09': {},
#                 },
#                 '06': {
#                     '08': {},
#                 },
#             },
#             '99': {
#                 '11': {
#                     '48': {
#                         '39': {},
#                     },
#                 },
#                 '12': {
#                     '54': {
#                         '67': {},
#                     },
#                     '88': {
#                         '78': {},
#                     },
#                 },
#             },

#         }

#         self.tree_from_dict = nodeutil.Tree.from_dict(self.tree_dict)

#         self.tree = self.tree_from_dict

#     def tearDown(self):
#         pass

#     # def test_get_lineage(self):
#     #     nodes = self.tree.nodes
#     #     out = []
#     #     for node in nodes:
#     #         out.append('node: {0}'.format(node.name))
#     #         out.append(
#     #             'lineage: {0}'.format(
#     #                 [n.name for n in self.tree.get_lineage(node) if n])
#     #         )
#     #         out.append('')

#     #     print formatter.format_output(out, width=79)

#     # def test_to_dict(self):
#     #     repr_as = 'name'
#     #     s = pprint.pformat(self.tree.to_dict(repr_as=repr_as))
#     #     print s

#     # def test_get_hierarchy(self):
#     #     leaf_nodes = list(self.tree.get_leaf_nodes())

#     #     for leaf_node in leaf_nodes:
#     #         hierarchy = self.tree.get_hierarchy(leaf_node)
#     #         pretty_hierarchy = ' || '.join(
#     #             ["Node('{0}')".format(node.name) for node in hierarchy])

#     #         print "node: Node('{0}')".format(leaf_node.name)
#     #         print 'heirarchy: {0}'.format(pretty_hierarchy)


if __name__ == '__main__':
    unittest.main()
