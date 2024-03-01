from __future__ import unicode_literals
import six
import pytz
from copy import copy
from math import ceil
from datetime import date, datetime
from .utils import comma_join, is_iterable


# TODO
# - check that field names are valid
# - operators for arrays: length, has, empty

class Operator(object):
    """
    Base class for filtering operators.
    """

    def to_sql(self, model_cls, field_name, value):
        """
        Subclasses should implement this method. It returns an SQL string
        that applies this operator on the given field and value.
        """
        raise NotImplementedError   # pragma: no cover

    def _value_to_sql(self, field, value, quote=True):
        if isinstance(value, F):
            return value.to_sql()
        return field.to_db_string(field.to_python(value, pytz.utc), quote)


class SimpleOperator(Operator):
    """
    A simple binary operator such as a=b, a<b, a>b etc.
    """

    def __init__(self, sql_operator, sql_for_null=None):
        self._sql_operator = sql_operator
        self._sql_for_null = sql_for_null

    def to_sql(self, model_cls, field_name, value):
        field = getattr(model_cls, field_name)
        value = self._value_to_sql(field, value)
        if value == '\\N' and self._sql_for_null is not None:
            return ' '.join([field_name, self._sql_for_null])
        return ' '.join([field_name, self._sql_operator, value])


class InOperator(Operator):
    """
    An operator that implements IN.
    Accepts 3 different types of values:
    - a list or tuple of simple values
    - a string (used verbatim as the contents of the parenthesis)
    - a queryset (subquery)
    """

    def to_sql(self, model_cls, field_name, value):
        field = getattr(model_cls, field_name)
        if isinstance(value, QuerySet):
            value = value.as_sql()
        elif isinstance(value, six.string_types):
            pass
        else:
            value = comma_join([self._value_to_sql(field, v) for v in value])
        return '%s IN (%s)' % (field_name, value)


class LikeOperator(Operator):
    """
    A LIKE operator that matches the field to a given pattern. Can be
    case sensitive or insensitive.
    """

    def __init__(self, pattern, case_sensitive=True):
        self._pattern = pattern
        self._case_sensitive = case_sensitive

    def to_sql(self, model_cls, field_name, value):
        field = getattr(model_cls, field_name)
        value = self._value_to_sql(field, value, quote=False)
        value = value.replace('\\', '\\\\').replace('%', '\\\\%').replace('_', '\\\\_')
        pattern = self._pattern.format(value)
        if self._case_sensitive:
            return '%s LIKE \'%s\'' % (field_name, pattern)
        else:
            return 'lowerUTF8(%s) LIKE lowerUTF8(\'%s\')' % (field_name, pattern)


class IExactOperator(Operator):
    """
    An operator for case insensitive string comparison.
    """

    def to_sql(self, model_cls, field_name, value):
        field = getattr(model_cls, field_name)
        value = self._value_to_sql(field, value)
        return 'lowerUTF8(%s) = lowerUTF8(%s)' % (field_name, value)


class NotOperator(Operator):
    """
    A wrapper around another operator, which negates it.
    """

    def __init__(self, base_operator):
        self._base_operator = base_operator

    def to_sql(self, model_cls, field_name, value):
        # Negate the base operator
        return 'NOT (%s)' % self._base_operator.to_sql(model_cls, field_name, value)


class BetweenOperator(Operator):
    """
    An operator that implements BETWEEN.
    Accepts list or tuple of two elements and generates sql condition:
    - 'BETWEEN value[0] AND value[1]' if value[0] and value[1] are not None and not empty
    Then imitations of BETWEEN, where one of two limits is missing
    - '>= value[0]' if value[1] is None or empty
    - '<= value[1]' if value[0] is None or empty
    """

    def to_sql(self, model_cls, field_name, value):
        field = getattr(model_cls, field_name)
        value0 = self._value_to_sql(field, value[0]) if value[0] is not None or len(str(value[0])) > 0 else None
        value1 = self._value_to_sql(field, value[1]) if value[1] is not None or len(str(value[1])) > 0 else None
        if value0 and value1:
            return '%s BETWEEN %s AND %s' % (field_name, value0, value1)
        if value0 and not value1:
            return ' '.join([field_name, '>=', value0])
        if value1 and not value0:
            return ' '.join([field_name, '<=', value1])

# Define the set of builtin operators

_operators = {}

def register_operator(name, sql):
    _operators[name] = sql

