import types
from flask import request
import json
from StringIO import StringIO
import csv
import time

from wtforms import (Form, TextField, validators, IntegerField,
                     SelectMultipleField)
from flask import render_template, jsonify, url_for, Response
from pygments import highlight
from pygments.lexers import PythonLexer, SqlLexer
from pygments.formatters import HtmlFormatter

from flask.ext.report.report import Report, create_report
from flask.ext.report.data_set import DataSet
from flask.ext.report.utils import query_to_sql, get_column_operated


def report_list(flask_report):
    flask_report.try_view_report()
    # directory 0 is reserved for special purpose
    reports = flask_report._get_report_list()
    params = dict(reports=reports)
    extra_params = flask_report.extra_params.get('report-list')
    if extra_params:
        if isinstance(extra_params, types.FunctionType):
            extra_params = extra_params()
        params.update(extra_params)
    return render_template('report____/report-list.html', **params)


class _ReportForm(Form):
    def __init__(self, report_view, data):
        self.report_view = report_view
        super(_ReportForm, self).__init__(data)

    def validate_data_set_id(self, e):
        try:
            self.data_set = DataSet(self.report_view, e.data)
            self.columns.choices = [(str(c['idx']), c['name']) for c in
                                    self.data_set.columns]
        except OSError:
            raise validators.ValidationError('invalid dataset')

    name = TextField('name', [validators.Required()])
    creator = TextField('createor')
    description = TextField('description')
    data_set_id = IntegerField('data_set_id', [validators.Required()])
    columns = SelectMultipleField('columns',
                                  [validators.Required()], choices=[])
    filters = TextField('filters')


def new_report(flask_report):
    form = _ReportForm(flask_report, request.form)

    if form.validate():
        def parse_filters(filters):
            result = {}
            for current in filters:
                if current["col"] not in result:
                    result[current["col"]] = {'operator': current["op"],
                                              'value': current["val"],
                                              'proxy': current['proxy']}
                else:
                    val = result[current["col"]]
                    if not isinstance(val, list):
                        val = [val]
                    val.append({'operator': current["op"],
                                'value': current["val"],
                                'proxy': current['proxy']})
                    result[current["col"]] = val
            return result

        name = form.name.data
        id = None
        if request.args.get('preview'):
            name += '(' + _('Preview') + ')'
            id = 0
        report_id = create_report(form.data_set, name=name,
                                  creator=form.creator.data,
                                  description=form.description.data,
                                  id=id, columns=form.columns.data,
                                  filters=parse_filters(
                                      json.loads(form.filters.data)))
        return jsonify({'id': report_id, 'name': form.name.data,
                        'url': url_for('.report', id_=report_id)})
    else:
        return jsonify({'errors': form.errors}), 403


def report(flask_report, id_=None):
    flask_report.try_view_report()
    if id_ is not None:
        report = Report(flask_report, id_)

        code = report.read_literal_filter_condition()

        SQL_html = highlight(query_to_sql(report.query), SqlLexer(),
                             HtmlFormatter())
        params = dict(report=report, SQL=SQL_html)
        if code is not None:
            customized_filter_condition = highlight(code, PythonLexer(),
                                                    HtmlFormatter())
            params['customized_filter_condition'] = \
                customized_filter_condition
        extra_params = flask_report.extra_params.get("report")
        if extra_params:
            if isinstance(extra_params, types.FunctionType):
                extra_params = extra_params(id_)
            params.update(extra_params)
        return report.html_template.render(**params)


def report_csv(flask_report, id_):
    report = Report(flask_report, id_)

    si = StringIO()
    writer = csv.writer(si, delimiter=',')
    writer.writerow([col['name'].encode('utf-8') for col in report.columns])
    col_id_list = [col['idx'] for col in report.columns]
    for row in report.data:
        row = [row[i].encode('utf-8') if isinstance(row[i], unicode) else
               row[i] for i in col_id_list]
        writer.writerow(row)

    rsp = Response(si.getvalue(), mimetype="text/csv")
    filename = report.name.encode('utf-8') + time.strftime('.%Y%m%d%H%M%S.csv')
    rsp.headers["Content-disposition"] = "attachment; filename=" + filename
    return rsp


def drill_down_detail(flask_report, report_id, col_id):
    filters = request.args
    report = Report(flask_report, report_id)
    col = report.data_set.columns[col_id]['expr']
    col = get_column_operated(getattr(col, 'element', col))
    model_name = flask_report.get_model_label(col.table)
    items = report.get_drill_down_detail(col_id, **filters)
    return report.get_drill_down_detail_template(
        col_id).render(items=items, key=col.key, model_name=model_name,
                       report=report)
