# -*- coding: utf-8 -*-
"""
Copyright (c) 2015 Red Hat, Inc
All rights reserved.

This software may be modified and distributed under the terms
of the BSD license. See the LICENSE file for details.
"""

from __future__ import unicode_literals

import json
import pytest

from dockerfile_parse import DockerfileParser
from tests.fixtures import dfparser, instruction

NON_ASCII = "žluťoučký"


class TestDockerfileParser(object):

    def test_dockerfileparser(self, dfparser):
        df_content = """\
FROM fedora
CMD {0}""".format(NON_ASCII)
        df_lines = ["FROM fedora\n", "CMD {0}".format(NON_ASCII)]

        dfparser.content = ""
        dfparser.content = df_content
        assert dfparser.content == df_content
        assert dfparser.lines == df_lines

        dfparser.content = ""
        dfparser.lines = df_lines
        assert dfparser.content == df_content
        assert dfparser.lines == df_lines

    def test_constructor_cache(self, tmpdir):
        tmpdir_path = str(tmpdir.realpath())
        df1 = DockerfileParser(tmpdir_path)
        df1.lines = ["From fedora:latest\n", "LABEL a b\n"]

        df2 = DockerfileParser(tmpdir_path, True)
        assert df2.cached_content

    def test_dockerfile_structure(self, dfparser):
        dfparser.lines = ["# comment\n",        # should be ignored
                          " From  \\\n",        # mixed-case
                          "   base\n",          # extra ws, continuation line
                          " # comment\n",
                          " label  foo  \\\n",  # extra ws
                          "    bar  \n",        # extra ws, continuation line
                          "USER  {0}".format(NON_ASCII)]   # extra ws, no newline

        assert dfparser.structure == [{'instruction': 'FROM',
                                       'startline': 1,  # 0-based
                                       'endline': 2,
                                       'content': ' From  \\\n   base\n',
                                       'value': 'base'},
                                      {'instruction': 'LABEL',
                                       'startline': 4,
                                       'endline': 5,
                                       'content': ' label  foo  \\\n    bar  \n',
                                       'value': 'foo      bar'},
                                      {'instruction': 'USER',
                                       'startline': 6,
                                       'endline': 6,
                                       'content': 'USER  {0}'.format(NON_ASCII),
                                       'value': '{0}'.format(NON_ASCII)}]

    def test_dockerfile_json(self, dfparser):
        dfparser.content = """\
# comment
From  base
LABEL foo="bar baz"
USER  {0}""".format(NON_ASCII)
        expected = json.dumps([{"FROM": "base"},
                               {"LABEL": "foo=\"bar baz\""},
                               {"USER": "{0}".format(NON_ASCII)}])
        assert dfparser.json == expected

    def test_get_baseimg_from_df(self, dfparser):
        dfparser.lines = ["From fedora:latest\n",
                          "LABEL a b\n"]
        base_img = dfparser.baseimage
        assert base_img.startswith('fedora')

    def test_get_instructions_from_df(self, dfparser, instruction):
        dfparser.content = ""
        lines = []
        i = instruction
        lines.insert(-1, '{0} "name1"=\'value 1\' "name2"=myself name3="" name4\n'.format(i))
        lines.insert(-1, '{0} name5=5\n'.format(i))
        lines.insert(-1, '{0} "name6"=6\n'.format(i))
        lines.insert(-1, '{0} name7\n'.format(i))
        lines.insert(-1, '{0} "name8"\n'.format(i))
        lines.insert(-1, '{0} "name9"="asd \\  \\n qwe"\n'.format(i))
        lines.insert(-1, '{0} "name10"="{1}"\n'.format(i, NON_ASCII))
        lines.insert(-1, '{0} "name1 1"=1\n'.format(i))
        lines.insert(-1, '{0} "name12"=12 \ \n   "name13"=13\n'.format(i))
        lines.insert(-1, '{0} name14=1\ 4\n'.format(i))
        # old syntax (without =)
        lines.insert(-1, '{0} name101 101\n'.format(i))
        lines.insert(-1, '{0} name102 1 02\n'.format(i))
        lines.insert(-1, '{0} "name103" 1 03\n'.format(i))
        lines.insert(-1, '{0} name104 "1"  04\n'.format(i))
        lines.insert(-1, '{0} name105 1 \'05\'\n'.format(i))
        lines.insert(-1, '{0} name106 1 \'0\'   6\n'.format(i))
        lines.insert(-1, '{0} name107 1 0\ 7\n'.format(i))
        dfparser.lines = lines
        if instruction == 'LABEL':
            instructions = dfparser.labels
        elif instruction == 'ENV':
            instructions = dfparser.envs
        assert len(instructions) == 21
        assert instructions.get('name1') == 'value 1'
        assert instructions.get('name2') == 'myself'
        assert instructions.get('name3') == ''
        assert instructions.get('name4') == ''
        assert instructions.get('name5') == '5'
        assert instructions.get('name6') == '6'
        assert instructions.get('name7') == ''
        assert instructions.get('name8') == ''
        assert instructions.get('name9') == 'asd \\  \\n qwe'
        assert instructions.get('name10') == '{0}'.format(NON_ASCII)
        assert instructions.get('name1 1') == '1'
        assert instructions.get('name12') == '12'
        assert instructions.get('name13') == '13'
        assert instructions.get('name14') == '1 4'
        assert instructions.get('name101') == '101'
        assert instructions.get('name102') == '1 02'
        assert instructions.get('name103') == '1 03'
        assert instructions.get('name104') == '1  04'
        assert instructions.get('name105') == '1 05'
        assert instructions.get('name106') == '1 0   6'
        assert instructions.get('name107') == '1 0 7'

    def test_modify_instruction(self, dfparser):
        FROM = ('ubuntu', 'fedora:latest')
        CMD = ('old cmd', 'new command')
        df_content = """\
FROM {0}
CMD {1}""".format(FROM[0], CMD[0])

        dfparser.content = df_content

        assert dfparser.baseimage == FROM[0]
        dfparser.baseimage = FROM[1]
        assert dfparser.baseimage == FROM[1]

        assert dfparser.cmd == CMD[0]
        dfparser.cmd = CMD[1]
        assert dfparser.cmd == CMD[1]

    def test_add_del_instruction(self, dfparser):
        df_content = """\
CMD xyz
LABEL a=b c=d
LABEL x=\"y z\"
ENV h i
ENV j='k' l=m
"""
        dfparser.content = df_content

        dfparser._add_instruction('FROM', 'fedora')
        assert dfparser.baseimage == 'fedora'
        dfparser._delete_instructions('FROM')
        assert dfparser.baseimage is None

        dfparser._add_instruction('FROM', 'fedora')
        assert dfparser.baseimage == 'fedora'
        dfparser._delete_instructions('FROM', 'fedora')
        assert dfparser.baseimage is None

        dfparser._add_instruction('LABEL', ('Name', 'self'))
        assert len(dfparser.labels) == 4
        assert dfparser.labels.get('Name') == 'self'
        dfparser._delete_instructions('LABEL')
        assert dfparser.labels == {}

        dfparser._add_instruction('ENV', ('Name', 'self'))
        assert len(dfparser.envs) == 4
        assert dfparser.envs.get('Name') == 'self'
        dfparser._delete_instructions('ENV')
        assert dfparser.envs == {}

        assert dfparser.cmd == 'xyz'

    @pytest.mark.parametrize(('existing',
                              'delete_key',
                              'expected',
    ), [
        # Delete non-existing key
        (['a b\n',
          'x="y z"\n'],
         'name',
         KeyError()),

        # Simple remove
        (['a b\n',
          'x="y z"\n'],
         'a',
         ['x="y z"\n']),

        # Simple remove
        (['a b\n',
          'x="y z"\n'],
         'x',
         ['a b\n']),

        #  Remove first of two instructions on the same line
        (['a b\n',
          'x="y z"\n',
          '"first"="first" "second"="second"\n'],
         'first',
         ['a b\n',
          'x="y z"\n',
          'second=second\n']),

        #  Remove second of two instructions on the same line
        (['a b\n',
          'x="y z"\n',
          '"first"="first" "second"="second"\n'],
         'second',
         ['a b\n',
          'x="y z"\n',
          'first=first\n']),
    ])
    def test_delete_instruction(self, dfparser, instruction, existing, delete_key, expected):
        existing = [instruction + ' ' + i for i in existing]
        if isinstance(expected, list):
            expected = [instruction + ' ' + i for i in expected]
        dfparser.lines = ["FROM xyz\n"] + existing

        if isinstance(expected, KeyError):
            with pytest.raises(KeyError):
                dfparser._delete_instructions(instruction, delete_key)
        else:
            dfparser._delete_instructions(instruction, delete_key)
            assert set(dfparser.lines[1:]) == set(expected)

    @pytest.mark.parametrize(('existing',
                              'new',
                              'expected',
    ), [
        # Simple test: set an instruction
        (['a b\n',
          'x="y z"\n'],
         {'Name': 'New shiny project'},
         ['Name=\'New shiny project\'\n']),

        # Set two instructions
        (['a b\n',
          'x="y z"\n'],
         {'something': 'nothing', 'mine': 'yours'},
         ['something=nothing\n', 'mine=yours\n']),

        # Set instructions to what they already were: should be no difference
        (['a b\n',
          'x="y z"\n',
          '"first"="first" second=\'second value\'\n'],
         {'a': 'b', 'x': 'y z', 'first': 'first', 'second': 'second value'},
         ['a b\n',
          'x="y z"\n',
          '"first"="first" second=\'second value\'\n']),

        # Adjust one label of a multi-value LABEL/ENV statement
        (['a b\n',
          'first=\'first value\' "second"=second\n',
          'x="y z"\n'],
         {'first': 'changed', 'second': 'second'},
         ['first=changed second=second\n']),

        # Delete one label of a multi-value LABEL/ENV statement
        (['a b\n',
          'x="y z"\n',
          'first=first second=second\n'],
         {'second': 'second'},
         ['second=second\n']),

        # Nested quotes
        (['"ownership"="Alice\'s label" other=value\n'],
         {'ownership': "Alice's label"},
         # quote() will always use single quotes when it can
         ["ownership='Alice\'\"\'\"\'s label'\n"]),

        # Modify a single value that needs quoting
        (['foo bar\n'],
         {'foo': 'extra bar'},
         ["foo 'extra bar'\n"]),
    ])
    def test_setter(self, dfparser, instruction, existing, new, expected):
        existing = [instruction + ' ' + i for i in existing]
        if isinstance(expected, list):
            expected = [instruction + ' ' + i for i in expected]
        dfparser.lines = ["FROM xyz\n"] + existing

        if instruction == 'LABEL':
            dfparser.labels = new
            assert dfparser.labels == new
        elif instruction == 'ENV':
            dfparser.envs = new
            assert dfparser.envs == new
        assert set(dfparser.lines[1:]) == set(expected)

    @pytest.mark.parametrize(('old_instructions', 'key', 'new_value', 'expected'), [
        # Simple case, no '=' or quotes
        ('Release 1', 'Release', '2', 'Release 2'),
        # No '=' but quotes
        ('"Release" "2"', 'Release', '3', 'Release 3'),
        # Simple case, '=' but no quotes
        ('Release=1', 'Release', '6', 'Release=6'),
        # '=' and quotes
        ('"Name"=\'alpha alpha\' Version=1', 'Name', 'beta delta', 'Name=\'beta delta\' Version=1'),
        # '=', multiple labels, no quotes
        ('Name=foo Release=3', 'Release', '4', 'Name=foo Release=4'),
        # '=', multiple labels and quotes
        ('Name=\'foo bar\' "Release"="4"', 'Release', '5', 'Name=\'foo bar\' Release=5'),
        # Release that's not entirely numeric
        ('Version=1.1', 'Version', '2.1', 'Version=2.1'),
    ])
    def test_setter_direct(self, dfparser, instruction, old_instructions, key, new_value, expected):
        df_content = """\
FROM xyz
LABEL a b
LABEL x=\"y z\"
ENV c d
ENV e=\"f g\"
{0} {1}
""".format(instruction, old_instructions)

        dfparser.content = df_content
        if instruction == 'LABEL':
            dfparser.labels[key] = new_value
            assert dfparser.labels[key] == new_value
            assert dfparser.lines[-1] == '{0} {1}\n'.format(instruction, expected)
            del dfparser.labels[key]
            assert not dfparser.labels.get(key)
        elif instruction == 'ENV':
            dfparser.envs[key] = new_value
            assert dfparser.envs[key] == new_value
            assert dfparser.lines[-1] == '{0} {1}\n'.format(instruction, expected)
            del dfparser.envs[key]
            assert not dfparser.labels.get(key)