register_operator('eq',          SimpleOperator('=', 'IS NULL'))
register_operator('ne',          SimpleOperator('!=', 'IS NOT NULL'))
register_operator('gt',          SimpleOperator('>'))
register_operator('gte',         SimpleOperator('>='))
register_operator('lt',          SimpleOperator('<'))
register_operator('lte',         SimpleOperator('<='))
register_operator('between',     BetweenOperator())
register_operator('in',          InOperator())
register_operator('not_in',      NotOperator(InOperator()))
register_operator('contains',    LikeOperator('%{}%'))
register_operator('startswith',  LikeOperator('{}%'))
register_operator('endswith',    LikeOperator('%{}'))
register_operator('icontains',   LikeOperator('%{}%', False))
register_operator('istartswith', LikeOperator('{}%', False))
register_operator('iendswith',   LikeOperator('%{}', False))
register_operator('iexact',      IExactOperator())


class Cond(object):
    """
    An abstract object for storing a single query condition Field + Operator + Value.
    """

    def to_sql(self, model_cls):
        raise NotImplementedError


class FieldCond(Cond):
    """
    A single query condition made up of Field + Operator + Value.
    """
    def __init__(self, field_name, operator, value):
        self._field_name = field_name
        self._operator = _operators.get(operator)
        if self._operator is None:
            # The field name contains __ like my__field
            self._field_name = field_name + '__' + operator
            self._operator = _operators['eq']
        self._value = value

    def to_sql(self, model_cls):
        return self._operator.to_sql(model_cls, self._field_name, self._value)


