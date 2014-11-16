# -*- coding: UTF-8 -*-

from itertools import izip

from flask.ext.report.synthetic_filter import SyntheticFilter
from datetime import datetime, timedelta
import calendar

class MonthFilter(SyntheticFilter):

    @property
    def name(self):
        return u'month'

    @property
    def operators(self):
        return ['eq']

    @property
    def type(self):
        return 'select'

    def __call__(self, value):
        year, month = value.split('-')
        year = int(year)
        month = int(month)
        first_day_of_month = datetime(year, month, 1)
        first_day_of_next_month = datetime(year, month, 1) + \
            timedelta(days=calendar.monthrange(year if (month != 12) \
                                               else (year + 1), (month + 1) % 12)[1])
        return {
            'WorkCommand.completed_time': [
                {
                    'operator': 'gt',
                    'value': str(first_day_of_month)
                },
                {
                    'operator': 'lt',
                    'value': str(first_day_of_next_month)
                }
            ]
        }

    @property
    def options(self):
        today = datetime.today()
        min_year = 2013
        min_month = 5
        max_year = today.year
        max_month = today.month + 1
        ret = []
        year_cnt = max_year - min_year + 1
        for year, month in izip((min_year, ) * 12 * year_cnt, range(1, 13) * year_cnt):
            if (year > min_year or (year == min_year and month >= min_month)) and (year < max_year or (year==max_year and month < max_month)):
                ret.append(('%d-%d' % (year, month), ) * 2)
            elif year > max_year or (year == max_year and month >= max_month):
                break
        return ret

__all__ = [MonthFilter()]
