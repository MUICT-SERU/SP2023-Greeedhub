# coding=utf-8

import json

from ...charts.chart import Chart
from ...options import *
from ...types import *
from ...datasets import COORDINATES

DEFAULT_GEO_TOOLTIP_FORMATTER = "{b}: {c}"


class Geo(Chart):
    """
    <<< 地理坐标系 >>>

    地理坐标系组件用于地图的绘制，支持在地理坐标系上绘制散点图，线集。
    """

    def __init__(self, init_opts: InitOpts = InitOpts()):
        super().__init__(init_opts=init_opts)
        self._coordinates = COORDINATES

    def add_coordinate(self, name, longitude, latitude):
        """
        Add a geo coordinate for a position.

        :param name: The name of a position
        :param longitude: The longitude of coordinate.
        :param latitude: The latitude of coordinate.
        """
        self._coordinates.update({name: [longitude, latitude]})

    def add_coordinate_json(self, json_file):
        """
        add a geo coordinate json file for position

        :param json_file: geo coords json file
        """
        with open(json_file, "r", encoding="utf-8") as f:
            json_reader = json.load(f)
            for k, v in json_reader.items():
                self.add_coordinate(k, v[0], v[1])

    def get_coordinate(self, name) -> List:
        """
        Return coordinate for the city name.

        :param name: City name or any custom name string.
        :param region : The region
        :param raise_exception: Whether to raise exception if not exist.
        :return: A list like [longitude, latitude] or None
        """
        if name in self._coordinates:
            return self._coordinates[name]

    def add(
        self,
        name: str,
        data_pair: ListTuple,
        type_: str = "scatter",
        maptype: str = "china",
        symbol: Optional[str] = None,
        symbol_size: Numeric = 12,
        border_color="#111",
        normal_color="#323c48",
        emphasis_color="#2a333d",
        label_opts: LabelOpts() = LabelOpts(),
        effect_opts: EffectOpts() = EffectOpts(),
        region_coords=None,
        is_roam: bool = True,
    ):
        # if "tooltip_formatter" not in kwargs:
        #     kwargs["tooltip_formatter"] = DEFAULT_GEO_TOOLTIP_FORMATTER

        if region_coords:
            for city_name, city_coord in region_coords.items():
                self.add_coordinate(city_name, city_coord[0], city_coord[1])

        _data = []
        for (_name, _value) in data_pair:
            lng, lat = self.get_coordinate(_name)
            _data.append({"name": _name, "value": [lng, lat, _value]})

        self.options.update(
            geo={
                "map": maptype,
                "roam": is_roam,
                "label": {"emphasis": {"show": True, "textStyle": {"color": "#eee"}}},
                "itemStyle": {
                    "normal": {"areaColor": normal_color, "borderColor": border_color},
                    "emphasis": {"areaColor": emphasis_color},
                },
            }
        )
        self._append_legend(name)

        if type == "scatter":
            self.options.get("series").append(
                {
                    "type": type_,
                    "name": name,
                    "coordinateSystem": "geo",
                    "symbol": symbol,
                    "symbolSize": symbol_size,
                    "data": _data,
                    "label": label_opts.opts,
                }
            )

        elif type == "effectScatter":
            self.options.get("series").append(
                {
                    "type": type_,
                    "name": name,
                    "coordinateSystem": "geo",
                    "showEffectOn": "render",
                    "rippleEffect": effect_opts.opts,
                    "symbol": symbol,
                    "symbolSize": symbol_size,
                    "data": _data,
                    "label": label_opts.opts,
                }
            )

        elif type == "heatmap":
            self.options.get("series").append(
                {"type": type_, "name": name, "coordinateSystem": "geo", "data": _data}
            )
