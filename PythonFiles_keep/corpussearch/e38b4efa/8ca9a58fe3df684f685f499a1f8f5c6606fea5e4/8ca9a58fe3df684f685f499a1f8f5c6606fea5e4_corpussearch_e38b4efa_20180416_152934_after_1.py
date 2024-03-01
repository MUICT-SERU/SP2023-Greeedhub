# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import math
import re
from ast import literal_eval
from collections import Counter, OrderedDict
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import ipywidgets as widgets
from IPython.display import clear_output

from .gui import CorpusGUI


class CorpusVisualization(object):
    """
    Visualization layer for corpus search.
    """

    def __init__(self, dataframe, label):
        self.plotDict = {}
        self.resultDF = dataframe
        self.label = label
        plt.style.use('seaborn-deep')

        self.plot = widgets.Button(
            description='Plot on'
            )
        self.plot.on_msg(
            self._plotFunction
            )
        self.resetPlot = widgets.Button(
            description='Reset plot'
            )
        self.options = self.resultDF.columns.values.tolist()
        self.options.append('Lambda Function')
        self.plotLevel = widgets.Dropdown(
            options=self.options
            )
        self.plotLevel.observe(
            self._addFreeForm
        )

        self.resetPlot.on_msg(
            self._resetPlotFunc
        )
        self.addColumnField = widgets.Text(
            placeholder='tuple of column and callable function, e.g., ("number", "row > 10")'
            )
        self.plotout = widgets.Output()
        self.plotLevelOut = widgets.Output()

    def _addFreeForm(self, change):
        """Display free form text field"""
        if change['type'] == 'change' and change['name'] == 'value':
            if change['new'] == 'Lambda Function':
                with self.plotLevelOut:
                    clear_output()
                    display(self.addColumnField)

    def _resetPlotFunc(self, widget, content, buffers):
        """Clear all previous plots."""
        self.plotDict.clear()
        level = self.plotLevel.value
        with self.plotout:
            clear_output()
        with self.plotLevelOut:
            clear_output()
            display(self.plotLevel)

    def _initFigure(self):
        """Basic initalization for matplotlib figure."""
        clear_output()
        xticks = []
        try:
            xticks = self.resultDF[self.plotLevel.value].unique()
        except ValueError:
            print('Can not use {0} for plotting'.format(level))

        xtickslabels = sorted(xticks, key=lambda x: x[0])

        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
        ax.set_xticks(
            np.linspace(
                1,  len(xtickslabels) + 1, len(xtickslabels), endpoint=False
                )
            )
        ax.set_xticklabels(xtickslabels, rotation=45)
        ax.set_yticks(np.linspace(0, 1, 5))
        ax.set_yticklabels(['0', '', '0.5', '', '1'])

    def _plotFunction(self, widget, content, buffers):
        resDict = {}
        if self.plotLevel.value == 'Lambda Function':
            level = 'lambda_func'
            try:
                param = literal_eval(self.addColumnField.value)
                series = self.resultDF[param[0]].apply(lambda row: eval(param[1]))
                self.resultDF = self.resultDF.assign(lambda_func=series)
            except:
                print('failed assiging new column')
                self.resultDF = self.resultDF.assign(lambda_func=None)
        else:
            level = self.plotLevel.value
        with self.plotout:
            if math.isclose(len(self.resultDF[level].apply(lambda row: str(row)).unique())/self.resultDF.shape[0], 1, rel_tol=0.2):
                clear_output()
                print('Difference between number of unique values and dataframe dimension to small.')
            else:
                clear_output()
                iterate = [x for x in self.resultDF[level]]
                resDict = OrderedDict(Counter(str(elem) for elem in iterate))
                xticks = []
                try:
                    xticks = self.resultDF[level].apply(lambda row: str(row)).unique().tolist()
                    xticks[:] = (elem[:15] for elem in xticks)
                except:
                    print('Can not use {0} for plotting'.format(level))
                xtickslabels = sorted(xticks)  # , key=lambda x: x[0])
                fig = plt.figure(figsize=(8, 8))
                ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
                ax.set_xticks(np.linspace(1,  len(xtickslabels) + 1, len(xtickslabels), endpoint=False))
                ax.set_xticklabels(xtickslabels, rotation=45)
                yMax = int(max(resDict.values()))
                if yMax > 10:
                    interval = int(yMax/10)
                else:
                    interval = 1
                ax.set_yticks(np.arange(0, yMax+1, interval))
                x = [x for x in range(1, len(resDict.keys())+1)]
                y = [y for y in resDict.values()]
                ax.bar(x, y, width=0.3, alpha=0.3, label=self.label)
                ax.legend()
                plt.show()

    def displayGUI(self):
        """Display the buttons for visual control and display"""
        visualControl = widgets.HBox([self.plot, self.plotLevelOut, self.resetPlot])
        searchBox = widgets.VBox([visualControl, self.plotout])
        display(searchBox)
        with self.plotLevelOut:
            display(self.plotLevel)


