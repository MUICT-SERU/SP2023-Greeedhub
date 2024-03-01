import pytest
import re
from pathlib import Path
from _pytest.python import Module, Instance, Function, Class


class Section:
    """
    plugin custom section
    [informative_node_od]
    enable:[true/false]
    delimiter:[str,default @]
    """

    def __init__(self, config):
        try:
            self._sections = config.inicfg.config.sections.get('informative_node_id', dict())
        except AttributeError:
            self._sections = dict()

    @property
    def enable(self):
        return self._sections.get('enable', 'false').lower() == 'true'

    @property
    def delimiter(self):
        return self._sections.get('delimiter', '@').strip() or '@'


def determiner(docstring, delimiter):
    if docstring:
        lines = [line.strip() for line in docstring.splitlines() if line.strip() != '']
        regex = f'''\\s*{re.escape(delimiter)}\\s*(.*)'''
        group = re.search(regex, lines[0])
        if group:
            return group.group(1)


def search(docstring, delimiter):
    regex = f'''(^\\"{{3}}\\s*\\s*|^\\'{{3}})\\s*{re.escape(delimiter)}\\s*(.*)(\\"{{3}}$|\\'{{3}}$)'''
    docstring = re.search(regex, docstring)
    if docstring:
        return docstring.group(2)
    return None


def validator(node_id: str):
    node_id = node_id.strip()
    for char in '[]()/ \\':
        node_id = node_id.replace(char, '_')
    return node_id.replace('::', '_')


def get_params(node_name: str):
    groups = re.search(r'(.+)\[(.+)\]', node_name)
    try:
        return groups.groups()
    except AttributeError:
        return None, None


def encoder(escaped: str):
    return escaped.encode().decode('unicode-escape')


class InformativeNode:
    def __init__(self, config):
        self.config = Section(config)

    def pytest_itemcollected(self, item):
        parts = []

        def package_traverse(test_item):
            nonlocal parts
            parents = Path(test_item.fspath).parents
            for i in parents:
                if i == Path.cwd():
                    break
                files = list(i.glob('__init__.py'))
                if files:
                    for init_file in files:
                        with open(init_file) as fp:
                            line = fp.readline()
                            docstring = search(line, self.config.delimiter)
                            if docstring:
                                parts.append((docstring, True))
                            else:
                                parts.append((i.name, True))

                else:
                    parts.append((i.name, True))

        def traverse(test_item):
            nonlocal parts
            if test_item:
                t = type(test_item)

                if t in (Function, Class):
                    parts.append((
                        determiner(test_item.obj.__doc__, self.config.delimiter) or test_item.name,
                        False
                    ))
                    traverse(test_item.parent)

                elif t is Instance:
                    traverse(test_item.parent)

                elif t is Module:
                    parts.append((
                        determiner(test_item.obj.__doc__, self.config.delimiter) or test_item.fspath.purebasename,
                        True
                    ))
                    package_traverse(test_item)

        traverse(item)
        file_parts = '/'.join(reversed([validator(name) for name, is_file in parts if is_file]))
        object_parts = '::'.join(reversed([validator(name) for name, is_file in parts if not is_file]))
        node_id = '::'.join([file_parts, object_parts])

        _, params = get_params(item.name)
        if params:
            node_id = f"{node_id}[{validator(encoder(params))}]"
        item._nodeid = node_id


def pytest_configure(config):
    plugin = InformativeNode(config)
    if plugin.config.enable:
        config.pluginmanager.register(plugin, 'InformativeNode')
