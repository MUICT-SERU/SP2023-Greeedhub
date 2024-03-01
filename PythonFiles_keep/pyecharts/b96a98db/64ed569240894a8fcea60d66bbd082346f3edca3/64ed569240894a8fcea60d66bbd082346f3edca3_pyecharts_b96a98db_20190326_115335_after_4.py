# coding=utf-8
from ... import options as opts
from ...charts.chart import Chart
from ...commons.types import Numeric, Sequence, Union
from ...globals import ChartType


class Tree(Chart):
    """
    <<< 树图 >>>

    树图主要用来可视化树形数据结构，是一种特殊的层次类型，具有唯一的根节点，左子树，和右子树。
    """

    def __init__(self, init_opts: Union[opts.InitOpts, dict] = opts.InitOpts()):
        super().__init__(init_opts=init_opts)

    @staticmethod
    def _set_collapse_interval(data, interval=0):
        """
        间隔折叠节点，当节点过多时可以解决节点显示过杂间隔。

        :param data: 节点数据
        :param interval: 指定间隔
        """
        if interval <= 0:
            return data
        if data and isinstance(data, list):
            children = data[0].get("children", None)
            if children and interval > 0:
                for index, value in enumerate(children):
                    if index % interval == 0:
                        value.update(collapsed="false")
                return data

    def add(
        self,
        series_name: str,
        data: Sequence,
        layout: str = "orthogonal",
        symbol: str = "emptyCircle",
        symbol_size: Numeric = 7,
        orient: str = "LR",
        top: str = "12%",
        left: str = "12%",
        bottom: str = "12%",
        right: str = "12%",
        collapse_interval: Numeric = 0,
        label_opts: Union[opts.LabelOpts, dict] = opts.LabelOpts(),
        leaves_label_opts: Union[opts.LabelOpts, dict] = opts.LabelOpts(),
        tooltip_opts: Union[opts.TooltipOpts, dict, None] = None,
    ):
        if isinstance(label_opts, opts.LabelOpts):
            label_opts = label_opts.opts
        if isinstance(leaves_label_opts, opts.LabelOpts):
            leaves_label_opts = leaves_label_opts.opts
        if isinstance(tooltip_opts, opts.TooltipOpts):
            tooltip_opts = tooltip_opts.opts

        _data = self._set_collapse_interval(data, collapse_interval)
        self.options.get("series").append(
            {
                "type": ChartType.TREE,
                "name": series_name,
                "data": _data,
                "left": left,
                "right": right,
                "top": top,
                "bottom": bottom,
                "symbol": symbol,
                "symbolSize": symbol_size,
                "layout": layout,
                "orient": orient,
                "label": label_opts,
                "leaves": {"label": leaves_label_opts},
                "tooltip": tooltip_opts,
            }
        )
        return self
