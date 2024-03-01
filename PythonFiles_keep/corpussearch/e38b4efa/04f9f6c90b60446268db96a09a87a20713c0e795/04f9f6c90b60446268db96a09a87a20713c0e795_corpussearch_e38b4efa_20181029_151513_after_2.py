# -*- coding: utf-8 -*-
import pandas as pd
import re
import ipywidgets as widgets
from IPython.display import clear_output, display

from citableclass.base import Citable
from .base import CorpusTextSearch


class SearchWordGUI(widgets.HBox):
    """
    Helper Class, defines single logical element of according, to enable
    more complex search patterns.
    """
    def __init__(self, optionList, colName):
        super(SearchWordGUI, self).__init__()
        self.optList = optionList
        self.column = colName
        if self.column not in self.optList:
            self.optList.extend([colName])

        self._text = widgets.Text(description='Search for:', placeholder='term')
        self._text.layout.margin = '0 0 0 20px'

        self._select = widgets.Dropdown(
            description='Search in:',
            options=self.optList,
            value=self.column,
        )

        children = [self._text, self._select]
        self.children = children

    @property
    def value(self):
        return self._text.value

    @property
    def part(self):
        return self._select.value


class CorpusGUI(CorpusTextSearch):
    """
    GUI wrapper for 'CorpusTextSearch'-class, to be used in Jupyter Notebooks.
    Initialized with path to data. Search can be in main column 'colname' or
    other columns containing data in string format.

    Searches can be chained by using the 'more' button. Logical operations are
    AND, OR, NOT.

    Results are printed in the 'Sentence' field for the 'colname' cells,
    with corresponding metadata from the other columns in the 'Result' field.

    Navigation through results is possible using 'previous' and 'next' buttons.

    Example:
            >>> gui1 = CorpusGUI(
                            pathDF='/path/to/dataframe/file.xlsx',
                            dataType='excel',
                            dataIndex='single',
                            colname='main'
                            )

            >>> gui1.displayGUI()
            True
    """
    def __init__(
            self, pathDF,
            dataType='pickle', dataIndex='multi', colname='text',
            maxValues=2500, pathMeta=False, pathType=False
            ):

        super(CorpusGUI, self).__init__(pathDF, dataType, dataIndex, colname, maxValues, pathMeta, pathType)
        self.initSearch = SearchWordGUI(self.searchFields, self.column)
        self.accordion = widgets.Accordion(children=[self.initSearch])
        self.accordion.set_title(0, 'Enter search term')

        self.extendSearch = widgets.ToggleButtons(options=['more', 'less'])
        self.extendSearch.on_msg(self._addSearchField)

        self.searchButton = widgets.Button(
            description='Search',
            button_style='danger'
        )

        self.searchButton.on_msg(self._searchLogic)

        self.displayResult = pd.DataFrame()

        self.direction = widgets.IntSlider(
            value=0,
            min=0,
            max=self.displayResult.shape[0],
            step=1,
        )

        self.direction.observe(self._setSentence, names='value')

        self._chooseResult()

        self.outInfo = widgets.Output()

        self.dfOut = widgets.Output()

        self.checkDataframe = widgets.Checkbox(
            value=False,
            description='Return Dataframe',
            disabled=False
        )

        self.outSentence = widgets.Textarea(
            value='',
            layout=widgets.Layout(flex='0 1 auto', height='200px', min_height='40px', width='70%'),
            placeholder='Sentence'
        )

        self.outMeta = widgets.Textarea(
            placeholder='Result',
            layout=widgets.Layout(flex='0 1 auto', height='200px', min_height='40px', width='30%'),
            value=''
        )

        self.sentenceFields = widgets.HBox([self.outMeta, self.outSentence])

    def _chooseResult(self):
        # self.direction = widgets.ToggleButtons(options=['previous', 'next'])
        self.direction = widgets.IntSlider(
            value=0,
            min=0,
            max=self.displayResult.shape[0],
            step=1,
            )

        # self.direction.on_msg(self._setSentence)
        self.direction.observe(self._setSentence, names='value')

    def _setDescription(self):
        """ Helper function to display metadata for result"""
        res = 'Result {0}\n'.format(self.counter) + '\n'.join(
             ["{0}: {1}".format(x, y) for x, y in self.displayResult.iloc[self.counter].to_dict().items() if x != self.column]
        )
        return res

    def _setSentence(self, value):
        """ Helper function: Navigate and set result to display"""
        self.counter = value['new']
        if self.counter < self.displayResult.shape[0] and self.counter > -1:
            self.outSentence.value = str(self.displayResult[self.column].iloc[self.counter])
            self.outMeta.value = self._setDescription()
        else:
            self.outSentence.value = 'End of found results. Enter new search.'
        return

    def _addSearchField(self, widget, content, buffers):
        """ Helper function to extend search logic."""
        child = SearchWordGUI(self.searchFields, self.column)
        children = []
        for ch in self.accordion.children:
            children.append(ch)
        if self.extendSearch.value == 'more':
            children.append(
                widgets.Dropdown(
                    description='Select logic to connect words',
                    options={'and': '&', 'or': '|', 'not': '~&'},
                    value='&'
                )
            )
            children.append(child)
            self.accordion.children = children
            self.accordion.set_title(len(children)-2, 'and/or/not')
            self.accordion.set_title(len(children)-1, 'add term')
        elif self.extendSearch.value == 'less':
            if len(children) >= 3:
                lesschildren = children[:-2]
                self.accordion.children = lesschildren
            else:
                pass
            pass
        return

    def _searchLogic(self, widget, content, buffers):
        """
        Helper function to initialize logical reduction
        in CorpusTextSearch.logicReduce()
        """
        self.tempRes = []
        self.tempList = []
        self.counter = 0
        for ch in self.accordion.children:
            if ch.value not in ['&', '|', '~&']:
                self.tempList.append((ch.part, ch.value))
            else:
                self.tempList.append(ch.value)
        self.outputResult = self.logicReduce(self.tempList)

        self.displayResult = self.outputResult.results()

        if self.displayResult.shape[0] > 0:
            # TODO: Add plotting logic in handle_submit(sender)
            # handle_submit(sender)
            maxVal = self.displayResult.copy()
            self.direction.max = maxVal.shape[0]

            self.outSentence.value = re.sub(r'\n|\s+', ' ', str(self.displayResult[self.column].iloc[self.counter]))
            self.outMeta.value = self._setDescription()
            with self.outInfo:
                clear_output()
                print('Found {} entries.'.format(self.displayResult.shape[0]))
        else:
            with self.outInfo:
                clear_output()
                print('Found no entries. Try changing search!')
        with self.dfOut:
            clear_output()
            if self.checkDataframe.value is True:
                print('Resulting dataframe is accesible by using ".result".')
                display(self.result)
            else:
                display(self.sentenceFields)

    def displayGUI(self):
        """Display the GUI for CorpusTextSearch"""
        searchControl = widgets.HBox([self.extendSearch, self.searchButton, self.outInfo, self.checkDataframe])
        textControl = self.direction
        searchBox = widgets.VBox([self.accordion, searchControl, textControl, self.dfOut])
        return display(searchBox)
