import os
import unittest
import tempfile
import shutil
import uuid
import random
import pkgutil
import collections


from compage import report, logger, formatter, nodeutil


class FileNode(nodeutil.Node):
    def __init__(self, name, isdir, imports, parent=None):
        super(FileNode, self).__init__(name=name, parent=parent)
        self.isdir = isdir
        self.imports = imports or []

    @property
    def contents(self):
        return ''.join(map(lambda m: 'import {0}\n'.format(m), self.imports))


class FileTree(nodeutil.Tree):
    def __init__(self, nodes, site):
        super(FileTree, self).__init__(nodes=nodes)
        self.site = site

    @property
    def num_dirs(self):
        return len([node for node in self.nodes if node.isdir])

    @property
    def num_files(self):
        return len([node for node in self.nodes if not node.isdir])

    def make_tree(self, log_msg=False):
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


def validate_min_max(min_num, max_num):
    if min_num > max_num:
        min_num = max_num
    return min_num, max_num


def validate_min_max_imports(min_imports, max_imports):
    max_imports, _ = validate_min_max(
        max_imports, len(list(pkgutil.iter_modules())))
    return validate_min_max(min_imports, max_imports)


def is_module_name_valid(module_name):
    return (not module_name.startswith('_')
            and all(map(str.islower, [char for char in module_name])))


def make_dir_node(node_name, parent):
    dir_node = FileNode(
        name=node_name,
        parent=parent,
        imports=None,
        isdir=True,
    )

    # Make __init__.py Node for dir node
    initpy_node = FileNode(
        name='__init__.py',
        parent=dir_node,
        imports=None,
        isdir=False,
    )

    return dir_node, initpy_node


def create_random_filenodes(root, min_max_nodes, min_max_imports):
    """Creates tree from random nodes"""
    import_map = {}
    min_imports, max_imports = validate_min_max_imports(*min_max_imports)
    min_nodes, max_nodes = validate_min_max(*min_max_nodes)

    # Make root node and __init__.py inside it
    root_node, initpy_node = make_dir_node(root, None)
    nodes = [root_node, initpy_node]

    curr_parent = root_node
    module_names = [m for _, m, _ in pkgutil.iter_modules()
                    if is_module_name_valid(m)]
    num_nodes = random.randint(min_nodes, max_nodes)
    for i in range(num_nodes):
        name = formatter.hex_to_alpha(uuid.uuid4().hex)

        # Randomize dir creation
        isdir = bool(random.randint(0, 1))

        if isdir:
            dir_node, initpy_node = make_dir_node(name, curr_parent)
            nodes += [dir_node, initpy_node]
        else:
            num_imports = random.randint(min_imports, max_imports)

            # Randomize modules for import statement
            imports = [random.choice(module_names) for i in range(num_imports)]
            name = '{0}.py'.format(name)

            nodes.append(
                FileNode(
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


def make_mock_package(site, package_name):
    nodes, _ = create_random_filenodes(
        package_name,
        min_max_nodes=(5, 8),
        min_max_imports=(1, 3),
    )

    file_tree = FileTree(nodes, site)
    file_tree.make_tree(log_msg=True)


class TestImportReporter(unittest.TestCase):
    def setUp(self):
        self.log_msg = False
        self.package_name = 'mock_package'
        self.package_root = tempfile.mkdtemp()
        self.width = 79
        self.required_packages = []
        self.file_tree, self.import_map = self._make_tree()
        self.file_paths = self._get_file_paths()
        self.import_reporter = report.ImportReporter(
            self.package_root,
            required_packages=self.required_packages,
            width=self.width,
        )

    def _make_tree(self):
        nodes, import_map = create_random_filenodes(
            self.package_name,
            min_max_nodes=(20, 30),
            min_max_imports=(5, 8),
        )

        file_tree = FileTree(nodes, self.package_root)
        file_tree.make_tree(log_msg=self.log_msg)

        return file_tree, import_map

    def _get_file_paths(self):
        file_paths = {}
        for file_name in self.import_map:
            file_node = self.file_tree.find(
                attr_name='name',
                attr_value=file_name,
                )[0]
            file_path = ''.join(
                [self.package_root]
                + ['/{0}'.format(node.name)
                   for node in self.file_tree.get_hierarchy(file_node)]
            )
            file_paths[file_name] = file_path
        return file_paths

    def _get_module_report(self, module_name, has_header=False):
        out = []
        import_data = {}
        for file_name, imports in self.import_map.iteritems():
            for index, import_name in enumerate(imports):
                if import_name == module_name:
                    import_data.setdefault(
                        self.file_paths.get(file_name), []).append(index + 1)

        if not has_header:
            report_header = ("\nImport Report for '{0}'").format(module_name)
            out.append(report_header)

        required = None
        if self.required_packages:
            if module_name in self._required_packages:
                required = '\nIn Required: Yes'
            else:
                required = '\nIn Required: No'
        else:
            required = ''
        msg = "Module Name: '{0}'{1}".format(module_name, required)
        out.append(formatter.format_header(msg=msg, width=self.width))

        for file_path in sorted(import_data.keys()):
            out.append('"{0}"'.format(file_path))
            for lineno in import_data[file_path]:
                line = 'import {0}\n'.format(module_name)
                msg = "line {0}:\n{1}".format(lineno, line)
                out.append(msg)

        return out

    def _get_import_report(self):
        out = []
        report_header = '\nImport Report'
        out.append(report_header)
        for module_name in sorted(self.import_reporter.modules):
            out += self._get_module_report(module_name, has_header=True)

        if not self.required_packages:
            return formatter.format_output(out, width=self.width)

        required_extras = sorted(
            set(self.required_packages).difference(
                self.import_reporter.modules))
        if required_extras:
            msg = 'Following packages are required but never imported:'
            out.append(formatter.format_header(msg=msg, width=self.width))
            out.append(formatter.format_iterable(required_extras))
        return formatter.format_output(out, width=self.width)

    def tearDown(self):
        if os.path.exists(self.package_root):
            shutil.rmtree(self.package_root)

            msg = 'Removed package \'{0}\'from site "{1}"'.format(
                self.package_name, self.package_root)

            if self.log_msg:
                logger.Logger.info(msg)

    def test_modules(self):
        expected_modules = []
        for modules in self.import_map.values():
            for module in modules:
                expected_modules.append(module)
        expected_modules = sorted(list(set(expected_modules)))
        self.assertEqual(self.import_reporter.modules, expected_modules)

    def test_import_report(self):
        self.assertEqual(
            self.import_reporter.import_report(), self._get_import_report())

    def test_rank_report(self):
        ranks = collections.defaultdict(int)
        for modules in self.import_map.values():
            for module in modules:
                ranks[module] += 1

        for module_name, import_count in self.import_reporter.rank_report():
            self.assertEqual(import_count, ranks.get(module_name))

    def test_module_report(self):
        for module in self.import_reporter.modules:
            test_module_report = formatter.format_output(
                self._get_module_report(module),
                width=self.width,
            )

            reporter_module_report = self.import_reporter.module_report(module)
            self.assertEqual(reporter_module_report, test_module_report)


if __name__ == '__main__':
    unittest.main()
