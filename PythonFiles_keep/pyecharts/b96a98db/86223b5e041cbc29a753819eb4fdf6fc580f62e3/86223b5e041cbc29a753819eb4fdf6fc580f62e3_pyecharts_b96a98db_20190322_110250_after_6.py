# coding=utf-8
from ... import options as opts
from ...charts.chart import Chart
from ...commons.types import ListTuple, Numeric, Union
from ...consts import CHART_TYPE


class Gauge(Chart):
    """
    <<< 仪表盘 >>>
    """

    def __init__(self, init_opts: Union[opts.InitOpts, dict] = opts.InitOpts()):
        super().__init__(init_opts=init_opts)

    def add(
        self,
        series_name: str,
        data_pair: ListTuple,
        min_: Numeric = 0,
        max_: Numeric = 100,
        start_angle: Numeric = 225,
        end_angle: Numeric = -45,
    ):
        self._append_legend(series_name)
        self.options.get("series").append(
            {
                "type": CHART_TYPE.GAUGE,
                "detail": {"formatter": "{value}%"},
                "name": series_name,
                "min": min_,
                "max": max_,
                "startAngle": start_angle,
                "endAngle": end_angle,
                "data": [{"value": v, "name": n} for (v, n) in data_pair],
            }
        )
        return self
