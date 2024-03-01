# coding=utf-8
from ... import options as opts
from ...charts.chart import AxisChart
from ...commons.types import ListTuple, Numeric, Optional, Union


class Line(AxisChart):
    """
    <<< 折线/面积图 >>>

    折线图是用折线将各个数据点标志连接起来的图表，用于展现数据的变化趋势。
    """

    def __init__(self, init_opts: Union[opts.InitOpts, dict] = opts.InitOpts()):
        super().__init__(init_opts=init_opts)
        self.options.update(yAxis=[opts.AxisOpts().opts])

    def add_yaxis(
        self,
        series_name: str,
        y_axis: ListTuple,
        *,
        is_symbol_show: bool = True,
        symbol: Optional[str] = None,
        symbol_size: Numeric = 4,
        stack: Optional[str] = None,
        is_smooth: bool = False,
        is_step: bool = False,
        label_opts: Union[opts.LabelOpts, dict] = opts.LabelOpts(),
        markpoint_opts: Union[opts.MarkPointOpts, dict, None] = None,
        markline_opts: Union[opts.MarkLineOpts, dict, None] = None,
        linestyle_opts: Union[opts.LineStyleOpts, dict] = opts.LineStyleOpts(),
        areastyle_opts: Union[opts.AreaStyleOpts, dict] = opts.AreaStyleOpts(),
    ):
        if isinstance(label_opts, opts.LabelOpts):
            label_opts = label_opts.opts
        if isinstance(markpoint_opts, opts.MarkPointOpts):
            markpoint_opts = markpoint_opts.opts
        if isinstance(markline_opts, opts.MarkLineOpts):
            markline_opts = markline_opts
        if isinstance(linestyle_opts, opts.LineStyleOpts):
            linestyle_opts = linestyle_opts.opts
        if isinstance(areastyle_opts, opts.AreaStyleOpts):
            areastyle_opts = areastyle_opts.opts

        self._append_legend(series_name)
        # 合并 x 和 y 轴数据，避免当 X 轴的类型设置为 'value' 的时候，
        # X、Y 轴均显示 Y 轴数据
        data = [list(z) for z in zip(self._xaxis_data, y_axis)]

        self.options.get("series").append(
            {
                "type": "line",
                "name": series_name,
                "symbol": symbol,
                "symbolSize": symbol_size,
                "smooth": is_smooth,
                "step": is_step,
                "stack": stack,
                "showSymbol": is_symbol_show,
                "data": data,
                "label": label_opts,
                "lineStyle": linestyle_opts,
                "areaStyle": areastyle_opts,
                "markPoint": markpoint_opts,
                "markLine": markline_opts,
            }
        )
        return self