class F(Cond):
    """
    Represents a database function call and its arguments.
    It doubles as a query condition when the function returns a boolean result.
    """

    def __init__(self, name, *args):
        self.name = name
        self.args = args

    def to_sql(self, *args):
        args_sql = comma_join(self.arg_to_sql(arg) for arg in self.args)
        return self.name + '(' + args_sql + ')'

    def arg_to_sql(self, arg):
        from .fields import Field, StringField, DateTimeField, DateField
        if isinstance(arg, F):
            return arg.to_sql()
        if isinstance(arg, Field):
            return "`%s`" % arg.name
        if isinstance(arg, six.string_types):
            return StringField().to_db_string(arg)
        if isinstance(arg, datetime):
            return DateTimeField().to_db_string(arg)
        if isinstance(arg, date):
            return DateField().to_db_string(arg)
        if isinstance(arg, bool):
            return six.text_type(int(arg))
        if arg is None:
            return 'NULL'
        if is_iterable(arg):
            return '[' + comma_join(self.arg_to_sql(x) for x in arg) + ']'
        return six.text_type(arg)

    # Support comparison operators with F objects

    def __lt__(self, other):
        return F.less(self, other)

    def __le__(self, other):
        return F.lessOrEquals(self, other)

    def __eq__(self, other):
        return F.equals(self, other)

    def __ne__(self, other):
        return F.notEquals(self, other)

    def __gt__(self, other):
        return F.greater(self, other)

    def __ge__(self, other):
        return F.greaterOrEquals(self, other)

    # Support arithmetic operations on F objects

    def __add__(self, other):
        return F.plus(self, other)

    def __radd__(self, other):
        return F.plus(other, self)

    def __sub__(self, other):
        return F.minus(self, other)

    def __rsub__(self, other):
        return F.minus(other, self)

    def __mul__(self, other):
        return F.multiply(self, other)

    def __rmul__(self, other):
        return F.multiply(other, self)

    def __div__(self, other):
        return F.divide(self, other)

    def __rdiv__(self, other):
        return F.divide(other, self)

    def __mod__(self, other):
        return F.modulo(self, other)

    def __rmod__(self, other):
        return F.modulo(other, self)

    def __neg__(self):
        return F.negate(self)

    def __pos__(self):
        return self

    # Arithmetic functions

    @staticmethod
    def plus(a, b):
        return F('plus', a, b)

    @staticmethod
    def minus(a, b):
        return F('minus', a, b)

    @staticmethod
    def multiply(a, b):
        return F('multiply', a, b)

    @staticmethod
    def divide(a, b):
        return F('divide', a, b)

    @staticmethod
    def intDiv(a, b):
        return F('intDiv', a, b)

    @staticmethod
    def intDivOrZero(a, b):
        return F('intDivOrZero', a, b)

    @staticmethod
    def modulo(a, b):
        return F('modulo', a, b)

    @staticmethod
    def negate(a):
        return F('negate', a)

    @staticmethod
    def abs(a):
        return F('abs', a)

    @staticmethod
    def gcd(a, b):
        return F('gcd',a, b)

    @staticmethod
    def lcm(a, b):
        return F('lcm', a, b)

    # Comparison functions

    @staticmethod
    def equals(a, b):
        return F('equals', a, b)

    @staticmethod
    def notEquals(a, b):
        return F('notEquals', a, b)

    @staticmethod
    def less(a, b):
        return F('less', a, b)

    @staticmethod
    def greater(a, b):
        return F('greater', a, b)

    @staticmethod
    def lessOrEquals(a, b):
        return F('lessOrEquals', a, b)

    @staticmethod
    def greaterOrEquals(a, b):
        return F('greaterOrEquals', a, b)

    # Functions for working with dates and times

    @staticmethod
    def toYear(d):
        return F('toYear', d)

    @staticmethod
    def toMonth(d):
        return F('toMonth', d)

    @staticmethod
    def toDayOfMonth(d):
        return F('toDayOfMonth', d)

    @staticmethod
    def toDayOfWeek(d):
        return F('toDayOfWeek', d)

    @staticmethod
    def toHour(d):
        return F('toHour', d)

    @staticmethod
    def toMinute(d):
        return F('toMinute', d)

    @staticmethod
    def toSecond(d):
        return F('toSecond', d)

    @staticmethod
    def toMonday(d):
        return F('toMonday', d)

    @staticmethod
    def toStartOfMonth(d):
        return F('toStartOfMonth', d)

    @staticmethod
    def toStartOfQuarter(d):
        return F('toStartOfQuarter', d)

    @staticmethod
    def toStartOfYear(d):
        return F('toStartOfYear', d)

    @staticmethod
    def toStartOfMinute(d):
        return F('toStartOfMinute', d)

    @staticmethod
    def toStartOfFiveMinute(d):
        return F('toStartOfFiveMinute', d)

    @staticmethod
    def toStartOfFifteenMinutes(d):
        return F('toStartOfFifteenMinutes', d)

    @staticmethod
    def toStartOfHour(d):
        return F('toStartOfHour', d)

    @staticmethod
    def toStartOfDay(d):
        return F('toStartOfDay', d)

    @staticmethod
    def toTime(d):
        return F('toTime', d)

    @staticmethod
    def toRelativeYearNum(d, timezone=''):
        return F('toRelativeYearNum', d, timezone)

    @staticmethod
    def toRelativeMonthNum(d, timezone=''):
        return F('toRelativeMonthNum', d, timezone)

    @staticmethod
    def toRelativeWeekNum(d, timezone=''):
        return F('toRelativeWeekNum', d, timezone)

    @staticmethod
    def toRelativeDayNum(d, timezone=''):
        return F('toRelativeDayNum', d, timezone)

    @staticmethod
    def toRelativeHourNum(d, timezone=''):
        return F('toRelativeHourNum', d, timezone)

    @staticmethod
    def toRelativeMinuteNum(d, timezone=''):
        return F('toRelativeMinuteNum', d, timezone)

    @staticmethod
    def toRelativeSecondNum(d, timezone=''):
        return F('toRelativeSecondNum', d, timezone)

    @staticmethod
    def now():
        return F('now')

    @staticmethod
    def today():
        return F('today')

    @staticmethod
    def yesterday(d):
        return F('yesterday')

    @staticmethod
    def timeSlot(d):
        return F('timeSlot', d)

    @staticmethod
    def timeSlots(start_time, duration):
        return F('timeSlots', start_time, duration)

    @staticmethod
    def formatDateTime(d, format, timezone=''):
        return F('formatDateTime', d, format, timezone)


class Q(object):

    AND_MODE = ' AND '
    OR_MODE = ' OR '

    def __init__(self, *filter_funcs, **filter_fields):
        self._conds = list(filter_funcs) + [self._build_cond(k, v) for k, v in six.iteritems(filter_fields)]
        self._l_child = None
        self._r_child = None
        self._negate = False
        self._mode = self.AND_MODE

    @classmethod
    def _construct_from(cls, l_child, r_child, mode):
        q = Q()
        q._l_child = l_child
        q._r_child = r_child
        q._mode = mode # AND/OR
        return q

    def _build_cond(self, key, value):
        if '__' in key:
            field_name, operator = key.rsplit('__', 1)
        else:
            field_name, operator = key, 'eq'
        return FieldCond(field_name, operator, value)

    def to_sql(self, model_cls):
        if self._conds:
            sql = self._mode.join(cond.to_sql(model_cls) for cond in self._conds)
        else:
            if self._l_child and self._r_child:
                sql = '({} {} {})'.format(
                        self._l_child.to_sql(model_cls), self._mode, self._r_child.to_sql(model_cls))
            else:
                return '1'
        if self._negate:
            sql = 'NOT (%s)' % sql
        return sql

    def __or__(self, other):
        return Q._construct_from(self, other, self.OR_MODE)

    def __and__(self, other):
        return Q._construct_from(self, other, self.AND_MODE)

    def __invert__(self):
        q = copy(self)
        q._negate = True
        return q


