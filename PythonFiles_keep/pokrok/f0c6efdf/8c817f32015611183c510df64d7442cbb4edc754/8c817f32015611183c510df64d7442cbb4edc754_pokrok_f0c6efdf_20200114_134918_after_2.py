from datetime import datetime
import sys

from pokrok.plugins import DefaultProgressMeterFactory, BaseProgressMeter
from pokrok.styles import Style, Widget


STYLE_SUPERSET = Style(
    sized=[Widget.BAR, Widget.COUNTER, Widget.PERCENT, Widget.ELAPSED],
    unsized=[Widget.COUNTER, Widget.ELAPSED],
)


class LoggingProgressMeterFactory(DefaultProgressMeterFactory):
    def __init__(self):
        super().__init__("Logging", LoggingProgressMeter, STYLE_SUPERSET)


class LoggingProgressMeter(BaseProgressMeter):
    """
    Progress meter that logs messages at a specified interval.

    Args:
        interval: The reporting interval.
        logger_name:
    """

    def __init__(
        self,
        mod,
        size,
        widgets,
        desc="",
        start=0,
        unit=None,
        multiplier=None,
        interval: int = 1000,
        logger_name: str = "progress",
        logger_level: str = "INFO",
        **_,
    ):
        super().__init__(size)

        self._logger = mod.getLogger(logger_name)
        self._logger.setLevel(logger_level)
        if not self._logger.hasHandlers():
            self._logger.addHandler(mod.StreamHandler(sys.stderr))
        self._level = logger_level

        self.count = start or 0
        self.size = size
        self.interval = interval
        self.multiplier = multiplier
        self.start_time = None
        self._scale = 1
        self._bar_size = 10
        self._bar_char = "*"

        default_widgets = STYLE_SUPERSET.get_widgets(size is not None)

        if widgets is None:
            widgets = default_widgets
        else:
            allowed = set(default_widgets)
            widgets = [w for w in widgets if w in allowed]

        self.key_fns = {}
        message = []

        if desc:
            message.append(desc)

        for w in widgets:
            if w == Widget.COUNTER:
                if size:
                    for suffix in ["", "k", "M", "G", "T", "P", "E", "Z"]:
                        if size < 1000:
                            break
                        size /= 1000
                        self._scale *= 1000
                    if suffix:
                        message.append("{count:.2f}/" + "{:.2f}".format(size) + suffix)
                    else:
                        message.append("{count}/" + str(size))
                else:
                    message.append("{count}")
                if unit:
                    message.append(unit)
                self.key_fns["count"] = lambda: self.count / self._scale
            elif w == Widget.ELAPSED:
                message.append("{elapsed:.1f} seconds")
                self.key_fns["elapsed"] = (
                    lambda: datetime.now().timestamp() - self.start_time.timestamp()
                )
            elif w == Widget.BAR:
                message.append("{bar}")
                bar_fmt = "[{{: <{}}}]".format(self._bar_size)
                self.key_fns["bar"] = lambda: bar_fmt.format(
                    self._bar_char * round((self.count / self.size) * self._bar_size)
                )
            elif w == Widget.PERCENT and size is not None:
                if Widget.COUNTER in widgets:
                    message.append("({percent:.0%})")
                else:
                    message.append("{percent:.0%}")
                self.key_fns["percent"] = lambda: self.count / self.size

        self.message = " ".join(message)

    def start(self):
        super().start()
        self.start_time = datetime.now()

    def finish(self):
        super().finish()
        self._logger.log(self._level, f"Read a total of {self.count} records")

    def increment(self, n=1):
        cur_mod = self.count % self.interval
        if self.multiplier:
            n *= self.multiplier
        self.count += n
        if (self.count % self.interval) <= cur_mod:
            format_kwargs = dict((key, fn()) for key, fn in self.key_fns.items())
            self._logger.log(self._level, self.message.format(**format_kwargs))
