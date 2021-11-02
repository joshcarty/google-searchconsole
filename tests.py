# encoding: utf-8

import unittest
import doctest
import datetime
import os

import searchconsole
from auth.creds import webproperty_uri


class TestAuthentication(unittest.TestCase):
    """ Test whether authentication procedure works. Currently
    uses client_secrets and credentials files saved in ./auth
    directory of repository.
    """

    def test_mappings(self):
        """ Test whether a webmasters service can be created using
        Google format client_config and credentials mappings. """
        from auth.creds import client_secrets, credentials

        account = searchconsole.authenticate(
            client_config=client_secrets,
            credentials=credentials
        )

        self.assertIsInstance(account, searchconsole.account.Account)

    def test_files(self):
        """ Test whether a webmasters service can be created using
        a Google format client secrets and credentials file. """
        account = searchconsole.authenticate(
            client_config='auth/client_secrets.json',
            credentials='auth/credentials.dat'
        )

        self.assertIsInstance(account, searchconsole.account.Account)

    def test_serialize_credentials(self):
        """ Test whether a credentials object can serialized."""
        serialized_file = 'auth/webmasters.dat'

        account = searchconsole.authenticate(
            client_config='auth/client_secrets.json',
            credentials='auth/credentials.dat',
            serialize=serialized_file
        )

        serialized_file_exists = os.path.isfile(serialized_file)
        self.assertTrue(serialized_file_exists)

        serialized_account = searchconsole.authenticate(
            client_config='auth/client_secrets.json',
            credentials=serialized_file,
        )

        self.assertIsInstance(serialized_account, searchconsole.account.Account)

        os.remove(serialized_file)


class AuthenticatedTestCase(unittest.TestCase):
    """Base test authenticated using file-based client secrets and
    credentials."""

    def setUp(self):
        self.account = searchconsole.authenticate(
            client_config='auth/client_secrets.json',
            credentials='auth/credentials.dat'
        )
        self.webproperty = self.account[webproperty_uri]
        self.query = self.webproperty.query


class TestAccount(AuthenticatedTestCase):
    """ Test whether properties of a Search Console account can
    be accessed: e.g. web properties. """

    def test_indexing(self):
        """ Test whether an account can be indexed by a number or
        by the full URL of a web property. """
        a = self.account[0]
        b = self.account[a.url]

        self.assertEqual(a, b)


class TestQuerying(AuthenticatedTestCase):
    """ Test whether users can query Search Analytics from a web
    property in Search Console. """

    def test_query(self):
        """It should be able to run a query and return a report. """
        q = self.query.dimension('date').range('yesterday', days=-7)
        report = q.get()

        self.assertTrue(report.rows)

    def test_multiple_dimensions(self):
        """ It should return more rows for multiple dimensions. This addresses issues
        noted here: https://productforums.google.com/forum/#!msg/webmasters/PKNGqSo1t
        Kc/lAE0hcdGCQAJ """
        a = self.query.range('today', days=-7).dimension('query').get()
        b = self.query.range('today', days=-7).dimension('query', 'date').get()

        self.assertGreater(len(b), len(a))

    def test_range(self):
        """ It should handle different date types. """
        a = self.query.range(start='2017-01-01', stop='2017-01-03')
        b = self.query.range(start=datetime.date(2017, 1, 1), stop=datetime.date(2017, 1, 3))

        self.assertEqual(a.raw['startDate'], '2017-01-01')
        self.assertEqual(b.raw['startDate'], '2017-01-01')
        self.assertEqual(a.raw['startDate'], b.raw['startDate'])

    def test_range_days(self):
        """ It should handle a day offset from a start or stop date. """
        a = self.query.range(start='2017-01-01', stop='2017-01-03')
        b = self.query.range(start='2017-01-01', days=3)

        self.assertEqual(a.raw['endDate'], '2017-01-03')
        self.assertEqual(b.raw['endDate'], '2017-01-03')
        self.assertEqual(a.raw['endDate'], b.raw['endDate'])

    def test_range_months(self):
        """ It should handle a month offset from a start or stop date. """
        a = self.query.range(start='2017-01-01', stop='2017-01-31')
        b = self.query.range(start='2017-01-01', months=1)

        self.assertEqual(a.raw['endDate'], '2017-01-31')
        self.assertEqual(b.raw['endDate'], '2017-01-31')
        self.assertEqual(a.raw['endDate'], b.raw['endDate'])

    def test_descriptions(self):
        """ It should handle some convenient date strings. """
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        a = self.query.range('yesterday', days=-1)
        b = self.query.range(yesterday, days=-1)

        self.assertEqual(a.raw['endDate'], b.raw['endDate'])

    def test_search_type(self):
        """ It should be able to filter for the specific search type. """
        a = self.query.search_type('image')
        self.assertEqual(a.raw['type'], 'image')

    def test_search_type_metrics(self):
        """ Certain search types should not return position """
        a = self.query.range('yesterday', days=-7).get()
        b = self.query.search_type('googleNews').range('yesterday', days=-7).get()

        self.assertTrue(hasattr(a.Row, 'position'))
        self.assertFalse(hasattr(b.Row, 'position'))

    def test_immutable(self):
        """ Queries should be refined by creating a new query instance not
        by modifying the base query. """
        a = self.query.dimension('date')
        b = a.range('2017-11-01', '2017-11-03')

        self.assertNotEqual(a, b)
        self.assertNotEqual(a.raw, b.raw)

    def test_limit(self):
        """ It can limit the total amount of results. """
        q = self.query.range('yesterday', days=-7).dimension('date')
        full_report = q.get()
        limited_report = q.limit(2).get()

        self.assertEqual(len(limited_report.rows), 2)
        self.assertEqual(len(limited_report), 2)
        self.assertEqual(full_report.rows[:2], limited_report.rows[:2])

    def test_start_limit(self):
        """ It can limit the amount of results and the index at which
        to start.  """
        q = self.query.range('yesterday', days=-7).dimension('date')
        full_report = q.get()
        limited_report = q.limit(2, 2).get()

        self.assertEqual(len(limited_report), 2)
        self.assertEqual(full_report[2:4], limited_report.rows)


def load_tests(loader, tests, ignore):
    """ Many docstrings contain doctests. Instead of using a separate doctest
    runner, we use doctest's Unittest API."""
    account = searchconsole.authenticate(
        client_config='auth/client_secrets.json',
        credentials='auth/credentials.dat'
    )

    globs = {
        'account': account,
        'webproperty': account[webproperty_uri],
        'www_webproperty_com': webproperty_uri,
        'query': account[webproperty_uri].query
    }

    kwargs = {
        'globs': globs,
        'optionflags': doctest.ELLIPSIS
    }

    tests.addTests(doctest.DocTestSuite(searchconsole.auth, **kwargs))
    tests.addTests(doctest.DocTestSuite(searchconsole.account, **kwargs))
    tests.addTests(doctest.DocTestSuite(searchconsole.query, **kwargs))

    return tests


if __name__ == '__main__':
    unittest.main()