@six.python_2_unicode_compatible
class QuerySet(object):
    """
    A queryset is an object that represents a database query using a specific `Model`.
    It is lazy, meaning that it does not hit the database until you iterate over its
    matching rows (model instances).
    """

    def __init__(self, model_cls, database):
        """
        Initializer. It is possible to create a queryset like this, but the standard
        way is to use `MyModel.objects_in(database)`.
        """
        self._model_cls = model_cls
        self._database = database
        self._order_by = []
        self._q = []
        self._fields = model_cls.fields().keys()
        self._limits = None
        self._distinct = False

    def __iter__(self):
        """
        Iterates over the model instances matching this queryset
        """
        return self._database.select(self.as_sql(), self._model_cls)

    def __bool__(self):
        """
        Returns true if this queryset matches any rows.
        """
        return bool(self.count())

    def __nonzero__(self):      # Python 2 compatibility
        return type(self).__bool__(self)

    def __str__(self):
        return self.as_sql()

    def __getitem__(self, s):
        if isinstance(s, six.integer_types):
            # Single index
            assert s >= 0, 'negative indexes are not supported'
            qs = copy(self)
            qs._limits = (s, 1)
            return six.next(iter(qs))
        else:
            # Slice
            assert s.step in (None, 1), 'step is not supported in slices'
            start = s.start or 0
            stop = s.stop or 2**63 - 1
            assert start >= 0 and stop >= 0, 'negative indexes are not supported'
            assert start <= stop, 'start of slice cannot be smaller than its end'
            qs = copy(self)
            qs._limits = (start, stop - start)
            return qs

    def as_sql(self):
        """
        Returns the whole query as a SQL string.
        """
        distinct = 'DISTINCT ' if self._distinct else ''
        fields = '*'
        if self._fields:
            fields = comma_join('`%s`' % field for field in self._fields)
        ordering = '\nORDER BY ' + self.order_by_as_sql() if self._order_by else ''
        limit = '\nLIMIT %d, %d' % self._limits if self._limits else ''
        params = (distinct, fields, self._model_cls.table_name(),
                  self.conditions_as_sql(), ordering, limit)
        return u'SELECT %s%s\nFROM `%s`\nWHERE %s%s%s' % params

    def order_by_as_sql(self):
        """
        Returns the contents of the query's `ORDER BY` clause as a string.
        """
        return comma_join([
            '%s DESC' % field[1:] if field[0] == '-' else field
            for field in self._order_by
        ])

    def conditions_as_sql(self):
        """
        Returns the contents of the query's `WHERE` clause as a string.
        """
        if self._q:
            return u' AND '.join([q.to_sql(self._model_cls) for q in self._q])
        else:
            return u'1'

    def count(self):
        """
        Returns the number of matching model instances.
        """
        if self._distinct or self._limits:
            # Use a subquery, since a simple count won't be accurate
            sql = u'SELECT count() FROM (%s)' % self.as_sql()
            raw = self._database.raw(sql)
            return int(raw) if raw else 0
        # Simple case
        return self._database.count(self._model_cls, self.conditions_as_sql())

    def order_by(self, *field_names):
        """
        Returns a copy of this queryset with the ordering changed.
        """
        qs = copy(self)
        qs._order_by = field_names
        return qs

    def only(self, *field_names):
        """
        Returns a copy of this queryset limited to the specified field names.
        Useful when there are large fields that are not needed,
        or for creating a subquery to use with an IN operator.
        """
        qs = copy(self)
        qs._fields = field_names
        return qs

    def filter(self, *q, **filter_fields):
        """
        Returns a copy of this queryset that includes only rows matching the conditions.
        Add q object to query if it specified.
        """
        qs = copy(self)
        qs._q = list(self._q)
        for arg in q:
            if isinstance(arg, Q):
                qs._q.append(arg)
            elif isinstance(arg, F):
                qs._q.append(Q(arg))
            else:
                raise TypeError('Invalid argument "%r" to queryset filter' % arg)
        if filter_fields:
            qs._q += [Q(**filter_fields)]
        return qs

    def exclude(self, **filter_fields):
        """
        Returns a copy of this queryset that excludes all rows matching the conditions.
        """
        qs = copy(self)
        qs._q = list(self._q) + [~Q(**filter_fields)]
        return qs

    def paginate(self, page_num=1, page_size=100):
        """
        Returns a single page of model instances that match the queryset.
        Note that `order_by` should be used first, to ensure a correct
        partitioning of records into pages.

        - `page_num`: the page number (1-based), or -1 to get the last page.
        - `page_size`: number of records to return per page.

        The result is a namedtuple containing `objects` (list), `number_of_objects`,
        `pages_total`, `number` (of the current page), and `page_size`.
        """
        from .database import Page
        count = self.count()
        pages_total = int(ceil(count / float(page_size)))
        if page_num == -1:
            page_num = pages_total
        elif page_num < 1:
            raise ValueError('Invalid page number: %d' % page_num)
        offset = (page_num - 1) * page_size
        return Page(
            objects=list(self[offset : offset + page_size]),
            number_of_objects=count,
            pages_total=pages_total,
            number=page_num,
            page_size=page_size
        )

    def distinct(self):
        """
        Adds a DISTINCT clause to the query, meaning that any duplicate rows
        in the results will be omitted.
        """
        qs = copy(self)
        qs._distinct = True
        return qs

    def aggregate(self, *args, **kwargs):
        """
        Returns an `AggregateQuerySet` over this query, with `args` serving as
        grouping fields and `kwargs` serving as calculated fields. At least one
        calculated field is required. For example:
        ```
            Event.objects_in(database).filter(date__gt='2017-08-01').aggregate('event_type', count='count()')
        ```
        is equivalent to:
        ```
            SELECT event_type, count() AS count FROM event
            WHERE data > '2017-08-01'
            GROUP BY event_type
        ```
        """
        return AggregateQuerySet(self, args, kwargs)


