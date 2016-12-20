"""Utilities for creating directory, files"""
import os


from compage import nodeutil, logger


__all__ = ['FileNode', 'FileTree']


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


class FileTree(nodeutil.Tree):
    def __init__(self, site, nodes):
        super(FileTree, self).__init__(nodes)
        self.site = site
        self.num_dirs = self._get_num_dirs()
        self.num_files = self._get_num_files()

    def make_tree(self):
        for node in self.nodes:
            hierarchy = map(lambda node: node.name, self.get_hierarchy(node))
            node_path = os.path.join(self.site, *hierarchy)
            if node.isdir:
                if not os.path.exists(node_path):
                    os.makedirs(node_path)
            else:
                with open(node_path, 'w') as fp:
                    fp.write(node.contents)

        msg = ("Created dir tree '{0}'({1} directories,"
               " {2} files) at site \"{3}\"").format(
            self.root_nodes[0].name, self.num_dirs, self.num_files, self.site)
        logger.Logger.info(msg)

    def _get_num_dirs(self):
        return len([node for node in self.nodes if node.isdir])

    def _get_num_files(self):
        return len([node for node in self.nodes if not node.isdir])
