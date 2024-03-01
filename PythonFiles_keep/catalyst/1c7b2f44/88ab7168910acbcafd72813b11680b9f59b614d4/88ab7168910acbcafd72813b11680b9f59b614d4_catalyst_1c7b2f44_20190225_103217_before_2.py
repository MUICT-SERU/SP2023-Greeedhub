import os
import logging
import json
from abc import ABC, abstractmethod
from datetime import time, datetime
from typing import List, Dict, Mapping

from catalyst.dl.callbacks import Callback
from catalyst.dl.state import RunnerState
from catalyst.dl.utils import UtilsFactory
from .utils import to_batch_metrics


class MetricsFormatter(ABC, logging.Formatter):
    def __init__(self, message_prefix):
        """
        :param message_prefix: logging fomat string that will be prepended to message
        """
        super().__init__(f"{message_prefix}{{message}}", style="{")

    @abstractmethod
    def _format_message(self, state: RunnerState):
        pass

    def format(self, record: logging.LogRecord):
        # noinspection PyUnresolvedReferences
        state = record.state

        record.msg = self._format_message(state)

        return super().format(record)


class TxtMetricsFormatter(MetricsFormatter):
    """
    Translate batch metrics in human-readable format.

    This class is used by logging.Logger to make a string from record.
    For details refer to official docs for 'logging' module.

    Note:
        This is inner class used by Logger callback,
        no need to use it directly!
    """

    def __init__(self):
        super().__init__("[{asctime}] ")

    def _format_metrics(self, metrics: Mapping[str, float]):
        metrics_formatted = \
            [f"{name}={value:.5}" for name, value in sorted(metrics.items())]

        metrics_formatted = ', '.join(metrics_formatted)

        return metrics_formatted

    def _format_message(self, state: RunnerState):
        metrics = self._format_metrics(state.metrics.epoch_values)
        message = f"Epoch {state.epoch}: {metrics}"
        return message


class JsonMetricsFormatter(MetricsFormatter):
    """
    Translate batch metrics in json format.

    This class is used by logging.Logger to make a string from record.
    For details refer to official docs for 'logging' module.

    Note:
        This is inner class used by Logger callback,
        no need to use it directly!
    """

    def __init__(self):
        super().__init__("")

    def _format_message(self, state: RunnerState):
        res = dict(
            metirics=state.metrics.epoch_values.copy(),
            epoch=state.epoch,
            time=datetime.now().isoformat()
        )
        return json.dumps(res, indent=True, ensure_ascii=False)


class Logger(Callback):
    """
    Logger callback, translates state.*_metrics to console and text file
    """

    def __init__(self):
        """
        :param logdir: log directory to use for text logging
        """
        self.logger = None

    def on_stage_start(self, state: RunnerState):
        state.logdir.mkdir(parents=True, exist_ok=True)
        self.logger = self._get_logger(state.logdir)

    @staticmethod
    def _get_logger(logdir):
        logger = logging.getLogger("metrics")
        logger.setLevel(logging.DEBUG)

        fh = logging.FileHandler(f"{logdir}/metrics.txt")
        fh.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        jh = logging.FileHandler(f"{logdir}/metrics.json")
        jh.setLevel(logging.INFO)

        txt_formatter = TxtMetricsFormatter()
        json_formatter = JsonMetricsFormatter()
        fh.setFormatter(txt_formatter)
        ch.setFormatter(txt_formatter)
        jh.setFormatter(json_formatter)

        # add the handlers to the logger
        logger.addHandler(fh)
        logger.addHandler(ch)
        logger.addHandler(jh)
        return logger

    def on_epoch_end(self, state):
        self.logger.info("", extra={"state": state})


class TensorboardLogger(Callback):
    """
    Logger callback, translates state.*_metrics to tensorboard
    """

    # TODO:hexfaker update to support MetricManager

    def __init__(
        self,
        metric_names: List[str] = None,
        log_on_batch_end=True,
        log_on_epoch_end=True
    ):
        """
        :param logdir: directory where logs will be created
        :param metric_names: List of metric names to log.
            If none - logs everything.
        :param log_on_batch_end: Logs per-batch value of metrics,
            prepends 'batch_' prefix to their names.
        :param log_on_epoch_end: Logs per-epoch metrics if set True.
        """
        self.metrics_to_log = metric_names
        self.log_on_batch_end = log_on_batch_end
        self.log_on_epoch_end = log_on_epoch_end

        assert self.log_on_batch_end or self.log_on_epoch_end, \
            "You have to log something!"

        self.loggers = dict()

    def on_loader_start(self, state):
        lm = state.loader_name
        if lm not in self.loggers:
            self.loggers[lm] = UtilsFactory.create_tflogger(
                logdir=state.logdir, name=lm
            )

    def _log_metrics(
        self, metrics: Dict[str, float], step: int, mode: str, suffix=""
    ):
        if self.metrics_to_log is None:
            self.metrics_to_log = sorted(list(metrics.keys()))

        for name in self.metrics_to_log:
            if name in metrics:
                self.loggers[mode].add_scalar(
                    f"{name}{suffix}", metrics[name], step
                )

    def on_batch_end(self, state: RunnerState):
        if self.log_on_batch_end:
            mode = state.loader_name

            self._log_metrics(
                metrics=state.metrics.batch_values,
                step=state.step,
                mode=mode,
                suffix="/batch"
            )

    def on_loader_end(self, state: RunnerState):
        if self.log_on_epoch_end:
            mode = state.loader_name
            self._log_metrics(
                metrics=state.metrics.epoch_values,
                step=state.epoch,
                mode=mode,
                suffix="/epoch"
            )