class AggregateQuerySet(QuerySet):
    """
    A queryset used for aggregation.
    """

    def __init__(self, base_qs, grouping_fields, calculated_fields):
        """
        Initializer. Normally you should not call this but rather use `QuerySet.aggregate()`.

        The grouping fields should be a list/tuple of field names from the model. For example:
        ```
            ('event_type', 'event_subtype')
        ```
        The calculated fields should be a mapping from name to a ClickHouse aggregation function. For example:
        ```
            {'weekday': 'toDayOfWeek(event_date)', 'number_of_events': 'count()'}
        ```
        At least one calculated field is required.
        """
        super(AggregateQuerySet, self).__init__(base_qs._model_cls, base_qs._database)
        assert calculated_fields, 'No calculated fields specified for aggregation'
        self._fields = grouping_fields
        self._grouping_fields = grouping_fields
        self._calculated_fields = calculated_fields
        self._order_by = list(base_qs._order_by)
        self._q = list(base_qs._q)
        self._limits = base_qs._limits
        self._distinct = base_qs._distinct

    def group_by(self, *args):
        """
        This method lets you specify the grouping fields explicitly. The `args` must
        be names of grouping fields or calculated fields that this queryset was
        created with.
        """
        for name in args:
            assert name in self._fields or name in self._calculated_fields, \
                   'Cannot group by `%s` since it is not included in the query' % name
        qs = copy(self)
        qs._grouping_fields = args
        return qs

    def only(self, *field_names):
        """
        This method is not supported on `AggregateQuerySet`.
        """
        raise NotImplementedError('Cannot use "only" with AggregateQuerySet')

    def aggregate(self, *args, **kwargs):
        """
        This method is not supported on `AggregateQuerySet`.
        """
        raise NotImplementedError('Cannot re-aggregate an AggregateQuerySet')

    def as_sql(self):
        """
        Returns the whole query as a SQL string.
        """
        distinct = 'DISTINCT ' if self._distinct else ''
        grouping = comma_join('`%s`' % field for field in self._grouping_fields)
        fields = comma_join(list(self._fields) + ['%s AS %s' % (v, k) for k, v in self._calculated_fields.items()])
        params = dict(
            distinct=distinct,
            grouping=grouping or "''",
            fields=fields,
            table=self._model_cls.table_name(),
            conds=self.conditions_as_sql()
        )
        sql = u'SELECT %(distinct)s%(fields)s\nFROM `%(table)s`\nWHERE %(conds)s\nGROUP BY %(grouping)s' % params
        if self._order_by:
            sql += '\nORDER BY ' + self.order_by_as_sql()
        if self._limits:
            sql += '\nLIMIT %d, %d' % self._limits
        return sql

    def __iter__(self):
        return self._database.select(self.as_sql()) # using an ad-hoc model

    def count(self):
        """
        Returns the number of rows after aggregation.
        """
        sql = u'SELECT count() FROM (%s)' % self.as_sql()
        raw = self._database.raw(sql)
        return int(raw) if raw else 0


