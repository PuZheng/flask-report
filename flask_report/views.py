import os
from flask import request
import json
from StringIO import StringIO
import csv
import time

from wtforms import (Form, TextField, validators, IntegerField,
                     SelectMultipleField)
from flask import render_template, jsonify, url_for, Response, flash, redirect
from pygments import highlight
from pygments.lexers import PythonLexer, SqlLexer
from pygments.formatters import HtmlFormatter
from flask.ext.mail import Message

from flask.ext.report.report import Report, create_report
from flask.ext.report.data_set import DataSet
from flask.ext.report.utils import query_to_sql, get_column_operated, dump_yaml
from flask.ext.report.notification import Notification


def report_list(flask_report):
    flask_report.try_view_report()
    # directory 0 is reserved for special purpose
    reports = flask_report.report_list
    params = dict(reports=reports)
    extra_params = flask_report.report_list_template_param(reports)
    if extra_params:
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


def report(flask_report, id_=None):
    flask_report.try_view_report()
    if id_ is not None:
        report = Report(flask_report, id_)

        code = report.raw_filter_condition

        SQL_html = highlight(query_to_sql(report.query), SqlLexer(),
                             HtmlFormatter())
        params = dict(report=report, SQL=SQL_html)
        if code is not None:
            customized_filter_condition = highlight(code, PythonLexer(),
                                                    HtmlFormatter())
            params['customized_filter_condition'] = \
                customized_filter_condition
        extra_params = flask_report.report_template_param(report)
        if extra_params:
            params.update(extra_params)
        return report.html_template.render(**params)
    else:  # create report
        form = _ReportForm(flask_report, request.form)

        if form.validate():
            name = form.name.data
            id = None
            if request.args.get('preview'):
                name += '(' + _('Preview') + ')'
                id = 0

            filter_map = {}
            for filter_ in json.loads(form.filters.data):
                filter_map.setdefault(filter_['col'], []).append({
                    'operator': filter_['op'],
                    'value': filter_['val'],
                    'synthetic': filter_['synthetic']
                })

            report_id = create_report(form.data_set, name=name,
                                      creator=form.creator.data,
                                      description=form.description.data,
                                      id=id, columns=form.columns.data,
                                      filters=filter_map)
            return jsonify({'id': report_id, 'name': form.name.data,
                            'url': url_for('.report', id_=report_id)})
        else:
            return jsonify({'errors': form.errors}), 403


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


def data_set_list(flask_report):
    flask_report.try_edit_data_set()
    data_sets = [DataSet(flask_report, int(dir_name)) for dir_name in
                 os.listdir(flask_report.data_set_dir) if
                 dir_name.isdigit() and dir_name != '0']
    params = dict(data_sets=data_sets)
    extra_params = flask_report.data_set_list_template_param(data_sets)
    if extra_params:
        params.update(extra_params)
    return render_template("report____/data-set-list.html", **params)


def data_set(flask_report, id_):
    flask_report.try_edit_data_set()
    data_set = DataSet(flask_report, id_)
    SQL_html = highlight(query_to_sql(data_set.query), SqlLexer(),
                         HtmlFormatter())
    params = dict(data_set=data_set, SQL=SQL_html)
    extra_params = flask_report.data_set_template_param(data_set)
    if extra_params:
        params.update(extra_params)
    return render_template("report____/data-set.html", **params)


def notification_list(flask_report):
    notifications = [Notification(flask_report, int(dir_name)) for dir_name
                     in os.listdir(flask_report.notification_dir) if
                     dir_name.isdigit() and dir_name != '0']
    params = dict(notification_list=notifications)
    extra_params = flask_report.notification_list_template_param(notifications)
    if extra_params:
        params.update(extra_params)
    return render_template("report____/notification-list.html", **params)


def _save_notification(flask_report, form, id_):
    kwargs = dict(name=form["name"], senders=form.getlist("sender"),
                  report_ids=form.getlist("report_ids", type=int),
                  description=form["description"],
                  subject=form["subject"], crontab=form["crontab"],
                  enabled=form.get("enabled", type=bool, default=False))
    dump_yaml(os.path.join(flask_report.notification_dir, str(id_),
                           'meta.yaml'), **kwargs)


def notification(flask_report, id_=None):
    flask_report.try_edit_notification()

    if id_ is not None:
        notification = Notification(flask_report, id_)

        if request.method == "POST":
            if request.form.get('action') == _('Enable'):
                flask_report.start_notification(id_)
            elif request.form.get("action") == _("Disable"):
                flask_report.stop_notification(id_)
            else:
                _save_notification(flask_report, request.form, id_)
            flash(_("Update Successful!"))
            return redirect(url_for(".notification", id_=id_,
                                    _method="GET"))
        else:
            params = dict(notification=notification,
                          report_list=flask_report.report_list)
            extra_params = flask_report.notification_template_param(
                notification)
            if extra_params:
                params.update(extra_params)
            return render_template("report____/notification.html", **params)
    else:
        if request.method == "POST":
            id_ = max([int(dir_name) for dir_name in
                       os.listdir(flask_report.notification_dir) if
                       dir_name.isdigit() and dir_name != '0']) + 1
            new_dir = os.path.join(flask_report.notification_dir, str(id_))
            if not os.path.exists(new_dir):
                os.mkdir(new_dir)
            _save_notification(flask_report, request.form, id_)
            flash(_("Save Successful!"))
            return redirect(url_for(".notification", id_=id_))
        else:
            # TODO why no id_?
            params = dict(report_list=flask_report.report_list)
            extra_params = flask_report.notification_template_param(None)
            if extra_params:
                params.update(extra_params)
            return render_template("report____/notification.html", **params)


def schedule_list(flask_report):
    return json.dumps([str(job) for job in flask_report.sched.get_jobs()])


def push_notification(flask_report, id_):
    to = request.args.get('to')
    notification = Notification(flask_report, id_)
    # don't use sender, use recipient instead
    if not to:
        senders = notification.senders
    else:
        senders = [to]

    for sender in senders:
        if sender not in senders:
            return _('notification %(id)s is not allowed to send to %(to)s',
                     id=id_, to=sender), 403
    html = notification.template.render(notification=notification)
    msg = Message(subject=notification.subject,
                  html=html,
                  # TODO where sender come from
                  sender="lite_mms@163.com",
                  recipients=senders)
    flask_report.mail.send(msg)
    return 'ok'


def start_notification(flask_report, id_):
    notification = Notification(flask_report, id_)

    def _closure(environ):
        def _push_notification():
            with flask_report.app.request_context(environ):
                flask_report.push_notification(id_)

        return _push_notification

    flask_report.sched.add_cron_job(_closure(request.environ),
                                    name='flask_report_notification' + str(id_),
                                    **notification.crontab._asdict())
    notification.enabled = True
    notification.dump()
    return 'ok'


def stop_notification(flask_report, id_):
    jobs = flask_report.sched.get_jobs()
    for job in jobs:
        if job.name == 'flask_report_notification' + str(id_):
            notification = Notification(flask_report, id_)
            notification.enabled = False
            notification.dump()
            flask_report.sched.unschedule_job(job)
        return 'ok'
    else:
        return 'unknown notifiaction:' + str(id_), 404


def report_graphs(flask_report, id_):
    report = Report(flask_report, id_)
    return render_template("report____/graphs.html",
                           url=request.args.get("url"),
                           bar_charts=report.bar_charts,
                           name=report.name, pie_charts=report.pie_charts)
