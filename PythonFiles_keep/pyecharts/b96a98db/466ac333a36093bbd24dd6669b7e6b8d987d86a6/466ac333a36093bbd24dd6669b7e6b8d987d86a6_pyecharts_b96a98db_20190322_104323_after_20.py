# coding=utf-8
from ... import options as opts
from ...charts.chart import Chart
from ...commons.types import ListTuple, Union


class ThemeRiver(Chart):
    """
    <<< 主题河流图 >>>

    主题河流图是一种特殊的流图, 它主要用来表示事件或主题等在一段时间内的变化。
    """

    def __init__(self, init_opts: Union[opts.InitOpts, dict] = opts.InitOpts()):
        super().__init__(init_opts=init_opts)

    def add(
        self,
        series_name: str,
        data: ListTuple,
        label_opts: Union[opts.LabelOpts, dict] = opts.LabelOpts(),
    ):
        if isinstance(label_opts, opts.LabelOpts):
            label_opts = label_opts.opts

        self._append_legend(series_name)
        self.options.get("series").append(
            {
                "type": "themeRiver",
                "name": series_name,
                "data": data,
                "label": label_opts,
            }
        )

        self.options.update(singleAxis={"type": "time"})
        self.options.get("tooltip").update(trigger="axis")
        return self
