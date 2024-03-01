import re
from typing import Union, IO, List, Iterable


class Option:
    """
    Represents an Option of an INI-File
    """

    def __init__(self, key: str, value: str=None, section=None):
        """
        create an :Option:
        :param key: the :Option:'s key
        :param value: the :Option:'s value
        :param section: the :Section: the :Option: will be assiciated with
        """
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

    def get(self, option_name: str) -> Iterable[Option]:
        return [option for option in self.options if option_name == option.key]

    def __getitem__(self, key: str):
        options = self.get(key)
        if len(options) == 0:
            raise KeyError(key)
        return [option.value for option in options]


class MultiIniParser:
    """
    Ini-File configuration parser that is able to read config files containing multiple sections and options with the
    same name. This class takes the ideas and some code of :configparser.ConfigParser: from the Python Standard-library and
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
        option1 = parser[None]["option1"][0]
        option2_1 = parser["section"][0]["option2"[0]
        option2_2 = parser["section"][0]["option2"[1]
        option3_1 = parser["section"][1]["option3"[0]
        option3_2 = parser["section"][1]["option3"[1]
    or with::
        parser = MultiIniParser()
        parser.read(ini_file)
        top_level_section = parser.get_sections_by_name(None)
        option1 = top_level_section.get("option1")
        option1_value = option1.value
        sections = parser.get_sections_by_name("section")
        option2 = sections[0].get("option2")
        option21_value = option2[0].value
        option22_value = option2[1].value
        option3 = sections[1].get("option2")
        option31_value = option3[0].value
        option32_value = option3[1].value
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
    _SECTION_COMPILED_REGEX = re.compile(_SECTION_TEMPLATE, re.VERBOSE)

    def __init__(self, option_delimiters=(':', '=')):
        """
        create a :MultiIniParser:
        :param option_delimiters: define the characters which delimit option name and option value,
        defaults are ':' and '='
        """
        self._top_section: Section = Section()
        self.sections: List[Section] = []
        escaped_delimiters = [re.escape(d) for d in option_delimiters] # idea taken from Python configparser module
        prepared_delimiters = "|".join(escaped_delimiters) # idea taken from Python configparser module
        option_template_with_delimiters = MultiIniParser._OPTION_TEMPLATE.format(delim=prepared_delimiters) # idea taken from Python configparser module
        self.option_regex = re.compile(option_template_with_delimiters, re.VERBOSE) # idea taken from Python configparser module

    def read(self, to_parse: Union[str, IO, Iterable[str]]):
        """
        read the ini-file from either a :str:, a file or a collection of :str: lines and parse them into items of
        :Section:s and :Option:s
        :param to_parse: a single string containing the whole INI-File, a file on a filesystem or a collection of :str:
        lines which contain the INI-File.
        """
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

            section_match = re.match(MultiIniParser._SECTION_COMPILED_REGEX, line_without_comments)
            if section_match:
                section_name = section_match.group("header")
                section = Section(name=section_name)
                self.sections.append(section)
                actual_section = section
                continue

            option_match = re.match(self.option_regex, line_without_comments)
            if option_match:
                option = option_match.group("option")
                value = option_match.group("value")
                actual_section.options.append(Option(key=option, value=value,
                                                     section=actual_section))

    def get_sections_by_name(self, section_name) -> Union[Section, Iterable[Section], None]:
        """
        retrieve a collection of :Section:, which bear the passed name
        :param section_name: the name of the sections to be retrieved, if :None: is passed the top level section without
        a name is returned
        :return: the top level :Section: without a name when :None: is passed as Section's name or
        a collection of :Section:s bearing the passed name or :None: if no section can be found with that name
        """
        if section_name is None:
            return self._top_section
        sections = [section for section in self.sections if section_name == section.name]
        return sections if len(sections) != 0 else None

    def get(self, section_name: Union[str, None], option_name: str) -> Iterable[Option]:
        """
        get all options for passed section and option names
        :param section_name: the :Section:'s name the :Option:s are associated with, can be :None: if you want the
        :Options: in the top level section without a name
        :param option_name: the :Option:s' name
        :return: a collection of the requested :Option:s
        """
        if section_name is None:
            section = self._top_section
            return section.get(option_name)
        else:
            found_options: List[Option] = list()
            sections_by_name = self.get_sections_by_name(section_name)
            for section in sections_by_name:
                    found_options.extend(section.get(option_name))
            return found_options

    def get_options_by_name(self, option_name: str) -> Union[Iterable[Option], None]:
        """
        get all :Option:s from all section in INI-File which bear the passed name
        :param option_name: the :Option:s' name
        :return: a collection of :Option:s or None if no :Option: with that name can be found
        """
        options: Option = list()
        for section in self.sections:
            options.extend([option for option in section.options if option.key == option_name])
        return options if len(options) != 0 else None

    def __getitem__(self, key: Union[str, None]) -> Union[Section, Iterable[Section]]:
        """
        get the :Section:s of an INI-File with a given key but with Python's square bracket notation::
        sections = parser["section"]
        :param key: the :Section:s' name, can be :None: if you want the top level :Section: without a name
        :return: either the top level section if None is passed, or a collection of :Section:s with the respective name
        :raise KeyError: if there are no sections with that name
        """
        if key is None:
            return self._top_section
        sections: Iterable = self.get_sections_by_name(key)
        if len(sections) == 0:
            raise KeyError(key)
        return sections