# coding=utf-8
from ... import options as opts
from ...charts.chart import Chart
from ...commons.types import ListTuple, Union


class Polar(Chart):
    """
    <<< 极坐标系 >>>

    可以用于散点图和折线图。
    """

    def __init__(self, init_opts: Union[opts.InitOpts, dict] = opts.InitOpts()):
        super().__init__(init_opts=init_opts)

    def add(
        self,
        series_name: str,
        data: ListTuple,
        angle_data=None,
        radius_data=None,
        type_: str = "line",
        symbol_size=4,
        start_angle=90,
        boundary_gap=True,
        axis_range=None,
        is_clockwise: bool = True,
        is_stack: bool = False,
        is_angleaxis_show: bool = True,
        is_radiusaxis_show: bool = True,
        radiusaxis_z_index=50,
        angleaxis_z_index=50,
        render_item=None,
        symbol=None,
        label_opts: Union[opts.LabelOpts, dict] = opts.LabelOpts(),
        areastyle_opts: Union[opts.AreaStyleOpts, dict] = opts.AreaStyleOpts(),
        axisline_opts: Union[opts.AxisLineOpts, dict] = opts.AxisLineOpts(),
        splitline_opts: Union[opts.SplitLineOpts, dict] = opts.SplitLineOpts(),
        effect_opts: Union[opts.EffectOpts, dict] = opts.EffectOpts(),
        axislabel_opts: Union[opts.LabelOpts, dict] = opts.LabelOpts(),
    ):

        if isinstance(label_opts, opts.LabelOpts):
            label_opts = label_opts.opts
        if isinstance(areastyle_opts, opts.AreaStyleOpts):
            areastyle_opts = areastyle_opts.opts
        if isinstance(axisline_opts, opts.AxisLineOpts):
            axisline_opts = axisline_opts.opts
        if isinstance(splitline_opts, opts.SplitLineOpts):
            splitline_opts = splitline_opts.opts
        if isinstance(effect_opts, opts.EffectOpts):
            effect_opts = effect_opts.opts
        if isinstance(axislabel_opts, opts.LabelOpts):
            axislabel_opts = axislabel_opts.opts

        polar_type = "value" if type == "line" else "category"
        is_stack = "stack" if is_stack else ""
        self._append_legend(series_name)

        _amin, _amax = None, None
        if axis_range:
            if len(axis_range) == 2:
                _amin, _amax = axis_range

        # _area_style = chart["area_style"]
        if kwargs.get("area_color", None) is None:
            _area_style = None

        bar_type_series = {
            "type": "bar",
            "coordinateSystem": "polar",
            "stack": is_stack,
            "name": series_name,
            "data": data,
        }

        radius_axis_opt = {
            "show": is_radiusaxis_show,
            "type": polar_type,
            "data": radius_data,
            "min": _amin,
            "max": _amax,
            "axisLine": axisline_opts,
            "axisLabel": axislabel_opts,
            "z": radiusaxis_z_index,
        }

        angle_axis_opt = {
            "show": is_angleaxis_show,
            "type": polar_type,
            "data": angle_data,
            "clockwise": is_clockwise,
            "startAngle": start_angle,
            "boundaryGap": boundary_gap,
            "splitLine": splitline_opts,
            "axisLine": axisline_opts,
            "axisLabel": axislabel_opts,
            "z": angleaxis_z_index,
        }

        if type in ("scatter", "line"):
            self.options.get("series").append(
                {
                    "type": type_,
                    "name": series_name,
                    "coordinateSystem": "polar",
                    "symbol": symbol,
                    "symbolSize": symbol_size,
                    "data": data,
                    "label": label_opts,
                    "areaStyle": areastyle_opts,
                }
            )

        elif type == "effectScatter":
            self.options.get("series").append(
                {
                    "type": type_,
                    "name": series_name,
                    "coordinateSystem": "polar",
                    "showEffectOn": "render",
                    "rippleEffect": effect_opts,
                    "symbol": symbol,
                    "symbolSize": symbol_size,
                    "data": data,
                    "label": label_opts,
                }
            )

        elif type == "barRadius":
            self.options.get("series").append(bar_type_series)
            self.options.update(angleAxis={})
            self.options.update(radiusAxis=radius_axis_opt)

        elif type == "barAngle":
            self.options.get("series").append(bar_type_series)
            self.options.update(radiusAxis={"show": is_radiusaxis_show})
            self.options.update(angleAxis=angle_axis_opt)

        elif type == "custom":
            assert render_item is not None
            self.options.get("series").append(
                {
                    "type": "custom",
                    "name": series_name,
                    "coordinateSystem": "polar",
                    "data": data,
                    "renderItem": render_item,
                }
            )

        if type not in ("barAngle", "barRadius"):
            self.options.update(angleAxis=angle_axis_opt)
            self.options.update(radiusAxis=radius_axis_opt)
        self.options.update(polar={})
        return self
