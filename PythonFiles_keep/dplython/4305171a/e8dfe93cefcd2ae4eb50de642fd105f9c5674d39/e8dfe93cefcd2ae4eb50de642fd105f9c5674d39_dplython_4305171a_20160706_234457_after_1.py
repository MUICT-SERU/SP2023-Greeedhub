# Chris Riederer
# 2016-02-17

"""Dplyr-style operations on top of pandas DataFrame."""

from functools import wraps
import itertools
import sys
import types
import warnings
warnings.simplefilter("once")

import six
from six.moves import range

import numpy as np
import pandas
from pandas import DataFrame

from later import (Later, CreateLaterFunction, DelayFunction, X,
                   Manager)

__version__ = "0.0.4"


def _addQuotes(item):
  return '"' + item + '"' if isinstance(item, str) else item

# TODOs:
# add len to Later

# * Descending and ascending for arrange
# * diamonds >> select(-X.cut)
# * Move special function Later code into Later object
# * Add more tests
# * Reflection thing in Later -- understand this better
# * Should rename some things to be clearer. "df" isn't really a df in the 
    # __radd__ code, for example 
# * lint
# * Let users use strings instead of Laters in certain situations
#     e.g. select("cut", "carat")
# * What about implementing Manager as a container as well? This would help
#     with situations where column names have spaces. X["type of horse"]
# * Should I enforce that output is a dataframe?
#     For example, should df >> (lambda x: 7) be allowed?
# * Pass args, kwargs into sample

# Scratch
# https://mtomassoli.wordpress.com/2012/03/18/currying-in-python/
# http://stackoverflow.com/questions/16372229/how-to-catch-any-method-called-on-an-object-in-python
# Sort of define your own operators: http://code.activestate.com/recipes/384122/
# http://pandas.pydata.org/pandas-docs/stable/internals.html
# I think it might be possible to override __rrshift__ and possibly leave 
#   the pandas dataframe entirely alone.
# http://www.rafekettler.com/magicmethods.html


class DplyFrame(DataFrame):
  """A subclass of the pandas DataFrame with methods for function piping.

  This class implements two main features on top of the pandas DataFrame. First,
  dplyr-style groups. In contrast to SQL-style or pandas style groups, rows are 
  not collapsed and replaced with a function value.
  Second, >> is overloaded on the DataFrame so that functions on the right-hand
  side of this equation are called on the object. For example,
  
  >>> df >> select(X.carat)
  
  will call a function (created from the "select" call) on df.

  Currently, these inputs need to be one of the following:

  * A "Later" 
  * The "ungroup" function call
  * A function that returns a pandas DataFrame or DplyFrame.
  """
  _metadata = ["_grouped_on", "_grouped_self"]

  def __init__(self, *args, **kwargs):
    super(DplyFrame, self).__init__(*args, **kwargs)
    self._grouped_on = None
    self._current_group = None
    self._grouped_self = None
    if len(args) == 1 and isinstance(args[0], DplyFrame):
      self._copy_attrs(args[0])

  def _copy_attrs(self, df):
    for attr in self._metadata:
      self.__dict__[attr] = getattr(df, attr, None)

  @property
  def _constructor(self):
    return DplyFrame

  def group_self(self, names):
    self._grouped_on = names
    self._grouped_self = self.groupby(names)

  def ungroup(self):
    self._grouped_on = None
    self._grouped_self = None

  def apply_on_groups(self, delayedFcn):
    outDf = self._grouped_self.apply(delayedFcn)

    # Remove multi-index created from grouping and applying
    for grouped_name in outDf.index.names[:-1]:
      if grouped_name in outDf:
        outDf.reset_index(level=0, drop=True, inplace=True)
      else:
        outDf.reset_index(level=0, inplace=True)

    # Drop all 0 index, created by summarize
    if (outDf.index == 0).all():
      outDf.reset_index(drop=True, inplace=True)

    outDf.group_self(self._grouped_on)
    return outDf

  def __rshift__(self, delayedFcn):

    if type(delayedFcn) == Later:
      return delayedFcn.evaluate(self)

    if delayedFcn == UngroupDF:
      otherDf = DplyFrame(self.copy(deep=True))
      return delayedFcn(otherDf)

    if self._grouped_self:
      outDf = self.apply_on_groups(delayedFcn)
      return outDf
    else:
      otherDf = DplyFrame(self.copy(deep=True))
      return delayedFcn(otherDf)


def ApplyToDataframe(fcn):
  @wraps(fcn)
  def DplyrFcn(*args, **kwargs):
    data_arg = None
    if len(args) > 0 and isinstance(args[0], pandas.DataFrame):
      # data_arg = args[0].copy(deep=True)
      data_arg = args[0]
      if 'join' not in fcn.__name__:
        args = args[1:]
    fcn_to_apply = fcn(*args, **kwargs)
    if data_arg is None:
      return fcn_to_apply
    else:
      return data_arg >> fcn_to_apply
  return DplyrFcn


