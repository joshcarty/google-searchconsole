# encoding: utf-8

import collections
import time
from copy import deepcopy

import googleapiclient.errors

from . import utils


class Query:

    """
    Return a query for certain metrics and dimensions.

    This is the main way through which to produce reports from data in
    Google Search Console.

    The most important methods are:

    * `range` to specify a date range for your query. Queries are still limited
      by the 3 month limit and no Exception is raised if you exceed this limit.
    * `dimension` to specify the dimensions you would like report on (country,
      device, page, query, searchAppearance)
    * `filter` to specify which rows to filter by.
    * `limit` to specify a subset of results.

    The query object is mostly immutable. Methods return a new query rather
    than modifying in place, allowing you to create new queries without
    unintentionally modifying the state of another query.

    Usage:
    >>> webproperty.query.range(start='today', days=-7).dimension('date').get()
    <searchconsole.query.Report(rows=...)>
    >>> query = webproperty.query.range(start='today', days=-7)\\
    ...                          .dimension('date', 'query')\\
    ...                          .filter('query', 'dress', 'contains')\\
    ...                          .filter('page', '/womens-clothing/', 'contains')\\
    ...                          .limit(20000)
    >>> query.get()
    <searchconsole.query.Report(rows=...)>
    """

    _lock = 0

    def __init__(self, api, parameters=None, metadata=None):
        self.raw = {
            'startRow': 0,
            'rowLimit': 25000
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
        """
        Return a new query that fetches metrics within a given date range.

        Args:
            start (str or datetime.date): Query start date.
            stop (str or datetime.date): Query end date.
            months (int): Months from or to.
            days (int): Days from or to.

        Returns:
            `searchconsole.query.Query`

        Usage:
            >>> query.range('2017-01-01', '2017-01-07')
            <searchconsole.query.Query(...)>
            >>> query.range('2017-01-01', days=28)
            <searchconsole.query.Query(...)>
            >>> query.range('2017-01-01', months=3)
            <searchconsole.query.Query(...)>
        """

        start, stop = utils.daterange(start, stop, days, months)

        self.raw.update({
            'startDate': start,
            'endDate': stop
        })

        return self

    @utils.immutable
    def dimension(self, *dimensions):
        """
        Return a new query that fetches the specified dimensions.

        Args:
            *dimensions (str): Dimensions you would like to report on.
                Possible values: country, device, page, query, searchAppearance

        Returns:
            `searchconsole.query.Query`

        Usage:
            >>> query.filter('query', 'dress', 'contains')
            <searchconsole.query.Query(...)>
        """

        self.raw['dimensions'] = list(dimensions)

        return self

    @utils.immutable
    def filter(self, dimension, expression, operator='equals',
               group_type='and'):
        """
        Return a new query that filters rows by the specified filter.

        Args:
            dimension (str): Dimension you would like to filter on.
            expression (str): The value you would like to filter.
            operator (str): The operator you would like to use to filter.
                Possible values: equals, contains, notContains, includingRegex, excludingRegex.
            group_type (str): The way in which you would like multiple filters
                to combine. Note: currently only 'and' is supported by the API.

        Returns:
            `searchconsole.query.Query`

        Usage:
            >>> query.filter('query', 'dress', 'contains')
            <searchconsole.query.Query(...)>
        """

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

    @utils.immutable
    def search_type(self, search_type):
        """
        Return a new query that filters for the specified search type.
        Args:
            search_type (str): The search type you would like to report on.
                Possible values: 'web' (default), 'image', 'video', 'discover','googleNews'.

        Returns:
            `searchconsole.query.Query`

        Usage:
            >>> query.search_type('image')
            <searchconsole.query.Query(...)>
        """

        self.raw['type'] = search_type

        return self

    @utils.immutable
    def data_state(self, data_state):
        """
        Return a new query filtered by the specified data_state, which allows you 
        to include fresh (not finalized) data in your API call.  

        Fresh data: data as recent as less than a day old. Fresh data point can 
        be replaced with the final data point after a few days. 

        Args:
            data_state (str): The data_state you would like to use for your report. 
                Possible values: 'final' (default - only finalized data), 
                'all' (finalized & fresh data).

        Returns:
            `searchconsole.query.Query`

        Usage:
            >>> query.data_state('final')
            <searchconsole.query.Query(...)>
        """

        self.raw['dataState'] = data_state

        return self

    @utils.immutable
    def limit(self, *limit_):
        """
        Return a new query limiting the number of rows returned. It can also
        be used to offset a certain number of rows using a SQL-like syntax.

        Args:
            *limit_ (int): The maximum number of rows to return.

        Returns:
            `searchconsole.query.Query`

        Usage:
            >>> query.limit(10)
            <searchconsole.query.Query(...)>
            >>> query.limit(10, 10)
            <searchconsole.query.Query(...)>
        """

        if len(limit_) == 2:
            maximum, start = limit_
        else:
            start = 0
            maximum = limit_[0]

        self.meta['limit'] = maximum

        self.raw.update({
            'startRow': start,
            'rowLimit': min(25000, maximum)
        })

        return self

    def clone(self):

        query = self.__class__(
            api=self.api,
            parameters=deepcopy(self.raw),
            metadata=deepcopy(self.meta)
        )

        return query

    @utils.immutable
    def next(self):

        step = self.raw.get('rowLimit', 25000)
        start = self.raw.get('startRow', 0) + step
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
    """
    Executing a query will return a report, which contains the requested data.

    Queries are executed and turned into a report lazily whenever data is
    requested. You can explicitly create a report using the `Query.get` method.

    Usage:
    >>> webproperty.query.range(start='today', days=-7).dimension('date')
    <searchconsole.query.Query(...)>
    >>> webproperty.query.range(start='today', days=-7).dimension('date').get()
    <searchconsole.query.Report(rows=...)>

    You can access the data using:
    >>> report = webproperty.query.range(start='today', days=-7).dimension('date').get()
    >>> report.rows
    [Row(...), ..., Row(...)]
    """

    def __init__(self, raw, query):
        self.raw = []
        self.queries = []

        self.dimensions = query.raw.get('dimensions', [])
        self.metrics = self._build_metrics(query)
        self.columns = self.dimensions + self.metrics
        self.Row = collections.namedtuple('Row', self.columns)
        self.rows = []
        self.append(raw, query)

    @staticmethod
    def _build_metrics(query):
        metrics = ['clicks', 'impressions', 'ctr', 'position']
        # Not all metrics are supported by all reports types.
        if query.raw.get('type') in ('discover', 'googleNews'):
            metrics.remove('position')
        return metrics

    def append(self, raw, query):
        self.raw.append(raw)
        self.queries.append(query)

        step = query.raw.get('rowLimit', 25000)
        rows = raw.get('rows', [])
        self.is_complete = not rows

        for row in self.raw[-1].get('rows', []):
            row = row.copy()
            dimensions = dict(zip(self.dimensions, row.pop('keys', [])))
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
