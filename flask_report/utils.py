# -*- coding: UTF-8 -*-
import os
import re

import yaml
import sqlalchemy
import operator
from flask.ext.babel import _

AGGREGATE_FUNC = ["sum", "avg", "max", "min", "count"]


def collect_models(module):
    '''
    collect all database models from a module

    :param module module: the module to be searched
    :return list: a list of models defined in given module
    '''
    return [v for v in module.__dict__.values() if
            hasattr(v, '_sa_class_manager')]


def get_primary_key(model):
    """
    get primary key name from a model

    :param model: model class or table
    """
    from sqlalchemy.schema import Table

    if isinstance(model, Table):
        for idx, c in enumerate(model.columns):
            if c.primary_key:
                return c.key
    else:
        props = model._sa_class_manager.mapper.iterate_properties

        for p in props:
            if hasattr(p, 'columns'):
                for c in p.columns:
                    if c.primary_key:
                        return p.key

    return None


def get_column_operated(func):
    # TODO missing doc
    ret = func
    while not isinstance(ret, sqlalchemy.schema.Column):
        if isinstance(ret, sqlalchemy.sql.expression.ColumnClause):  # sub query
            ret = list(enumerate(ret.base_columns))[0][1]
        if isinstance(ret, sqlalchemy.sql.expression.BinaryExpression):
            if hasattr(ret.left, "table"):
                ret = ret.left
            elif hasattr(ret.right, "table"):
                ret = ret.right
        else:
            ret = ret.clauses.clauses[0]
    return ret


def query_to_sql(statement, bind=None):
    """
    print a query, with values filled in
    for debugging purposes *only*
    for security, you should always separate queries from their values
    please also note that this function is quite slow
    """
    if not statement:
        return ""
    import sqlalchemy.orm

    if isinstance(statement, sqlalchemy.orm.Query):
        if bind is None:
            bind = statement.session.get_bind(
                statement._mapper_zero_or_none()
            )
        statement = statement.statement
    elif bind is None:
        bind = statement.bind

    dialect = bind.dialect
    compiler = statement._compiler(dialect)

    class LiteralCompiler(compiler.__class__):
        def visit_bindparam(
                self, bindparam, within_columns_clause=False,
                literal_binds=False, **kwargs
        ):
            return super(LiteralCompiler, self).render_literal_bindparam(
                bindparam, within_columns_clause=within_columns_clause,
                literal_binds=literal_binds, **kwargs
            )

        def render_literal_value(self, value, type_):

            if isinstance(type_, sqlalchemy.types.DateTime) or \
                    isinstance(type_, sqlalchemy.types.Date):
                return '"' + unicode(value) + '"'
            elif isinstance(value, str):
                value = value.decode(dialect.encoding)
            return super(LiteralCompiler, self).render_literal_value(value,
                                                                     type_)

    compiler = LiteralCompiler(dialect, statement)
    import sqlparse

    return sqlparse.format(compiler.process(statement), reindent=True,
                           keyword_case='upper')


def get_color(idx, colors, total_length=None, rgb=True):
    try:
        return colors[idx]
    except (IndexError, TypeError):
        def _get_color(idx, length):
            from flask.ext.report.colors import COLORS

            r = int(len(COLORS) * (idx + 1) / (length + 1))
            color = COLORS.values()[r]
            if rgb:
                return color
            else:
                return ('rgba(%s, %s, %s, 0.5)' % (int(color[1:3], 16),
                                                   int(color[3:5], 16),
                                                   int(color[5:7], 16)),
                        'rgba(%s, %s, %s, 1)' % (int(color[1:3], 16),
                                                 int(color[3:5], 16),
                                                 int(color[5:7], 16)))

        return _get_color(idx, total_length)


def dump_to_yaml(obj):
    import yaml

    if obj:
        result = yaml.safe_dump(obj, allow_unicode=True).decode("utf-8")
        if result[-5:] == "\n...\n":
            result = result[:-5]
    else:
        result = ''
    return result


def get_column(filter_key, columns, flask_report):
    # TODO missing documents

    col = None
    try:
        if "(" not in filter_key and ")" not in filter_key:
            model_name, column_name = filter_key.split(".")
            col = operator.attrgetter(column_name)(
                flask_report.model_map[model_name])
        else:
            model_name, column_name = re.split("[()]", filter_key)[1].split(".")
            model = flask_report.model_map[model_name]
            filter_key = filter_key.replace(model_name,
                                            model.__table__.name)
            for c in columns:
                if filter_key == c["key"]:
                    col = c["expr"]
                    break
    except ValueError:
        for c in columns:
            if filter_key == c["name"]:
                if "(" not in c["key"] and ")" not in c["key"]:
                    model_name, column_name = c["key"].split(".")
                    model = flask_report.model_map[model_name]
                    col = operator.attrgetter(column_name)(model)
                else:
                    col = c["expr"]
                break
    finally:
        if col is None:
            raise ValueError(_("No Such Column"))
        else:
            return col


def is_sql_function(col):
    return isinstance(col, sqlalchemy.sql.functions.GenericFunction)

def dump_yaml(path, **kwargs):
    '''
    write into a file using yaml format
    '''
    if os.path.isfile(path):
        try:
            os.unlink(path+"~")
        except OSError:
            pass
        os.rename(path, path+"~")
    with open(path, 'w') as f:
        yaml.safe_dump(kwargs, allow_unicode=True, stream=f)
