# encoding: utf-8

import datetime
import functools

from dateutil.relativedelta import relativedelta
from dateutil.parser import parse


def immutable(method):
    @functools.wraps(method)
    def wrapped_method(self, *args, **kwargs):
        obj = self.clone()
        method(obj, *args, **kwargs)
        return obj

    return wrapped_method


def serialize(date):
    if isinstance(date, datetime.date):
        return date.isoformat()
    return date


def extract(obj):
    if isinstance(obj, datetime.date):
        if hasattr(obj, 'date'):
            return obj.date()
        else:
            return obj
    else:
        raise ValueError('Not a datetime or date object.')


def normalize(obj):
    if obj is None:
        return None
    if isinstance(obj, datetime.date):
        return extract(obj)
    elif isinstance(obj, str):
        try:
            return extract(parse(obj))
        except ValueError:
            return extract(parse_description(obj))


def parse_description(s):
    today = datetime.date.today()
    if s == 'today':
        return today
    elif s == 'yesterday':
        return today - relativedelta(days=1)
    else:
        raise ValueError('Cannot parse date string.')



def daterange(start=None, stop=None, days=0, months=0):
    yesterday = datetime.date.today() - relativedelta(days=1)
    start = normalize(start) or yesterday
    stop = normalize(stop)

    is_past = days < 0 or months < 0

    if days or months:
        if start and stop:
            raise Exception(
                "A date range cannot be defined alongside months or days."
            )
        else:
            if is_past:
                days = days + 1
            else:
                days = days - 1

            delta = relativedelta(days=days, months=months)

            stop = start + delta

    stop = stop or start

    return map(serialize, sorted([start, stop]))