@ApplyToDataframe
def sift(*args):
  """Filters rows of the data that meet input criteria.

  Giving multiple arguments to sift is equivalent to a logical "and".
  
  >>> df >> sift(X.carat > 4, X.cut == "Premium")
  # Out:
  # carat      cut color clarity  depth  table  price      x  ...
  #  4.01  Premium     I      I1   61.0     61  15223  10.14
  #  4.01  Premium     J      I1   62.5     62  15223  10.02
  
  As in pandas, use bitwise logical operators like ``|``, ``&``:
  
  >>> df >> sift((X.carat > 4) | (X.cut == "Ideal")) >> head(2)
  # Out:  carat    cut color clarity  depth ...
  #        0.23  Ideal     E     SI2   61.5     
  #        0.23  Ideal     J     VS1   62.8     
  """
  def f(df):
    # TODO: This function is a candidate for improvement!
    final_filter = pandas.Series([True for t in range(len(df))])
    final_filter.index = df.index
    for arg in args:
      stmt = arg.evaluate(df)
      final_filter = final_filter & stmt
    if final_filter.dtype != bool:
      raise Exception("Inputs to filter must be boolean")
    return df[final_filter]
  return f


def dfilter(*args, **kwargs):
  warnings.warn("'dfilter' is deprecated. Please use 'sift' instead.",
                DeprecationWarning)
  return sift(*args, **kwargs)


@ApplyToDataframe
def select(*args):
  """Select specific columns from DataFrame. 

  Output will be DplyFrame type. Order of columns will be the same as input into
  select.

  >>> diamonds >> select(X.color, X.carat) >> head(3)
  Out:
    color  carat
  0     E   0.23
  1     E   0.21
  2     E   0.23
  """
  return lambda df: df[[column._name for column in args]]


def _dict_to_possibly_ordered_tuples(dict_):
  order = dict_.pop("__order", None)
  if order:
    ordered_keys = set(order)
    dict_keys = set(dict_)

    missing_order = ordered_keys - dict_keys
    if missing_order:
      raise ValueError(", ".join(missing_order) +
                       " in __order not found in keyword arguments")

    missing_kwargs = dict_keys - ordered_keys
    if missing_kwargs:
      raise ValueError(", ".join(missing_kwargs) + " not found in __order")

    return [(key, dict_[key]) for key in order]
  else:
    return sorted(dict_.items(), key=lambda e: e[0])


@ApplyToDataframe
def mutate(*args, **kwargs):
  """Adds a column to the DataFrame.

  This can use existing columns of the DataFrame as input.

  >>> (diamonds >> 
          mutate(carat_bin=X.carat.round()) >> 
          group_by(X.cut, X.carat_bin) >> 
          summarize(avg_price=X.price.mean()))
  Out:
         avg_price  carat_bin        cut
  0     863.908535          0      Ideal
  1    4213.864948          1      Ideal
  2   12838.984078          2      Ideal
  ...
  27  13466.823529          3       Fair
  28  15842.666667          4       Fair
  29  18018.000000          5       Fair
  """
  def addColumns(df):
    for arg in args:
      if isinstance(arg, Later):
        df[str(arg)] = arg.evaluate(df)
      else:
        df[str(arg)] = arg

    for key, val in _dict_to_possibly_ordered_tuples(kwargs):
      if type(val) == Later:
        df[key] = val.evaluate(df)
      else:
        df[key] = val
    return df
  return addColumns


@ApplyToDataframe
def group_by(*args, **kwargs):
  def GroupDF(df):
    group_columns = list(kwargs.keys())
    mutate_columns = kwargs
    for arg in args:
      if arg._name is not None:
        group_columns.append(arg._name)
      else:
        group_columns.append(str(arg))
        mutate_columns[str(arg)] = arg

    if mutate_columns:
      df = df >> mutate(**mutate_columns)
    df.group_self(group_columns)
    return df
  return GroupDF


@ApplyToDataframe
def summarize(**kwargs):
  def CreateSummarizedDf(df):
    input_dict = {k: val.evaluate(df) for k, val in six.iteritems(kwargs)}
    if len(input_dict) == 0:
      return DplyFrame({}, index=index)
    if hasattr(df, "_current_group") and df._current_group:
      input_dict.update(df._current_group)
    index = [0]
    return DplyFrame(input_dict, index=index)
  return CreateSummarizedDf


@ApplyToDataframe
def count(*args, **kwargs):
  def CreateCountDf(df):
    return (df >> group_by(*args, **kwargs) >>
                  summarize(n=X._.__len__()) >> ungroup())
  return CreateCountDf
  

def UngroupDF(df):
  # df._grouped_on = None
  # df._group_dict = None
  df.ungroup()
  return df


@ApplyToDataframe
def ungroup():
  return UngroupDF
  

