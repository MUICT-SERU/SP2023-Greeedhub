import re
from typing import Union, IO, List


class MultiIniParser:
    """
    Ini-File configuration parser that is able to read config files containing multiple sections and options with the
    same name. This class takes the ideas and some code of :class configparser.ConfigParser: from the Python Standard-library and
    extends those to its cause. Additionally it strives for an easier readablity as the original.

    Example INI-File::
        option1: first option
        [section]
        option2: second option
        option2: second second option
        [section]
        option3: third option
        option3: second third option

    can be accessed with::
        parser = MultiIniParser()
        parser.read(ini_file)
        option1 = parser[None][0]["option1"][0]
        option2_1 = parser["section"][0]["option2"[0]
        option2_2 = parser["section"][0]["option2"[1]
        option3_1 = parser["section"][1]["option3"[0]
        option3_2 = parser["section"][1]["option3"[1]
    """

    _SECTION_TEMPLATE = r"""
            \[                                  # [
            (?P<header>[^]]+)                   # very permissive!
            \]                                  # ]
                                                # source: Python configparser module
            """
    _OPTION_TEMPLATE = r"""
                (?P<option>.*?)                     # very permissive!
                \s*(?:                              # any number of space/tab,
                (?P<vi>{delim})\s*                  # optionally followed by
                                                    # any of the allowed
                                                    # delimiters, followed by any
                                                    # space/tab
                                                    # source: Python configparser module
                (?P<value>.*))?$
                """
    SECTCRE = re.compile(_SECTION_TEMPLATE, re.VERBOSE)

    def __init__(self, delimiters=(':', '=')):
        self._top_section: Section = Section()
        self.sections: List[Section] = []
        escaped_delimiters = [re.escape(d) for d in delimiters] # idea taken from Python configparser module
        prepared_delimiters = "|".join(escaped_delimiters) # idea taken from Python configparser module
        option_template_with_delimiters = MultiIniParser._OPTION_TEMPLATE.format(delim=prepared_delimiters) # idea taken from Python configparser module
        self.option_regex = re.compile(option_template_with_delimiters, re.VERBOSE) # idea taken from Python configparser module

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
        elif isinstance(to_parse, list):
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

class Option:
    """
    Represents an Option of an INI-File
    """

    def __init__(self, key: str, value: str=None, section=None):
        self.key: str = key
        self.value: str = value
        self.section = section


class Section:
    """
    Represents a Section containing Options of an INI-File
    """

    def __init__(self, name: str=None):
        self.name: str = name
        self.options: List[Option] = []

    def get(self, option_name: str) -> List[Option]:
        return [option for option in self.options if option_name == option.key]

    def __getitem__(self, key: str):
        options = self.get(key)
        if len(options) == 0:
            raise KeyError(key)
        return [option.value for option in options]