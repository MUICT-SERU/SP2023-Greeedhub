# -*- coding: utf-8 -*-
import pandas as pd
import re
import ipywidgets as widgets


from citableclass.base import Citable
# from .base import CorpusTextSearch
from corpussearch.base import CorpusTextSearch


class SearchWordGUI(widgets.HBox):
    def __init__(self):
        super(SearchWordGUI, self).__init__()

        #############
        # Functions #
        #############
        def chgTxt(change):
            self._text.value = change['new']

        def generateOptions(val):
            ret = []
            for x in set(dfSentences[val].values):
                if type(x) == str:
                    res = x.split(',')
                    ret.append(res)
            retTemp = set([x for y in ret for x in y])
            if retTemp:
                pass
            else:
                retTemp = ['No choice possible']
            retVal = [x.strip(' )(') for x in retTemp if ':' not in x]
            return retVal

        ###########
        # Widgets #
        ###########
        self._text = widgets.Text(description='Search for:', placeholder='Enter search word')
        self._text.layout.margin = '0 0 0 20px'
        optList = ['']
        # for part in ['cause','effect','context']:
        #    optList.extend(generateOptions(part))

        self._select = widgets.Dropdown(
            description='Values:',
            options=sorted(list(set(optList))),
            value='',
        )
        ###########
        # Actions #
        ###########
        self._select.observe(
            chgTxt,
            names='value'
        )

        children = [self._text]
        self.children = children

    @property
    def value(self):
        return self._text.value

    @property
    def part(self):
        return 'sentence'


class CorpusGUI(object):

    def __init__(self):
        self.initSearch = SearchWordGUI()
        self.accordion = widgets.Accordion(children=[initSearch])
        self.accordion.set_title(0, 'Enter search term')

    def _addSearchField(self, widget, content, buffers):
        child = SearchWordGUI()
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

    def extend(self):
        self.extendSearch = widgets.ToggleButtons(
            options=['more', 'less'],
        )

        self.extendSearch.on_msg(self._addSearchField)
        return

    def search(self):
        self.searchButton = widgets.Button(
            description='Search', button_style='danger'
        )

        self.searchButton.on_click(
            print('Test')
        )
        return

    def displayGUI(self):
        self.extend()
        self.search()
        moreSearch = widgets.HBox([self.extendSearch, self.searchButton])
        searchBox = widgets.VBox([self.accordion, moreSearch])

        return display(searchBox)