@ApplyToDataframe
def arrange(*args):
  """Sort DataFrame by the input column arguments.

  >>> diamonds >> sample_n(5) >> arrange(X.price) >> select(X.depth, X.price)
  Out:
         depth  price
  28547   61.0    675
  35132   59.1    889
  42526   61.3   1323
  3468    61.6   3392
  23829   62.0  11903
  """
  names = [column._name for column in args]
  def f(df):
    sortby_df = df >> mutate(*args)
    index = sortby_df.sort_values([str(arg) for arg in args]).index
    return df.loc[index]
  return f


@ApplyToDataframe
def head(*args, **kwargs):
  """Returns first n rows"""
  return lambda df: df.head(*args, **kwargs)


@ApplyToDataframe
def sample_n(n):
  """Randomly sample n rows from the DataFrame"""
  return lambda df: DplyFrame(df.sample(n))


@ApplyToDataframe
def sample_frac(frac):
  """Randomly sample `frac` fraction of the DataFrame"""
  return lambda df: DplyFrame(df.sample(frac=frac))


@ApplyToDataframe
def sample(*args, **kwargs):
  """Convenience method that calls into pandas DataFrame's sample method"""
  return lambda df: df.sample(*args, **kwargs)


@ApplyToDataframe
def nrow():
  return lambda df: len(df)


@ApplyToDataframe
def rename(**kwargs):
  """Rename one or more columns, leaving other columns unchanged

  Example usage:
    diamonds >> rename(new_name=old_name)
  """
  def rename_columns(df):
    column_assignments = {old_name_later._name: new_name
                          for new_name, old_name_later in kwargs.items()}
    return df.rename(columns=column_assignments)
  return rename_columns


@ApplyToDataframe
def transmute(**kwargs):
  """ Similar to `select` but allows mutation in column definitions.

  In : (diamonds >>
          head(3) >>
          transmute(new_price=X.price * 2, x_plus_y=X.x + X.y))
  Out:
        new_price  x_plus_y
    0        652      7.93
    1        652      7.73
    2        654      8.12
  """
  mutate_dateframe_fn = mutate(**dict(kwargs))
  column_names = [name for name, _ in _dict_to_possibly_ordered_tuples(kwargs)]
  return lambda df: mutate_dateframe_fn(df)[column_names]


@DelayFunction
def PairwiseGreater(series1, series2):
  index = series1.index
  newSeries = pandas.Series([max(s1, s2) for s1, s2 in zip(series1, series2)])
  newSeries.index = index
  return newSeries


@DelayFunction
def if_else(bool_series, series_true, series_false):
  index = bool_series.index
  newSeries = pandas.Series([s1 if b else s2 for b, s1, s2
      in zip(bool_series, series_true, series_false)])
  newSeries.index = index
  return newSeries

def get_join_cols(by_entry):
  """ helper function used for joins
  builds left and right join list for djoin function
  """
  left_cols = []
  right_cols = []
  for col in by_entry:
    if isinstance(col, str):
      left_cols.append(col)
      right_cols.append(col)
    else:
      left_cols.append(col[0])
      right_cols.append(col[1])
  return left_cols, right_cols

def mutating_join(right, **kwargs):
  """ generic function for mutating dplyr-style joins
  uses dplyr syntax
  >>> left_data >> inner_join(right_data, by=[join_columns_in_list_as_single_or_tuple], suffixes=(character_tuple_of_length_2)
  e.g. flights2 >> left_join(airports, by=[('origin', 'faa')]) >> head(5)

  The by argument takes a list of columns. For a list like ['A', 'B'], it assumes 'A' and 'B' are columns in both
  dataframes.
  For a list like [('A', 'B')], it assumes column 'A' in the left dataframe is the same as column 'B' in the right dataframe.
  Can mix and match (e.g. by=['A', ('B', 'C')] will assume both dataframes have column 'A', and column 'B' in the left
  dataframe is the same as column 'C' in the right dataframe.
  If by is not specified, then all shared columns will be assumed to be the join columns.

  suffixes will be used to rename columns that are common to both dataframes, but not used in the join operation.
  e.g. suffixes=('_1', '_2').
  If suffixes is not included, then the pandas default will be used ('_x', '_y')

  Currently, only the 4 mutating joins are implemented (left, right, inner, outer/full)
  """
  # candidate for improvement
  if 'by' in kwargs:
    left_cols, right_cols = get_join_cols(kwargs['by'])
  else:
    left_cols, right_cols = None, None
  if 'suffixes' in kwargs:
    dsuffixes = kwargs['suffixes']
  else:
    dsuffixes = ('_x', '_y')
  def f(df):
    x = lambda df: DplyFrame(df.merge(right, how=kwargs['how'], left_on=left_cols, right_on=right_cols, suffixes=dsuffixes))
    return x
  return f

@ApplyToDataframe
def inner_join(right, **kwargs):
  return mutating_join(right, how='inner', **kwargs)

@ApplyToDataframe
def full_join(right, **kwargs):
  return mutating_join(right, how='outer', **kwargs)

@ApplyToDataframe
def left_join(right, **kwargs):
  return mutating_join(right, how='left', **kwargs)

@ApplyToDataframe
def right_join(right, **kwargs):
  return mutating_join(right, how='right', **kwargs)
