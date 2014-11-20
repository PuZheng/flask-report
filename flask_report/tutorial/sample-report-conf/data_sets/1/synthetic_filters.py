# -*- coding: UTF-8 -*-

from flask.ext.report.synthetic_filter import SyntheticFilter
from datetime import datetime


class MonthFilter(SyntheticFilter):

    _LAST_MONTH = 1
    _MONTH_BEFORE_LAST_MONTH = 2
    _THIS_QUARTER = 3
    _LAST_QUARTER = 4

    @property
    def name(self):
        return u'month'

    @property
    def operators(self):
        return ['eq']

    @property
    def type(self):
        return 'number'

    def __call__(self, model_map, op, value, q):
        today = datetime.today()
        value = int(value)
        if value == self._LAST_MONTH:
            start_month = today.month - 1
            end_month = start_month + 1
        elif value == self._MONTH_BEFORE_LAST_MONTH:
            start_month = today.month - 2
            end_month = start_month + 1
        elif value == self._THIS_QUARTER:
            start_month = ((today.month - 1) / 3) * 3 + 1
            end_month = start_month + 3
        elif value == self._LAST_QUARTER:
            start_month = ((today.month - 1) / 3) * 3 - 2
            end_month = start_month + 3

        # note, month start from 1, eg. 0 is actually December in last year
        if start_month > 0:
            start_year = today.year
        else:
            start_year = today.year - 1
            start_month += 12
        if end_month <= 0:
            end_year = today.year - 1
            end_month += 12
        elif end_month >= 13:
            end_year = today.year + 1
            end_month %= 12
        else:
            end_year = today.year

        start = datetime(start_year, start_month, 1)
        end = datetime(end_year, end_month, 1)
        WorkCommand = model_map['WorkCommand']
        return q.filter(WorkCommand.created >= start).filter(
            WorkCommand.created < end)

    @property
    def options(self):
        return [
            (self._LAST_MONTH, 'last month'),
            (self._MONTH_BEFORE_LAST_MONTH, 'month before last month'),
            (self._THIS_QUARTER, 'this quarter'),
            (self._LAST_QUARTER, 'last quarter'),
        ]

__all__ = [MonthFilter()]
