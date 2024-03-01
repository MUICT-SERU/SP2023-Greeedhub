# coding=utf-8
from ... import options as opts
from ...charts.chart import Chart
from ...commons.types import ListTuple, Optional, Union
from ...consts import CHART_TYPE


class Radar(Chart):
    """
    <<< 雷达图 >>>

    雷达图主要用于表现多变量的数据。
    """

    def __init__(self, init_opts: Union[opts.InitOpts, dict] = opts.InitOpts()):
        super().__init__(init_opts=init_opts)

    def set_radar_component(
        self,
        schema=None,
        c_schema=None,
        shape="",
        text_color="#333",
        text_size=12,
        splitline_opt: Union[opts.SplitLineOpts, dict] = opts.SplitLineOpts(),
        splitarea_opt: Union[opts.SplitAreaOpts, dict] = opts.SplitAreaOpts(),
        axisline_opt: Union[opts.AxisLineOpts, dict] = opts.AxisLineOpts(),
    ):
        if isinstance(splitline_opt, opts.SplitLineOpts):
            splitline_opt = splitline_opt.opts
        if isinstance(splitarea_opt, opts.SplitAreaOpts):
            splitarea_opt = splitarea_opt.opts
        if isinstance(axisline_opt, opts.AxisLineOpts):
            axisline_opt = axisline_opt.opts

        indicator = []
        if schema:
            for s in schema:
                _name, _max = s
                indicator.append({"name": _name, "max": _max})
        if c_schema:
            indicator = c_schema
        self.options.update(
            radar={
                "indicator": indicator,
                "shape": shape,
                "name": {"textStyle": {"color": text_color, "fontSize": text_size}},
                "splitLine": splitline_opt,
                "splitArea": splitarea_opt,
                "axisLine": axisline_opt,
            }
        )
        return self

    def add(
        self,
        series_name: str,
        value: ListTuple,
        symbol: Optional[str] = None,
        item_color=None,
        label_opts: opts.LabelOpts = opts.LabelOpts(),
        linestyle_opts: opts.LineStyleOpts = opts.LineStyleOpts(),
        areastyle_opts: opts.AreaStyleOpts = opts.AreaStyleOpts(),
    ):
        if isinstance(label_opts, opts.LabelOpts):
            label_opts = label_opts.opts
        if isinstance(linestyle_opts, opts.LineStyleOpts):
            linestyle_opts = linestyle_opts.opts
        if isinstance(areastyle_opts, opts.AreaStyleOpts):
            areastyle_opts = areastyle_opts.opts

        self._append_legend(series_name)
        self.options.get("series").append(
            {
                "type": CHART_TYPE.RADAR,
                "name": series_name,
                "data": value,
                "symbol": symbol,
                "label": label_opts,
                "itemStyle": {"normal": {"color": item_color}},
                "lineStyle": linestyle_opts,
                "areaStyle": areastyle_opts,
            }
        )
        return self
