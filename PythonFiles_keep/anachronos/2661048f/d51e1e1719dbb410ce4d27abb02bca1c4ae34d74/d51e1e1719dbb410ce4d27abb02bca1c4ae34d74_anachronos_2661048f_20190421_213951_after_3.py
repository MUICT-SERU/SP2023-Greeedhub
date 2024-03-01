from anachronos.compat.jivago_streams import Stream
from anachronos.test.assertion import Assertion


class OccursEveryXSeconds(Assertion):

    def __init__(self, item, interval_s: int, tolerance_ms: int = 200):
        self.tolerance_ms = tolerance_ms
        self.item = item
        self.interval_s = interval_s

    def run(self, anachronos: "Anachronos"):
        times = Stream(anachronos.get_messages()) \
            .filter(lambda x: x.payload == self.item) \
            .map(lambda x: x.time) \
            .toList()

        fits_criteria = Stream.zip(times, times[1::]) \
            .map(lambda current, next: next - current) \
            .allMatch(self.is_within_interval)

        self._do_assertion(fits_criteria,
                           f'Failed "OccursEveryXSeconds" assertion. Expected {self.item} to occur every {self.interval_s}s.')

    def is_within_interval(self, delta_s) -> bool:
        return self.interval_s * 1000 - self.tolerance_ms <= delta_s.total_seconds() * 1000 <= self.interval_s * 1000 + self.tolerance_ms
