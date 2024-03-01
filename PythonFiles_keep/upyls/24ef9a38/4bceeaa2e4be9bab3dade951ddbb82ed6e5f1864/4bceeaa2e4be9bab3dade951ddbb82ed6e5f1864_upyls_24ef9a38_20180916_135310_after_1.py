import re
from typing import Union, IO, List


class Option:

    def __init__(self, key: str, value: str=None, section=None):
        self.key: str = key
        self.value: str = value
        self.section = section


class Section:

    def __init__(self, name: str=None):
        self.name: str = name
        self.options: List[Option] = []

    def get(self, option_name: str) -> List[Option]:
        return [option for option in self.options if option_name == option.key]

    def __getitem__(self, key: str):
        options = self.get(key)
        if len(options) == 0:
            raise KeyError(key)
        return options


class MultiIniParser:
    """
    Ini-File configuration parser that is able to read config files containing multiple sections and options with the
    same name
    """

    _SECT_TMPL = r"""
            \[                                  # [
            (?P<header>[^]]+)                   # very permissive!
            \]                                  # ]
            """
    _OPT_TMPL = r"""
            (?P<option>.*?)                     # very permissive!
            \s*(?:                              # any number of space/tab,
            (?P<vi>{delim})\s*                  # optionally followed by
                                                # any of the allowed
                                                # delimiters, followed by any
                                                # space/tab
            (?P<value>.*))?$
            """
    SECTCRE = re.compile(_SECT_TMPL, re.VERBOSE)

    def __init__(self, delimiters=(':', '=')):
        self._top_section: Section = Section()
        self.sections: List[Section] = []
        self.option_delimiter = ":"
        self.option_regex = re.compile(MultiIniParser._OPT_TMPL.format(delim=delimiters))

    def get(self, section_name: Union[str, None], option_name: str) -> List[Option]:
        if section_name is None:
            section = self._top_section
            return section.get(option_name)
        else:
            found_options: List[Option] = list()
            sections_by_name = self.get_sections_by_name(section_name)
            for section in sections_by_name:
                    found_options.extend(section.get(option_name))
            return found_options

    def get_sections_by_name(self, section_name) -> List[Section]:
        return [section for section in self.sections if section_name == section.name]

    def read(self, to_parse: Union[str, IO, List[str]]):
        lines: List[str] = []
        if isinstance(to_parse, IO):
            lines = to_parse.readlines()
        elif isinstance(to_parse, str):
            lines = to_parse.splitlines()
        elif isinstance(to_parse, List[str]):
            lines = to_parse
        else:
            raise ValueError("to_parse must either be a str, a file or a list of strings")
        actual_section: Section = self._top_section
        for line in lines:
            line_without_comments = line.split("#", 1)[0]
            empty_line_regex = re.compile("^\s*$")
            if re.match(empty_line_regex, line):
                continue
            section_match = re.match(MultiIniParser.SECTCRE, line_without_comments)
            if section_match:
                section_name = section_match.group("header")
                section = Section(name=section_name)
                self.sections.append(section)
                actual_section = section
            option_match = re.match(self.option_regex, line_without_comments)
            if option_match:
                option = option_match.group("option")
                value = option_match.group("value")
                actual_section.options.append(Option(key=option, value=value,
                                                     section=actual_section))
    def __getitem__(self, key: Union[str, None]) -> List[Section]:
        if key is None:
            return [self._top_section]
        sections = self.get_sections_by_name(key)
        if len(sections) == 0:
            raise KeyError(key)
        return sections