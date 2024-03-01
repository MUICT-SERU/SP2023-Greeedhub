# -*- coding: utf-8 -*-

from collections import OrderedDict
import inspect
import logging
from json import dumps

from querystring_parser.parser import parse

from django.conf import settings
from django.db.models import Q
from django.utils import six
from django.utils.safestring import mark_safe

from .column import *
from .mixins import JSONResponseView

logger = logging.getLogger(__name__)



class AttrDict(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class DeclarativeFieldsMetaclass(type):
    """
    Metaclass that collects Fields declared on the base classes.
    """
    _meta = AttrDict()

    def __new__(mcs, name, bases, attrs):


        attr_meta = attrs.pop('Meta', None)

        # Collect fields from current class.
        current_columns = []
        for key, value in list(attrs.items()):
            if isinstance(value, Column):
                current_columns.append((key, value))
                attrs.pop(key)
        current_columns.sort(key=lambda x: x[1].creation_counter)
        attrs['declared_fields'] = OrderedDict(current_columns)

        new_class = (super(DeclarativeFieldsMetaclass, mcs)
            .__new__(mcs, name, bases, attrs))

        if not attr_meta:
            meta = getattr(new_class, 'Meta', None)
        else:
            meta = attr_meta

        base_meta = getattr(new_class, '_meta', None)

        if meta:
            for key, value in meta.__dict__.items():
                setattr(base_meta, key, value)

            new_class.add_to_class('_meta', base_meta)


        # Walk through the MRO.
        declared_fields = OrderedDict()
        for base in reversed(new_class.__mro__):
            # Collect fields from base class.
            if hasattr(base, 'declared_fields'):
                declared_fields.update(base.declared_fields)

            # Field shadowing.
            for attr, value in base.__dict__.items():
                if value is None and attr in declared_fields:
                    declared_fields.pop(attr)

        new_class.base_fields = declared_fields
        new_class.declared_fields = declared_fields

        return new_class


    def add_to_class(cls, name, value):
        # We should call the contribute_to_class method only if it's bound
        if not inspect.isclass(value) and hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)


