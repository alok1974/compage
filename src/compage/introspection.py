"""Code Introspection Utilities"""
import os
import struct
import itertools
import dis
import collections

LOAD_CONST = chr(dis.opname.index('LOAD_CONST'))
IMPORT_NAME = chr(dis.opname.index('IMPORT_NAME'))
STORE_NAME = chr(dis.opname.index('STORE_NAME'))
STORE_GLOBAL = chr(dis.opname.index('STORE_GLOBAL'))
STORE_OPS = [STORE_NAME, STORE_GLOBAL]
HAVE_ARGUMENT = chr(dis.HAVE_ARGUMENT)


# Adapted from stdlib 'modulefinder'
class ImportScanner(object):
    """Scanner for extracting `import` statement in the source code"""
    def __init__(self, pathname):
        super(ImportScanner, self).__init__()
        self._code = self._get_code_oject(pathname)
        self._source = self._get_source_code(pathname)
        self._imports = None

    @property
    def imports(self):
        if self._imports is None:
            self._imports = []
            self._scan_code(self._code)
        return self._imports

    def _get_source_code(self, pathname):
        source = None
        with open(pathname, 'r') as fp:
            source = dict(enumerate(fp.readlines()))
        return source

    def _get_code_oject(self, pathname):
        code = None
        with open(pathname, 'r') as fp:
            code = compile(fp.read() + '\n', pathname, 'exec')
        return code

    def _scanner(self, co):
        code = co.co_code
        names = co.co_names
        consts = co.co_consts
        LOAD_LOAD_AND_IMPORT = LOAD_CONST + LOAD_CONST + IMPORT_NAME
        i = 0
        while code:
            c = code[0]
            if c in STORE_OPS:
                oparg, = struct.unpack('<H', code[1:3])
                yield "store", (i, names[oparg],)
                code = code[3:]
                i += 3
                continue
            if code[:9:3] == LOAD_LOAD_AND_IMPORT:
                oparg_1, oparg_2, oparg_3 = struct.unpack('<xHxHxH', code[:9])
                level = consts[oparg_1]
                if level == -1:  # normal import
                    yield "import", (i, consts[oparg_2], names[oparg_3])
                elif level == 0:  # absolute import
                    yield "absolute_import", (
                        i, consts[oparg_2], names[oparg_3])
                else:  # relative import
                    yield "relative_import", (
                        i, level, consts[oparg_2], names[oparg_3])
                code = code[9:]
                i += 9
                continue
            if c >= HAVE_ARGUMENT:
                code = code[3:]
                i += 3
            else:
                code = code[1:]
                i += 1

    def _scan_code(self, co):
        for what, args in self._scanner(co):
            addr = args[0]
            args = args[1:]
            lineno = self._addr_to_lineno(co, addr)
            line = None
            if lineno:
                line = self._source.get(lineno - 1)
            if what == "store":
                name, = args
            elif what in ("import", "absolute_import"):
                fromlist, name = args
                if fromlist is not None:
                    fromlist = [f for f in fromlist if f != "*"]
                if what == "absolute_import":
                    level = 0
                else:
                    level = -1
                self._import_hook(lineno, line, name, fromlist)
            elif what == "relative_import":
                level, fromlist, name = args
                if name:
                    self._import_hook(lineno, line, name, fromlist)
            else:
                # We don't expect anything else from the generator.
                raise RuntimeError(what)

        for c in co.co_consts:
            if isinstance(c, type(co)):
                self._scan_code(c)

    def _import_hook(self, lineno, line, name, fromlist):
        self._imports.append((lineno, line, name, fromlist))

    def _addr_to_lineno(self, co, addr):
        return dict(self._addr_line_map(co)).get(addr)

    def _addr_line_map(self, co):
        def pairwise(iterable):
            a = iter(iterable)
            return itertools.izip(a, a)

        last_line_num = None
        line_num = co.co_firstlineno
        byte_num = 0
        for byte_incr, line_incr in pairwise(map(ord, co.co_lnotab)):
            if byte_incr:
                if line_num != last_line_num:
                    yield (byte_num, line_num)
                    last_line_num = line_num
                byte_num += byte_incr
            line_num += line_incr
        if line_num != last_line_num:
            yield (byte_num, line_num)


class ImportFinder(object):
    """"Finds imports for a package"""
    def __init__(self, package_root):
        self._package_root = package_root
        self._import_data = None

    @property
    def import_data(self):
        if self._import_data is None:
            self._import_data = self._get_imports()
        return self._import_data

    def _get_imports(self):
        imports = {}
        for dirpath, dirnames, filenames in os.walk(self._package_root):
            for filename in filenames:
                if not filename.endswith('.py'):
                    continue
                file_path = os.path.join(dirpath, filename)
                file_imports = ImportScanner(file_path).imports
                for (lineno, line, name, _) in file_imports:
                    top_level_name = name.split('.', 1)[0]
                    imports.setdefault(
                        top_level_name,
                        collections.defaultdict(list)
                    )[file_path].append((lineno, line))

        return imports
