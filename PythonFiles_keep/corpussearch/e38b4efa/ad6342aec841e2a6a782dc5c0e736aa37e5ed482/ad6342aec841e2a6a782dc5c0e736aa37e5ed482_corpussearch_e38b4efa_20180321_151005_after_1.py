# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from collections import Counter, OrderedDict
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import ipywidgets as widgets
from IPython.display import clear_output


class CorpusVisualization(object):
    """
    Visualization layer for corpus search.
    """

    def __init__(self,search):
        self.search = search
        self.plotDict = {}
        plt.style.use('seaborn-deep')

        self.resetPlot = widgets.Button(
            description='Reset plot'
            )

        self.plotLevel = widgets.Text(
            description='Plot level',
            value=''
            )

        self.resetPlot.on_msg(
            self._resetPlotFunc(widget, content, buffers, self.plotLevel.value)
        )

        self.plotout = widgets.Output()

    def _resetPlotFunc(self, widget, content, buffers, level):
        """Clear all previous plots."""
        self.plotDict.clear()
        with self.plotout:
            self._initFigure(level)
            plt.show()

    def _initFigure(self,level):
        """Basic initalization for matplotlib figure."""
        clear_output()
        xticks = []
        try:
            if level in self.search.colValueDictTrigger and level != self.search.column:
                if level not in self.search.levelValues.keys():
                    if self.search.dataindex == 'multi':
                        self.search.levelValues[level] = self.search.dataframe.index.get_level_values(level).unique()
                    elif self.search.dataindex == 'single':
                        self.search.levelValues[level] = self.search.dataframe[level].unique()
                for vol in set(self.search.levelValues[level]):
                    xticks.append((vol))
        except ValueError:
            print('Can not use {0} for plotting'.format(level))

        xtickslabels = sorted(xticks, key=lambda x: x[0])

        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
        ax.set_xticks(np.linspace(1,  len(xtickslabels) + 1, len(xtickslabels), endpoint=False))
        ax.set_xticklabels(xtickslabels, rotation=45)
        ax.set_yticks(np.linspace(0.2, 1, 5))
        ax.set_yticklabels(['0', '', '0.5', '', '1'])

    def _countExp(self, expr, row):
        """Count occurance per level/column"""
        # TODO: redo this one
        pass

    def handle_submit(self, widget, content, buffers):
        resDict = {}
        iterate = [x[0] for x in self.result().iterrows()]
        resDict = OrderedDict(Counter((elem[0], elem[1]) for elem in iterate))
        with plotout:
            self._initFigure()
            labelStr = ' '.join([ch.value for ch in accordion.children])
            x = [x for x in range(1, len(resDict.keys())+1)]
            maxRadius = max(list(resDict.values()))
            radii = [xo for xo in [x/maxRadius for x in resDict.values()]]
            plotDict[labelStr] = (resDict.values(), maxRadius)
            i = 0
            maxVal = sorted([v[1] for key, v in plotDict.items()])[-1]
            colors = [cm.jet(i) for i in np.linspace(0, 1, len(plotDict.keys()))]
            for key, value in plotDict.items():
                radii = [xo for xo in [x/maxVal for x in value[0]]]
                ax.bar(x, radii, width=0.3, alpha=0.3, color=colors[i], label=key)
                i += 1

            ax.legend()

            plt.show()

    def showVisualButton(self):
        box = widgets.HBox([plotLevel,resetPlot])
        display(box)