class DatatableBase(six.with_metaclass(DeclarativeFieldsMetaclass)):
    """ JSON data for datatables
    """

    class Meta:
        order_columns = []
        max_display_length = 100  # max limit of records returned, do not allow to kill our server by huge sets of data


    @property
    def _querydict(self):
        if self.request.method == 'POST':
            return self.request.POST
        else:
            return parse(self.request.META.get('QUERY_STRING'))

    def get_column_titles(self):
        """ Return list of column titles for the template engine
        """
        titles = []
        for key, column in self.declared_fields.items():
            titles.append(getattr(column, 'title', key.replace("_", " ").title()))
        return titles


    def get_column_by_index(self, index):
        """
        Returns the column key at a specified index
        """
        keys = self.declared_fields.keys()
        return keys[index]


    def get_index_by_key(self, key):
        """
        Returns the column index for a provided key
        """
        keys = self.declared_fields.keys()
        return keys.index(key)

    def render_columns(self, rows):
        """ Renders a column on a row
        """

        keys = self.declared_fields.keys()

        # Make rows writable
        rows = [list(row) for row in rows]

        # Call the render_column method for each field
        for i, key in enumerate(keys):
            column = self.declared_fields[key]
            for row in rows:
                row[i] = column.render_column(row[i])

            # Call the render_{} method for each column in local class
            method_name = "render_{}".format(key)
            if hasattr(self, method_name):
                method = getattr(self, method_name)
                if callable(method):
                    for row in rows:
                        row[i] = method(row[i])


        return rows


    def ordering(self, qs):
        """
        Get parameters from the request and prepare order by clause
        """
        order = list()

        sorting_cols = self._querydict.get('order', {})
        for i, info in sorting_cols.items():
            column_index = int(info['column'])
            sort_dir = '-' if info['dir'] == 'desc' else ''
            column = self.get_column_by_index(column_index)
            order.append('{0}{1}'.format(sort_dir, column))

        if order:
            return qs.order_by(*order)
        return qs

    def paging(self, qs):
        """ Paging
        """
        limit = min(int(self._querydict.get('length', 10)), self._meta.max_display_length)
        start = int(self._querydict.get('start', 0))

        # if pagination is disabled ("paging": false)
        if limit == -1:
            return qs

        offset = start + limit

        return qs[start:offset]

    def get_initial_queryset(self):
        if not self._meta.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return self._meta.model.objects.all()

    def extract_datatables_column_data(self):
        """ Helper method to extract columns data from request as passed by Datatables 1.10+
        """
        request_dict = self._querydict
        col_data = []
        counter = 0
        data_name_key = 'columns[{0}][name]'.format(counter)
        while data_name_key in request_dict:
            searchable = True if request_dict.get('columns[{0}][searchable]'.format(counter)) == 'true' else False
            orderable = True if request_dict.get('columns[{0}][orderable]'.format(counter)) == 'true' else False

            col_data.append({'name': request_dict.get(data_name_key),
                             'data': request_dict.get('columns[{0}][data]'.format(counter)),
                             'searchable': searchable,
                             'orderable': orderable,
                             'search.value': request_dict.get('columns[{0}][search][value]'.format(counter)),
                             'search.regex': request_dict.get('columns[{0}][search][regex]'.format(counter)),
                             })
            counter += 1
            data_name_key = 'columns[{0}][name]'.format(counter)
        return col_data

    def filter_queryset(self, qs):
        """ If search['value'] is provided then filter all searchable columns using istartswith
        """
        # get global search value
        search = self.request.GET.get('search[value]', None)
        col_data = self.extract_datatables_column_data()
        q = Q()
        for col_no, col in enumerate(col_data):
            # apply global search to all searchable columns
            if search and col['searchable']:
                q |= Q(**{'{0}__istartswith'.format(self.declared_fields[col_no].replace('.', '__')): search})

            # column specific filter
            if col['search.value']:
                qs = qs.filter(**{'{0}__istartswith'.format(self.declared_fields[col_no].replace('.', '__')): col['search.value']})
        qs = qs.filter(q)
        return qs

    def get_values_list(self):
        """
        Returns a list of the values to retrieve for a values list
        """
        return [getattr(column, "value", key) for key, column in self.declared_fields.items()]

    def prepare_results(self, qs):
        data = []
        values_list = qs.values_list(*self.get_values_list())
        values_list = self.render_columns(values_list)
        for row in values_list:
            data.append(row)
        return data

    def get_context_data(self, *args, **kwargs):
        try:

            qs = self.get_initial_queryset()

            # number of records before filtering
            total_records = qs.count()

            qs = self.filter_queryset(qs)

            # number of records after filtering
            total_display_records = qs.count()

            qs = self.ordering(qs)
            qs = self.paging(qs)

            # prepare output data
            data = self.prepare_results(qs)

            ret = {'draw': int(self._querydict.get('draw', 0)),
                   'recordsTotal': total_records,
                   'recordsFiltered': total_display_records,
                   'data': data
            }
        except Exception as e:
            logger.exception(str(e))

            if settings.DEBUG:
                import sys
                from django.views.debug import ExceptionReporter
                reporter = ExceptionReporter(None, *sys.exc_info())
                text = "\n" + reporter.get_traceback_text()
            else:
                text = "\nAn error occured while processing an AJAX request."

            ret = {'error': text,
                   'data': [],
                   'recordsTotal': 0,
                   'recordsFiltered': 0,
                   'draw': int(self._querydict.get('draw', 0))}
        return ret


from django.template import Context
from django.template.loader import select_template

class Datatable(DatatableBase, JSONResponseView):

    def datatable_config(self):
        config = dict(
            columns=list()
        )

        # Column config
        for key, column in self.declared_fields.items():
            column_config = dict()
            if key not in self._meta.order_columns:
                column_config['orderable'] = False
            config['columns'].append(column_config)

        # Ordering
        config['order'] = []
        if hasattr(self._meta, "initial_order"):
            for order_col in self._meta.initial_order:
                order_dir = 'asc'
                if order_col.startswith('-'):
                    order_col = order_col[1:]
                    order_dir = 'desc'
                order_index = self.get_index_by_key(order_col)
                config['order'].append([order_index, order_dir])
        return mark_safe(dumps(config))

    def render(self):
        template = select_template(['django_datatables/table.html'])
        context = Context({
            "datatable": self,
        })
        template_content = template.render(context)
        return mark_safe(template_content)
