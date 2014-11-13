# -*- coding: UTF-8 -*-
import os
import operator

import yaml
from import_file import import_file
from werkzeug.utils import cached_property
import sqlalchemy
from flask.ext.babel import _

from flask.ext.report.utils import get_column_operator, get_primary_key


class DataSet(object):
    '''
    data set defines the source of data
    '''

    __TYPES__ = {
        "str": "text",
        "int": "number",
        "bool": "checkbox",
        "datetime": "datetime",
        "date": "date"
    }

    def __init__(self, report_view, id_):
        self.report_view = report_view
        self.id_ = id_
        data_set_meta_file = os.path.join(self.report_view.data_set_dir,
                                          str(id_), 'meta.yaml')
        data_set_meta = yaml.load(file(data_set_meta_file).read())
        self.name = data_set_meta['name']
        self.creator = data_set_meta.get('creator')
        self.create_time = data_set_meta.get('create_time')
        self.description = data_set_meta.get("description")
        self.default_report_name = data_set_meta.get("default_report_name", '')
        self.__special_chars = {"gt": operator.gt, "lt": operator.lt,
                                "ge": operator.ge, "le": operator.le,
                                "eq": operator.eq, "ne": operator.ne}
        self._filters = data_set_meta.get("filters", {})

    @cached_property
    def query(self):
        '''
        the query of data set
        '''
        query_def_file = os.path.join(self.report_view.data_set_dir,
                                      str(self.id_), "query_def.py")
        lib = import_file(query_def_file)
        return lib.get_query(self.report_view.db, self.report_view.model_map)

    @cached_property
    def columns(self):
        '''
        get the columns

        :return list: a list of column, each one is a dict, contains then
            following keys:

            * idx - the index of the column, start from 0
            * name - name of the column
            * key - key of the column, eg. column name defined in table
            * expr - the column definition in model

            for exampe, for query like:

                db.session.query(User.id, User.name.label('username'))

            and User.__tablename__ is 'TB_USER'

            the columns will be:

                [
                    {
                        idx: 0,
                        name: 'User.id',
                        key: 'TB_USER.id',
                        expr: User.id
                    },
                    {
                        idx: 1,
                        name: 'username',
                        key: 'TB_USER.name',
                        expr: User.name.label('username')
                    },
                ]
        '''
        def _make_dict(idx, c):
            if hasattr(c['expr'], 'element'):  # is label
                name = c['name'] or dict(name=str(c['expr']))
                key = str(c['expr'].element)
                if isinstance(c['expr'].element,
                              sqlalchemy.sql.expression.Function):
                    key = key.replace('"', '')
            else:
                name = str(c['expr'])
                key = c['expr'].table.name + "." + c['expr'].name

            return dict(idx=idx, name=name, key=key, expr=c['expr'])

        return tuple(_make_dict(idx, c) for idx, c in
                     enumerate(self.query.column_descriptions))

    def get_query(self, filters):
        # TODO what is this method for?

        def get_operator(op):
            return self.__special_chars[op]

        query = self.query

        for filter_ in filters:
            column, op_ = get_column_operator(filter_["col"],
                                              self.columns, self.report_view)
            if op_ == "filter":
                method_ = query.filter
            elif op_ == "having":
                method_ = query.having

            if hasattr(column, "property") and hasattr(column.property,
                                                       "direction"):
                column = column.property.local_remote_pairs[0][1]
            query = method_(get_operator(filter_["op"])(column, filter_["val"]))
        return query

    def _search_label(self, column):
        for c in self.columns:
            if c["key"] == str(column.expression) or \
                    c["expr"] == column:
                return c["name"]
        raise ValueError(_('There\'s no such column ' + str(column)))

    def _coerce_type(self, column):
        default = column.type.python_type
        return self.__TYPES__.get(default.__name__, 'text')

    @property
    def filters(self):
        '''
        a list filters
        '''

        filters = []

        for k, v in self._filters.items():
            column, op_ = get_column_operator(k, self.columns, self.report_view)

            result = {
                "name": v.get('name', self._search_label(column)),
                "col": k,
                "ops": v.get("operators"),
                'opts': [],
                'proxy': False
            }

            if hasattr(column, "property") and hasattr(column.property,
                                                       "direction"):
                def _iter_choices(column):
                    model = column.property.mapper.class_
                    pk = get_primary_key(model)
                    for row in self.report_view.db.session.query(model):
                        yield getattr(row, pk), unicode(row)

                result["opts"] = list(_iter_choices(column))
                result['type'] = 'select'
            else:
                result['type'] = v.get('type', self._coerce_type(column))
            filters.append(result)

        for k, f in self.synthetic_filter_map.items():
            filters.append({
                'name': f.name,
                'col': f.name,
                'ops': f.operators,
                'type': f.type,
                'opts': f.options,
                'proxy': True
            })
        return filters

    @property
    def synthetic_filter_map(self):
        '''
        a map of synthetic (user defined) filters, keys are filters'name, values
        are filters
        '''
        proxy_filter_file = os.path.join(self.dir, 'synthetic_filters.py')
        ret = {}
        if os.path.exists(proxy_filter_file):
            lib = import_file(proxy_filter_file)
            for filter_ in lib.__all__:
                ret[filter_.name] = filter_
        return ret

    @property
    def dir(self):
        '''
        the path of the directory where data set is defined
        '''
        return os.path.join(self.report_view.data_set_dir, str(self.id_))

    def get_current_filters(self, currents):
        # TODO what is this method for?
        def _match(to_matcher):
            result = to_matcher.copy()
            for filter in self.filters:
                if to_matcher["col"] == filter["col"]:
                    result.update(filter)
                    return result

        all = []
        for current in currents:
            filter_ = _match(current)
            if filter_:
                try:
                    filter_["val"] = int(filter_["val"])
                except ValueError:
                    pass
                all.append(filter_)
        return all
