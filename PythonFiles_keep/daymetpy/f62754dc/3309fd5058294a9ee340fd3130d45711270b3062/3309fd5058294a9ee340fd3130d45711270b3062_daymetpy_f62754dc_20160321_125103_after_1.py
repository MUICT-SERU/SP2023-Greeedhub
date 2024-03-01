__version__ = '0.0.2'

try:
    from daymetpy import daymet_timeseries
except ImportError:
    from daymetpy.daymetpy import daymet_timeseries

__all__ = ["daymet_timeseries"]