# -*- coding: UTF-8 -*-
import os
import codecs
from collections import namedtuple
from datetime import date

import yaml
from flask.ext.report.report import Report

CronTab = namedtuple('CronTab',
                     ['minute', 'hour', 'day', 'month', 'day_of_week'])


class Notification(object):
    '''
    notification is a series of sending actions
    '''

    def __init__(self, flask_report, id_):
        '''
        :param flask.ext.report.FlaskReport flask_report: flask report instance
        :param id_: id of the notification
        '''
        self.flask_report = flask_report
        self.id_ = id_

        meta_file = os.path.join(self.flask_report.notification_dir,
                                 str(id_), 'meta.yaml')
        meta = yaml.load(file(meta_file).read())
        self.name = meta['name']
        self.creator = meta.get('creator')
        self.create_time = meta.get('create_time')
        self.description = meta.get("description", '')
        self.senders = meta.get('senders')
        self.report_ids = meta.get('report_ids')
        self.__subject = meta.get('subject')
        self._crontab = meta.get('crontab')
        self.enabled = meta.get('enabled')

    @property
    def template(self):
        '''
        template of the email content to be sent, firstly, the file
        "template.html" will be used if it is presented in the notification
        definition directory, otherwise, 'report____/default_notification.html'
        will be used
        '''
        template_file = os.path.join(self.flask_report.notification_dir,
                                     str(self.id_), "template.html")
        if not os.path.exists(template_file):
            return self.flask_report.app.jinja_env.get_template(
                "report____/default_notification.html")
        return self.flask_report.app.jinja_env.from_string(
            codecs.open(template_file, encoding='utf-8').read())

    @property
    def subject(self):
        '''
        subject of the notification email, it reads the template string
        in notification configuration file and feeds it with 2 parameters,
        date and notification object
        '''
        return self.flask_report.app.jinja_env.from_string(
            self.__subject).render(date=date.today(), notification=self)

    @property
    def reports(self):
        '''
        reports to be sent
        '''
        return [Report(self.flask_report, id_) for id_ in self.report_ids]

    @property
    def crontab(self):

        return CronTab(*self._crontab.split())

    def dump(self):
        '''
        save this notifiction on disk
        '''
        meta_file = os.path.join(self.flask_report.notification_dir,
                                 str(self.id_), 'meta.yaml')
        d = {
            'name': self.name,
            'creator': self.creator,
            'create_time': self.create_time,
            'description': self.description,
            'senders': self.senders,
            'report_ids': self.report_ids,
            'subject': self.__subject,
            'crontab': self._crontab,
            'enabled': self.enabled
        }
        for k, v in d.items():
            if v is None:
                del d[k]
        yaml.dump(d, open(meta_file, 'w'), allow_unicode=True)
