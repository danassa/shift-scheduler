from dateutil.relativedelta import *
from datetime import timedelta, date, datetime


def get_day_name(x):
    return {
        0: 'שני',
        1: 'שלישי',
        2: 'רביעי',
        3: 'חמישי',
        4: 'שישי',
        5: 'שבת',
        6: 'ראשון',
    }[x]


def get_first_sunday(month, year):
    first = date(year=year, month=month, day=1)
    days_till_sunday = 6 - first.weekday()
    return first + timedelta(days=days_till_sunday)


def get_last_saturday(month, year):
    next_month = date(year=year, month=month, day=1) + relativedelta(months=1)
    first_sunday_of_next_month = get_first_sunday(next_month.month, next_month.year)
    return first_sunday_of_next_month - timedelta(days=1)


def get_day_type(date):
    day = date.weekday()
    if day == 5:
        return 'שבת'
    if day == 4:
        return 'שישי'
    return 'חול'
