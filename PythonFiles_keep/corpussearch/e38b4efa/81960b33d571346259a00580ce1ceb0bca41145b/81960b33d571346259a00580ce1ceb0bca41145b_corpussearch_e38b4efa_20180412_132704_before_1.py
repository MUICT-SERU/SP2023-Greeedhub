# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import math
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
            placeholder='callable function, e.g., row["number"] > 10'
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
                series = self.resultDF.apply(lambda row: eval(self.addColumnField.value),axis=1)
                self.resultDF = self.resultDF.assign(lambda_func=series)
            except:
                print('failed assiging new column')
        else:
            level = self.plotLevel.value
        with self.plotout:
            if math.isclose(len(self.resultDF[level].unique())/self.resultDF.shape[0], 1, rel_tol=0.2):
                clear_output()
                print('Difference between number of unique values and dataframe dimension to small.')
            else:
                clear_output()
                iterate = [x for x in self.resultDF[level]]
                resDict = OrderedDict(Counter(elem for elem in iterate))
                xticks = []
                try:
                    xticks = self.resultDF[level].unique().tolist()
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