class VisualizeDistribution(object):

    def __init__(self, dataframe, column, glossarDict):

        self.dataframe = dataframe
        self.column = column
        self.glossar = glossarDict

        self.plotOut = widgets.Output()

        self.plotGroupOut = widgets.Output()

        self._generateCount()

        self.choose = widgets.Dropdown(
            description='Choose item:',
            options=self.glossarCount.keys()
        )

        self.choose.observe(
            self._plotWordDistribution,
            names='value'
        )

        self.optList = list(self.glossar.keys())
        self.optList.insert(0, 'all')

        self.select = widgets.SelectMultiple(
            options=self.optList,
            value=['all'],
            description='Select cat.',
            disabled=False
        )

        self.groupOptlist = self.dataframe.columns.values.tolist()
        self.groupOptlist.append('Lambda function')

        self.addColumnField = widgets.Text(
            placeholder='tuple of column and callable function, e.g., ("number", "row > 10")'
            )

        self.groupSelect = widgets.Dropdown(
            options=self.groupOptlist,
            description='Group by'
        )

        self.groupSelect.observe(
            self._addFreeForm,

        )

        self.plot = widgets.Button(
            description='Plot'
            )

        self.plot.on_click(
            self._plotGlossarDistribution
        )

    def _addFreeForm(self, change):
        """Display free form text field"""
        if change['type'] == 'change' and change['name'] == 'value':
            if change['new'] == 'Lambda Function':
                with self.plotGroupOut:
                    clear_output()
                    display(self.addColumnField)

    def _natural_sort_key(self, s, _nsre=re.compile('([0-9]+)')):
        return [int(text) if text.isdigit() else text.lower()
                for text in re.split(_nsre, s)]

    def _queryWordOccurance(self, word, text):
        if word in text:
            return 1
        else:
            return 0

    def _generateCount(self):
        self.glossarCount = {}
        for key in self.glossar:
            res = []
            for word in self.glossar[key]:
                num = self.dataframe[self.column].apply(
                    lambda row: self._queryWordOccurance(word, row)
                    ).sum()
                res.append((word, num))
            self.glossarCount[key] = res

    def _generateDistrCount(self, key, text, method='cumul'):
        count = 0
        for word in self.glossar[key]:
            if method == 'cumul':
                res = re.findall(word, text)
                if res:
                    count += len(res)
            elif method == 'single':
                if word in text:
                    count += 1
        return count

    def _preparePlotDF(self, groupColumn):
        self.plotDF = self.dataframe.copy()
        for key in self.glossar.keys():
            self.plotDF[key] = self.dataframe[self.column].apply(
                lambda row: self._generateDistrCount(key, row)
                )

        sorted_index = sorted(list(self.plotDF.groupby(groupColumn).sum().index),
                              key=lambda x: self._natural_sort_key(x)
                              )

        self.sortedPlotDF = self.plotDF.groupby(groupColumn).sum().reindex(index=sorted_index).reset_index()

    def _plotWordDistribution(self, change):
        key = change['new']
        if not self.glossarCount:
            self._generateCount()
        df = pd.DataFrame(self.glossarCount[key], columns=['word', 'count'])
        with self.plotOut:
            clear_output()
            ax = df.plot.bar(
                x='word',
                y='count',
                figsize=(8, 5),
                title=key,
                legend=True,
                rot=45)
            ax.set_xlabel('Word', fontsize=12)
            ax.set_ylabel("Count", fontsize=12)
            ax.legend(loc='upper right')
            plt.show()

    def _plotGlossarDistribution(self, change):
        self._preparePlotDF(self.groupSelect.value)
        if 'all' in list(self.select.value):
            dfPlot = self.sortedPlotDF
        else:
            cols = list(self.select.value)
            cols.append(self.groupSelect.value)
            dfPlot = self.sortedPlotDF[cols]

        with self.plotOut:
            clear_output()
            ax = dfPlot.plot(
                kind='area',
                x=str(self.groupSelect.value),
                colormap='jet',
                use_index=False,
                figsize=(10, 5),
                legend=True,
                fontsize=10,
                stacked=True)
            ax.set_xlabel(str(self.groupSelect.value), fontsize=12)
            ax.set_ylabel("Count", fontsize=12)
            ax.legend(loc='upper right')
            plt.show()

    def displayWordGUI(self):
        display(self.choose, self.plotOut)

    def displayDistGUI(self):
        display(widgets.HBox([self.select, self.plotGroupOut, self.plot]), self.plotOut)
        with self.plotGroupOut:
            display(self.groupSelect)
