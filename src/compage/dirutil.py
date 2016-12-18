"""Utilities for creating directory, files"""
import os


from compage import nodeutil, logger


class FileNode(nodeutil.Node):
    def __init__(self, name, parent, isdir, contents=None):
        super(FileNode, self).__init__(name, parent)
        self._isdir = isdir
        self._contents = contents or ''

    @property
    def isdir(self):
        return self._isdir

    @property
    def contents(self):
        return self._contents


class FileTree(object):
    def __init__(self, root, nodes):
        super(FileTree, self).__init__()
        self.nodes = nodes
        self.root = root
        self.num_dirs = self._get_num_dirs()
        self.num_files = self._get_num_files()

    def make_tree(self):
        tree = nodeutil.Tree(self.nodes)
        package_name = tree.get_root_nodes()[0].name
        for node in tree.nodes:
            lineage = [n.name for n in tree.get_lineage(node) if n]
            hierarchy = [n for n in reversed(lineage)] + [node.name]

            node_path = os.path.join(self.root, *hierarchy)
            if node.isdir:
                if not os.path.exists(node_path):
                    os.makedirs(node_path)
            else:
                with open(node_path, 'w') as fp:
                    fp.write(node.contents)

        msg = ("Created package '{0}'({1} directories,"
               " {2} files) at site \"{3}\"").format(
            package_name, self.num_dirs, self.num_files, self.root)
        logger.Logger.info(msg)

    def _get_num_dirs(self):
        return len([node for node in self.nodes if node.isdir])

    def _get_num_files(self):
        return len([node for node in self.nodes if not node.isdir])
