# coding=utf-8
from ... import options as opts
from ...charts.chart import Chart
from ...commons.types import ListTuple, Optional, Union
from ...consts import CHART_TYPE


class Map(Chart):
    """
    <<< 地图 >>>

    地图主要用于地理区域数据的可视化。
    """

    def __init__(self, init_opts: Union[opts.InitOpts, dict] = opts.InitOpts()):
        super().__init__(init_opts=init_opts)

    def add(
        self,
        series_name: str,
        data_pair: ListTuple,
        maptype: str = "china",
        *,
        is_roam: bool = True,
        symbol: Optional[str] = None,
        is_map_symbol_show: bool = True,
        label_opts: Union[opts.LabelOpts, dict] = opts.LabelOpts(),
    ):
        if isinstance(label_opts, opts.LabelOpts):
            label_opts = label_opts.opts

        self.js_dependencies.add(maptype)
        data = [{"name": n, "value": v} for (n, v) in data_pair]
        self._append_legend(series_name)
        self.options.get("series").append(
            {
                "type": CHART_TYPE.MAP,
                "name": series_name,
                "symbol": symbol,
                "label": label_opts,
                "mapType": maptype,
                "data": data,
                "roam": is_roam,
                "showLegendSymbol": is_map_symbol_show,
            }
        )
        return self
