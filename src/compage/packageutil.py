"""
Utility classes for Creating a Python Packages either randomly (for tests)
or from a given structure in the form of a dictionary
"""
import os
import pkgutil
import random
import uuid


from compage import formatter, logger, nodeutil


class FileNode(nodeutil.Node):
    def __init__(self, name, isdir=None, imports=None, parent=None):
        super(FileNode, self).__init__(name=name, parent=parent)
        self.isdir = isdir
        self.imports = imports or []

    @property
    def contents(self):
        return ''.join(map(lambda m: 'import {0}\n'.format(m), self.imports))


class FileTree(nodeutil.Tree):
    def __init__(self, nodes, site=None):
        super(FileTree, self).__init__(nodes=nodes)
        self.site = site

    @property
    def num_dirs(self):
        return len([node for node in self.nodes if node.isdir])

    @property
    def num_files(self):
        return len([node for node in self.nodes if not node.isdir])

    def make_tree(self, log_msg=False):
        if self.site is None:
            raise IOError('No site specified, unable to make tree')

        for node in self.nodes:
            hierarchy = map(lambda node: node.name, self.get_hierarchy(node))
            node_path = os.path.join(self.site, *hierarchy)
            self._create_dir(os.path.dirname(node_path))
            if not node.isdir:
                with open(node_path, 'w') as fp:
                    fp.write(node.contents)
        msg = ("Created '{0}'({1} directories,"
               " {2} files) at site \"{3}\"").format(
            self.root_nodes[0].name, self.num_dirs, self.num_files, self.site)

        if log_msg:
            logger.Logger.info(msg)

    def _create_dir(self, path):
        if not os.path.exists(path):
            os.makedirs(path)


class Package(object):
    """
    Creates a mock python style package randomly or from
    a given tree structure
    """
    def __init__(self, site, package_name, node_class=None, tree_class=None):
        super(Package, self).__init__()
        self.site = site
        self.package_name = package_name
        self.node_class = node_class or FileNode
        self.tree_class = tree_class or FileTree
        self.import_map = None
        self.file_tree = None
        self.file_paths = None

    @classmethod
    def from_random(cls, site, package_name, min_max_nodes, min_max_imports,
                    node_class=None, tree_class=None, log_msg=False):

        instance = cls(
            site=site,
            package_name=package_name,
            node_class=node_class,
            tree_class=tree_class,
        )

        nodes, import_map = instance._random_file_nodes(
            min_max_nodes=min_max_nodes,
            min_max_imports=min_max_imports,
        )

        instance.import_map = import_map
        instance.file_tree = instance.tree_class(nodes, instance.site)
        instance.file_tree.make_tree(log_msg=log_msg)
        instance.file_paths = instance._get_file_paths()

        return instance

    @classmethod
    def from_dir_tree(cls, site, dir_tree, import_map, node_class=None,
                      tree_class=None, log_msg=False):
        instance = cls(
            site=site,
            package_name=dir_tree.keys()[0],
            node_class=node_class,
            tree_class=tree_class,
        )

        instance.import_map = import_map

        instance.file_tree = instance.tree_class.from_dict(
            dir_tree, node_cls=instance.node_class)

        leaf_nodes = [n for n in instance.file_tree.get_leaf_nodes()]
        for node in instance.file_tree.nodes:
            if node in leaf_nodes:
                node.isdir = False
                node.imports = import_map.get(node.name, [])
            else:
                node.isdir = True
                node.imports = []

        instance.file_tree.site = instance.site
        instance.file_tree.make_tree(log_msg=log_msg)
        instance.file_paths = instance._get_file_paths()

        return instance

    def _random_file_nodes(self, min_max_nodes, min_max_imports):
        """Creates random nodes that can be ingested by a tree"""
        import_map = {}
        min_imports, max_imports = self._validate_min_max_imports(
            *min_max_imports)
        min_nodes, max_nodes = self._validate_min_max(*min_max_nodes)

        # Make root node and __init__.py inside it
        root_node, initpy_node = self._make_dir_node(self.package_name, None)
        nodes = [root_node, initpy_node]

        curr_parent = root_node
        module_names = [m for _, m, _ in pkgutil.iter_modules()
                        if self._is_module_name_valid(m)]
        num_nodes = random.randint(min_nodes, max_nodes)
        for i in range(num_nodes):
            name = formatter.hex_to_alpha(uuid.uuid4().hex[:5])

            # Randomize dir creation
            isdir = bool(random.randint(0, 1))

            if isdir:
                dir_node, initpy_node = self._make_dir_node(name, curr_parent)
                nodes += [dir_node, initpy_node]
            else:
                num_imports = random.randint(min_imports, max_imports)

                # Randomize modules for import statement
                imports = [random.choice(module_names)
                           for i in range(num_imports)]
                name = '{0}.py'.format(name)

                nodes.append(
                    self.node_class(
                        name=name,
                        parent=curr_parent,
                        imports=imports,
                        isdir=False,
                    )
                )

                # Add file node to import map
                import_map[name] = imports

            # Randomize going up or down the tree
            # by selecting a random upstream dir
            curr_parent = random.choice([n for n in nodes if n.isdir])

        return nodes, import_map

    def _validate_min_max(self, min_num, max_num):
        if min_num > max_num:
            min_num = max_num
        return min_num, max_num

    def _validate_min_max_imports(self, min_imports, max_imports):
        max_imports, _ = self._validate_min_max(
            max_imports, len(list(pkgutil.iter_modules())))
        return self._validate_min_max(min_imports, max_imports)

    def _is_module_name_valid(self, module_name):
        return (not module_name.startswith('_')
                and all(map(str.islower, [char for char in module_name])))

    def _make_dir_node(self, node_name, parent):
        dir_node = self.node_class(
            name=node_name,
            parent=parent,
            imports=None,
            isdir=True,
        )

        # Make __init__.py Node for dir node
        initpy_node = self.node_class(
            name='__init__.py',
            parent=dir_node,
            imports=None,
            isdir=False,
        )

        return dir_node, initpy_node

    def _get_file_paths(self):
        file_paths = {}
        for file_name in self.import_map:
            file_node = self.file_tree.find(
                attr_name='name',
                attr_value=file_name,
                )[0]
            file_path = ''.join(
                [self.site]
                + ['/{0}'.format(node.name)
                   for node in self.file_tree.get_hierarchy(file_node)]
            )
            file_paths[file_name] = file_path
        return file_paths
