# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from collections import Counter, OrderedDict
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import ipywidgets as widgets
from IPython.display import clear_output

from .gui import CorpusGUI


class CorpusVisualization(CorpusGUI):
    """
    Visualization layer for corpus search.
    """

    def __init__(
            self, pathDF,
            dataType='pickle', dataIndex='multi', colname='text',
            maxValues=2500, pathMeta=False, pathType=False
        ):

        super(CorpusVisualization, self).__init__(
            pathDF, dataType, dataIndex, colname, maxValues, pathMeta, pathType)

        self.plotDict = {}

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

        self.plotLevel = widgets.Dropdown(
            options=self.colValueDictTrigger
            )

        self.resetPlot.on_msg(
            self._resetPlotFunc
        )

        self.plotout = widgets.Output()

    def _resetPlotFunc(self, widget, content, buffers):
        """Clear all previous plots."""
        self.plotDict.clear()
        level = self.plotLevel.value
        with self.plotout:
            clear_output()
            #self._initFigure(level)
            #plt.show()

    def _initFigure(self):
        """Basic initalization for matplotlib figure."""
        clear_output()
        xticks = []
        try:
            xticks = self.results()[self.plotLevel.value].unique()
            #if level in self.colValueDictTrigger and level != self.column:
            #    if level not in self.levelValues.keys():
            #        if self.dataindex == 'multi':
            #            self.levelValues[level] = self.result.index.get_level_values(level).unique()
            #        elif self.dataindex == 'single':
            #            self.levelValues[level] = self.result[level].unique()
            #    for vol in set(self.levelValues[level]):
            #        xticks.append((vol))
        except ValueError:
            print('Can not use {0} for plotting'.format(level))

        xtickslabels = sorted(xticks, key=lambda x: x[0])

        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
        ax.set_xticks(np.linspace(1,  len(xtickslabels) + 1, len(xtickslabels), endpoint=False))
        ax.set_xticklabels(xtickslabels, rotation=45)
        ax.set_yticks(np.linspace(0, 1, 5))
        ax.set_yticklabels(['0', '', '0.5', '', '1'])

    def _countExp(self, expr, row):
        """Count occurance per level/column"""
        # TODO: redo this one
        pass

    def _plotFunction(self, widget, content, buffers):
        resDict = {}
        iterate = [x for x in self.results()[self.plotLevel.value]]
        resDict = OrderedDict(Counter(elem for elem in iterate))
        level = self.plotLevel.value
        with self.plotout:
            clear_output()
            xticks = []
            try:
                if self.column != self.plotLevel.value:
                    xticks = self.results()[self.plotLevel.value].unique()
            except ValueError:
                print('Can not use {0} for plotting'.format(level))

            xtickslabels = sorted(xticks, key=lambda x: x[0])

            fig = plt.figure(figsize=(8, 8))
            ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
            ax.set_xticks(np.linspace(1,  len(xtickslabels) + 1, len(xtickslabels), endpoint=False))
            ax.set_xticklabels(xtickslabels, rotation=45)
            yMax = int(max(resDict.values()))
            ax.set_yticks(np.arange(0, yMax+1,1))
            #ax.set_yticklabels(['0', '', str(yMax/2), '', str(yMax)])
            # self._initFigure()
            labelStr = ' '.join([ch.value for ch in self.accordion.children])
            x = [x for x in range(1, len(resDict.keys())+1)]
            # maxRadius = max(list(resDict.values()))
            y = [y for y in resDict.values()]
            # self.plotDict[labelStr] = (resDict.values(), maxRadius)
            # i = 0
            # maxVal = sorted([v[1] for key, v in self.plotDict.items()])[-1]
            # colors = [cm.jet(i) for i in np.linspace(0, 1, len(self.plotDict.keys()))]
            # for key, value in self.plotDict.items():
            # radii = [xo for xo in [x/maxVal for x in value[0]]]
            ax.bar(x, y, width=0.3, alpha=0.3, label=labelStr)

            ax.legend()

            plt.show()

    def displayGUI(self):
        """Display the GUI for CorpusTextSearch"""
        searchControl = widgets.HBox([self.extendSearch, self.searchButton, self.outInfo])
        textControl = widgets.HBox([self.direction])
        sentenceFields = widgets.HBox([self.outMeta, self.outSentence])
        visualControl = widgets.HBox([self.plot, self.plotLevel, self.resetPlot])
        searchBox = widgets.VBox([
            self.accordion, searchControl, textControl, sentenceFields,
            visualControl, self.plotout
            ]
        )

        return display(searchBox)

    def showVisualButton(self):
        box = widgets.HBox([self.plot, self.plotLevel, self.resetPlot])
        display(widgets.VBox([box, self.plotout]))
