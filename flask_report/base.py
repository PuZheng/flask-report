# -*- coding: UTF-8 -*-
import os
import json
import types
from StringIO import StringIO
import time
import csv
import functools

from apscheduler.schedulers.background import BackgroundScheduler
from flask import (render_template, request, url_for, redirect, flash, jsonify,
                   Response, Blueprint)
from flask.ext.mail import Message
from flask.ext.babel import _
from pygments import highlight
from pygments.lexers import PythonLexer, SqlLexer
from pygments.formatters import HtmlFormatter

from flask.ext.report import views
from flask.ext.report.notification import Notification, get_all_notifications
from flask.ext.report.report import Report, create_report
from flask.ext.report.data_set import DataSet
from flask.ext.report.utils import get_column_operated, query_to_sql, dump_yaml


class FlaskReport(object):

    def __init__(self, app, db, models, blueprint=None, extra_params=None,
                 table_label_map=None, mail=None):
        '''
        This is the class that add reports to a flask app.

        the usage is:

            app = Flask(__name__)
            db = SQLAlchemy(app)
            FlaskReport(app, db, )

        :param app: flask app instance
        :param db: database instance
        :param models: a list of models
        :param flaks.Blueprint blueprint: provide blueprint if you want register
            web pages under this blueprint
        :param dict extra_params: extra template parameters for each page, you
            may want to use them when you override default templates, for
            example, add a navigation bar. The keys include:

                * data-set-list
                * data-set
                * report-list
                * report
                * notification
                * notification-list

            they correspond to pages with the same filename plus suffix 'html'.
            The values are the parameters provided to each page, they may be
            functions with no args if you want lazy evaluation
        :param dict table_label_map: a dict from table to label, the keys are
            the table name, the values are the labels of each table
        :param mail: the mail instance if you want send email, see
            `Flask-Mail <https://pypi.python.org/pypi/Flask-Mail>`_
        '''
        self.db = db
        self.app = app
        host = blueprint or app
        self.conf_dir = app.config.get("REPORT_DIR", "report_conf")
        self.report_dir = os.path.join(self.conf_dir, "reports")
        self.notification_dir = os.path.join(self.conf_dir, "notifications")
        self.data_set_dir = os.path.join(self.conf_dir, "data_sets")
        self.table_label_map = table_label_map or {}

        self.model_map = dict((model.__name__, model) for model in models)

        if not os.path.exists(self.conf_dir):
            os.makedirs(self.conf_dir)
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)
        if not os.path.exists(self.data_set_dir):
            os.makedirs(self.data_set_dir)

        host.add_url_rule("/report-list/", 'report_list',
                          functools.partial(views.report_list, self))
        host.add_url_rule("/new-report/", 'new_report',
                          functools.partial(views.new_report, self),
                          methods=['POST'])
        host.add_url_rule("/graphs/report/<int:id_>", 'report_graphs',
                          functools.partial(self.report_graphs, self))
        host.add_url_rule("/report/<int:id_>", 'report',
                          functools.partial(self.report, self),
                          methods=['GET', 'POST'])
        host.add_url_rule("/report_csv/<int:id_>", 'report_csv',
                          functools.partial(self.report_csv, self))
        host.add_url_rule("/drill-down-detail/<int:report_id>/<int:col_id>",
                          'drill_down_detail',
                          functools.partial(self.drill_down_detail, self))

        host.route("/data-set-list/")(self.data_set_list)
        host.route("/data-set/<int:id_>")(self.data_set)
        host.route("/notification-list")(self.notification_list)
        host.route("/notification/", methods=['GET', 'POST'])(self.notification)
        host.route("/notification/<int:id_>", methods=['GET', 'POST'])(
            self.notification)
        host.route("/push_notification/<int:id_>",
                   methods=['POST'])(self.push_notification)
        host.route("/start_notification/<int:id_>",
                   methods=['GET'])(self.start_notification)
        host.route("/stop_notification/<int:id_>",
                   methods=['GET'])(self.stop_notification)
        host.route("/schedule-list")(self.get_schedules)

        # register it for using the templates of data browser
        self.blueprint = Blueprint("report____", __name__,
                                   static_folder="static",
                                   template_folder="templates")
        app.register_blueprint(self.blueprint, url_prefix="/__report__")
        self._extra_params = extra_params or {'report': lambda id_: {},
                                             'report_list': lambda: {},
                                             'data_set': lambda id_: {},
                                             'data_sets': lambda: {},
                                             'notification-list': lambda: {},
                                             'notification': lambda id_: {}}

        @app.template_filter("dpprint")
        def dict_pretty_print(value):
            if isinstance(value, list):
                return '[' + ', '.join(dict_pretty_print(i) for i in value) + \
                    ']'
            return '{' + ','.join('%s:%s' % (k, v) for k, v in value.items()) \
                + '}'

        if mail:
            self.mail = mail
            self.sched = BackgroundScheduler()
            self.sched.start()

            with app.test_request_context():
                for notification in get_all_notifications(self):
                    if notification.enabled:
                        self.start_notification(notification.id_)

    @property
    def model_map(self):
        '''
        a dictionary of which keys are the model classes' names, values are
        the model classes
        '''
        return self._model_map

    @property
    def extra_params(self):
        '''
        the user defined template parameters, see
        `flask.ext.report.FlaskReport.__init__`_
        '''
        return self._extra_params

    def try_view_report(self):
        '''
        this function will be invoked before accessing report or report-list,
        throw an exception if you don't want them to be accessed,
        I prefer *flask.ext.principal.PermissionDenied* personally
        '''
        pass

    def try_edit_data_set(self):
        '''
        this function will be invoked before creating/editing data set,
        throw an exception if you don't want them to be accessed,
        I prefer *flask.ext.principal.PermissionDenied* personally
        '''
        pass

    def try_edit_notification(self):
        '''
        this function will be invoked before creating/editing notification
        throw an exception if you don't want them to be accessed,
        I prefer *flask.ext.principal.PermissionDenied* personally
        '''
        pass

    def report_graphs(self, id_):
        report = Report(self, id_)
        return render_template("report____/graphs.html",
                               url=request.args.get("url"),
                               bar_charts=report.bar_charts,
                               name=report.name, pie_charts=report.pie_charts)

    def data_set_list(self):
        self.try_edit_data_set()
        data_sets = [DataSet(self, int(dir_name)) for dir_name in
                     os.listdir(self.data_set_dir) if
                     dir_name.isdigit() and dir_name != '0']
        params = dict(data_sets=data_sets)
        extra_params = self.extra_params.get("data-sets")
        if extra_params:
            if isinstance(extra_params, types.FunctionType):
                extra_params = extra_params()
            params.update(extra_params)
        return render_template("report____/data-set-list.html", **params)

    def data_set(self, id_):
        self.try_edit_data_set()
        data_set = DataSet(self, id_)
        SQL_html = highlight(query_to_sql(data_set.query), SqlLexer(),
                             HtmlFormatter())
        params = dict(data_set=data_set, SQL=SQL_html)
        extra_params = self.extra_params.get('data-set')
        if extra_params:
            if isinstance(extra_params, types.FunctionType):
                extra_params = extra_params(id_)
            params.update(extra_params)
        return render_template("report____/data-set.html", **params)

    def _get_report_list(self):
        return [Report(self, int(dir_name)) for dir_name in
                os.listdir(self.report_dir) if
                dir_name.isdigit() and dir_name != '0']

    def _write_report(self, to_dir, **kwargs):
        import yaml

        kwargs.setdefault("name", "temp")
        kwargs.setdefault("description", "temp")
        import datetime

        kwargs["create_time"] = datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S")
        file_name = os.path.join(to_dir, "meta.yaml")
        if os.path.isfile(file_name):
            new_file_name = os.path.join(to_dir, "meta.yaml~")
            if os.path.isfile(new_file_name):
                os.unlink(new_file_name)
            os.rename(file_name, new_file_name)
        with file(file_name, "w") as f:
            yaml.safe_dump(kwargs, allow_unicode=True, stream=f)

    def _get_report(self, id_, ReportClass):
        from flask.ext.report.report_templates import BaseReport

        assert issubclass(ReportClass, BaseReport)
        data = Report(self, id_)
        if not data.data:
            raise ValueError
        report = ReportClass(queryset=data.data, columns=data.columns,
                             report_name=data.name,
                             sum_columns=data.sum_columns,
                             avg_columns=data.avg_columns)
        return report


    def get_model_label(self, table):
        return self.table_label_map.get(table.name) or \
            self.table_map[table.name].__name__

    def notification_list(self):
        notifications = [Notification(self, int(dir_name)) for dir_name
                         in os.listdir(self.notification_dir) if
                         dir_name.isdigit() and dir_name != '0']
        params = dict(notification_list=notifications)
        extra_params = self.extra_params.get("notification-list")
        if extra_params:
            if isinstance(extra_params, types.FunctionType):
                extra_params = extra_params()
            params.update(extra_params)
        return render_template("report____/notification-list.html", **params)

    def notification(self, id_=None):
        self.try_edit_notification()

        def _write(form, id_):
            kwargs = dict(name=form["name"], senders=form.getlist("sender"),
                          report_ids=form.getlist("report_ids", type=int),
                          description=form["description"],
                          subject=form["subject"], crontab=form["crontab"],
                          enabled=form.get("enabled", type=bool, default=False))
            dump_yaml(os.path.join(self.notification_dir, str(id_),
                                   'meta.yaml'), **kwargs)

        if id_ is not None:
            notification = Notification(self, id_)

            if request.method == "POST":
                if request.form.get('action') == _('Enable'):
                    self.start_notification(id_)
                elif request.form.get("action") == _("Disable"):
                    self.stop_notification(id_)  # any change will incur disable
                else:
                    _write(request.form, id_)
                flash(_("Update Successful!"))
                return redirect(url_for(".notification", id_=id_,
                                        _method="GET"))
            else:
                params = dict(notification=notification,
                              report_list=self._get_report_list())
                extra_params = self.extra_params.get("notification")
                if extra_params:
                    if isinstance(extra_params, types.FunctionType):
                        extra_params = extra_params(id_)
                    params.update(extra_params)
                return render_template("report____/notification.html", **params)
        else:
            if request.method == "POST":
                id_ = max([int(dir_name) for dir_name in
                           os.listdir(self.notification_dir) if
                           dir_name.isdigit() and dir_name != '0']) + 1
                new_dir = os.path.join(self.notification_dir, str(id_))
                if not os.path.exists(new_dir):
                    os.mkdir(new_dir)
                _write(request.form, id_)
                flash(_("Save Successful!"))
                return redirect(url_for(".notification", id_=id_))
            else:
                params = dict(report_list=self._get_report_list())
                extra_params = self.extra_params.get("notification")
                if extra_params:
                    if isinstance(extra_params, types.FunctionType):
                        extra_params = extra_params()
                    params.update(extra_params)
                return render_template("report____/notification.html", **params)

    def push_notification(self, id_):
        to = request.args.get('to')
        notification = Notification(self, id_)
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
        self.mail.send(msg)
        return 'ok'

    def start_notification(self, id_):
        notification = Notification(self, id_)

        def _closure(environ):
            def _push_notification():
                with self.app.request_context(environ):
                    self.push_notification(id_)

            return _push_notification

        self.sched.add_cron_job(_closure(request.environ),
                                name='flask_report_notification' + str(id_),
                                **notification.crontab._asdict())
        notification.enabled = True
        notification.dump()
        return 'ok'

    def stop_notification(self, id_):
        jobs = self.sched.get_jobs()
        for job in jobs:
            if job.name == 'flask_report_notification' + str(id_):
                notification = Notification(self, id_)
                notification.enabled = False
                notification.dump()
                self.sched.unschedule_job(job)
            return 'ok'
        else:
            return 'unknown notifiaction:' + str(id_), 404

    def get_schedules(self):
        return json.dumps([str(job) for job in self.sched.get_jobs()])
