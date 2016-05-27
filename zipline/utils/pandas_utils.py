"""
Utilities for working with pandas objects.
"""
from itertools import product
import operator as op

import pandas as pd


def explode(df):
    """
    Take a DataFrame and return a triple of

    (df.index, df.columns, df.values)
    """
    return df.index, df.columns, df.values


try:
    # pandas 0.16 compat
    _df_sort_values = pd.DataFrame.sort_values
    _series_sort_values = pd.Series.sort_values
except AttributeError:
    _df_sort_values = pd.DataFrame.sort
    _series_sort_values = pd.Series.sort


def sort_values(ob, *args, **kwargs):
    if isinstance(ob, pd.DataFrame):
        return _df_sort_values(ob, *args, **kwargs)
    elif isinstance(ob, pd.Series):
        return _series_sort_values(ob, *args, **kwargs)
    raise ValueError(
        'sort_values expected a dataframe or series, not %s: %r' % (
            type(ob).__name__, ob,
        ),
    )


def _time_to_micros(time):
    """Convert a time into microseconds since midnight.

    Parameters
    ----------
    time : datetime.time
        The time to convert.

    Returns
    -------
    us : int
        The number of microseconds since midnight.

    Notes
    -----
    This does not account for leap seconds or daylight savings.
    """
    seconds = time.hour * 60 * 60 + time.minute * 60 + time.second
    return 1000000 * seconds + time.microsecond


_opmap = dict(zip(
    product((True, False), repeat=3),
    product((op.le, op.lt), (op.le, op.lt), (op.and_, op.or_)),
))


def mask_between_time(dts, start, end, include_start=True, include_end=True):
    """Return a mask of all of the datetimes in ``dts`` that are between
    ``start`` and ``end``.

    Parameters
    ----------
    dts : pd.DatetimeIndex
        The index to mask.
    start : time
        Mask away times less than the start.
    end : time
        Mask away times greater than the end.
    include_start : bool, optional
        Inclusive on ``start``.
    include_end : bool, optional
        Inclusive on ``end``.

    Returns
    -------
    mask : np.ndarray[bool]
        A bool array masking ``dts``.

    See Also
    --------
    :meth:`pandas.DatetimeIndex.indexer_between_time`
    """
    # This function is adapted from
    # `pandas.Datetime.Index.indexer_between_time` which was originally
    # written by Wes McKinney, Chang She, and Grant Roch.
    time_micros = dts._get_time_micros()
    start_micros = _time_to_micros(start)
    end_micros = _time_to_micros(end)

    left_op, right_op, join_op = _opmap[
        bool(include_start),
        bool(include_end),
        start_micros <= end_micros,
    ]

    return join_op(
        left_op(start_micros, time_micros),
        right_op(time_micros, end_micros),
    )
