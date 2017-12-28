# encoding: utf-8

import collections
import time
from copy import deepcopy

import googleapiclient.errors

from . import utils


class Query:

    _lock = 0

    def __init__(self, api, parameters=None, metadata=None):

        self.raw = {
            'startRow': 0,
            'rowLimit': 5000
        }

        self.meta = {}
        self.api = api

        if parameters:
            self.raw.update(parameters)
        if metadata:
            self.meta.update(metadata)

    def _wait(self):

        now = time.time()
        elapsed = now - self._lock
        wait = max(0, 1 - elapsed)
        time.sleep(wait)
        self._lock = time.time()

        return wait

    @utils.immutable
    def range(self, start=None, stop=None, months=0, days=0):

        start, stop = utils.daterange(start, stop, days, months)

        self.raw.update({
            'startDate': start,
            'endDate': stop
        })

        return self

    @utils.immutable
    def dimension(self, *dimensions):

        self.raw['dimensions'] = list(dimensions)

        return self

    @utils.immutable
    def filter(self, dimension, expression, operator='equals', group_type='and'):

        dimension_filter = {
            'dimension': dimension,
            'expression': expression,
            'operator': operator
        }

        filter_group = {
            'groupType': group_type,
            'filters': [dimension_filter]
        }

        self.raw.setdefault('dimensionFilterGroups', []).append(filter_group)

        return self

    def clone(self):

        query = self.__class__(
            api=self.api,
            parameters=deepcopy(self.raw),
            metadata=deepcopy(self.meta)
        )

        return query

    @utils.immutable
    def limit(self, *limit_):

        if len(limit_) == 2:
            maximum, start = limit_
        else:
            start = 0
            maximum = limit_[0]

        self.meta['limit'] = maximum

        self.raw.update({
            'startRow': start,
            'rowLimit': min(5000, maximum)
        })

        return self

    @utils.immutable
    def next(self):

        step = self.raw.get('rowLimit', 5000)
        start = self.raw.get('startRow', 0) + step + 1
        self.raw['startRow'] = start

        return self

    def get(self):

        report = None
        cursor = self
        is_enough = False
        is_complete = False

        while not (is_enough or is_complete):
            chunk = cursor.execute()

            if report:
                report.append(chunk.raw[0], cursor)

            else:
                report = chunk

            is_enough = len(report.rows) >= self.meta.get('limit', float('inf'))
            is_complete = report.is_complete
            cursor = cursor.next()

        return report

    def build(self, copy=True):

        if copy:
            raw = deepcopy(self.raw)
        else:
            raw = self.raw

        return raw

    def execute(self):

        raw = self.build()
        url = self.api.url

        try:
            self._wait()
            response = self.api.account.service.searchanalytics().query(
                siteUrl=url, body=raw).execute()
        except googleapiclient.errors.HttpError as e:
            raise e

        return Report(response, self)

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.raw == other.raw
        return False

    def __repr__(self):
        return '<searchconsole.query.Query(dimensions={})>'.format(
            str(self.raw.get('dimensions', []))
        )


class Report:

    def __init__(self, raw, query):
        self.raw = []
        self.queries = []

        self.dimensions = query.raw.get('dimensions', [])
        self.metrics = ['clicks', 'impressions', 'ctr', 'position']
        self.columns = self.dimensions + self.metrics
        self.Row = collections.namedtuple('Row', self.columns)
        self.rows = []
        self.append(raw, query)

    def append(self, raw, query):
        self.raw.append(raw)
        self.queries.append(query)

        step = query.raw.get('rowLimit', 5000)
        rows = raw.get('rows', [])
        self.is_complete = len(rows) < step

        for row in self.raw[-1].get('rows', []):
            row = row.copy()
            dimensions = dict(zip(self.dimensions, row.pop('keys', [])))
            if not dimensions:
                print(query.raw, raw)
            self.rows.append(self.Row(**row, **dimensions))

    @property
    def first(self):
        if len(self.rows) == 0:
            return None
        else:
            return self.rows[0]

    @property
    def last(self):
        if len(self.rows) == 0:
            return None
        else:
            return self.rows[-1]

    def __iter__(self):
        return iter(self.rows)

    def __getitem__(self, key):
        return self.rows[key]

    def __contains__(self, item):
        return item in self.rows

    def __len__(self):
        return len(self.rows)

    def __repr__(self):
        return "<searchconsole.query.Report(rows={rows})>".format(rows=len(self))

    def to_dict(self):
        return [dict(row._asdict()) for row in self.rows]

    def to_dataframe(self):
        import pandas
        return pandas.DataFrame(self.rows)
