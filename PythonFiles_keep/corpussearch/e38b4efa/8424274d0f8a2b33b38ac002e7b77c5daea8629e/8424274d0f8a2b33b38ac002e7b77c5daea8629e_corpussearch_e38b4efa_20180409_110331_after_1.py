# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
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

    def __init__(self, searchObject):
        self.plotDict = {}
        self.results = searchObject.results
        self.accordion = searchObject.accordion
        self.column = searchObject.column
        self.colValueDictTrigger = searchObject.colValueDictTrigger
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

    def _initFigure(self):
        """Basic initalization for matplotlib figure."""
        clear_output()
        xticks = []
        try:
            xticks = self.results()[self.plotLevel.value].unique()
        except ValueError:
            print('Can not use {0} for plotting'.format(level))

        xtickslabels = sorted(xticks, key=lambda x: x[0])

        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
        ax.set_xticks(
            np.linspace(
                1,  len(xtickslabels) + 1, len(xtickslabels)
            , endpoint=False))
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
            ax.set_yticks(np.arange(0, yMax+1, 1))
            labelStr = ' '.join([ch.value for ch in self.accordion.children])
            x = [x for x in range(1, len(resDict.keys())+1)]
            y = [y for y in resDict.values()]
            ax.bar(x, y, width=0.3, alpha=0.3, label=labelStr)
            ax.legend()
            plt.show()

    def displayGUI(self):
        """Display the buttons for visual control and display"""
        visualControl = widgets.HBox([self.plot, self.plotLevel, self.resetPlot])
        searchBox = widgets.VBox([visualControl, self.plotout])
        return display(searchBox)
