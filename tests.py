# encoding: utf-8

import datetime
import doctest
import json
import os
import unittest

import dotenv

import searchconsole

dotenv.load_dotenv()


def get_client_config():
    """Get client config from environment variable."""
    return json.loads(os.environ["SEARCHCONSOLE_CLIENT_CONFIG"])


def get_credentials():
    """Get credentials from environment variable."""
    return json.loads(os.environ["SEARCHCONSOLE_CREDENTIALS"])


def get_webproperty_uri():
    """Get webproperty URI from environment variable."""
    return os.environ["SEARCHCONSOLE_WEBPROPERTY_URI"]


def get_service_account():
    """Get service account from environment variable."""
    return json.loads(os.environ["SEARCHCONSOLE_SERVICE_ACCOUNT"])


class TestAuthentication(unittest.TestCase):
    """Test whether authentication procedure works using environment
    variables or local auth files.
    """

    def setUp(self):
        self.client_config = get_client_config()
        self.credentials = get_credentials()

    def test_authentication(self):
        """Test whether a webmasters service can be created using
        client config and credentials from environment variables."""
        account = searchconsole.authenticate(
            client_config=self.client_config, credentials=self.credentials
        )

        self.assertIsInstance(account, searchconsole.account.Account)

    def test_service_account_authentication(self):
        """Test whether a webmasters service can be created using
        a service account JSON file."""
        account = searchconsole.authenticate(
            service_account=get_service_account(),
        )

        self.assertIsInstance(account, searchconsole.account.Account)

    @unittest.skipUnless(
        os.path.isfile("auth/client_config.json")
        and os.path.isfile("auth/credentials.json"),
        "Skipping file-based test: auth files not found",
    )
    def test_files(self):
        """Test whether a webmasters service can be created using
        a Google format client secrets and credentials file."""
        account = searchconsole.authenticate(
            client_config="auth/client_config.json", credentials="auth/credentials.json"
        )

        self.assertIsInstance(account, searchconsole.account.Account)

    @unittest.skipUnless(
        os.path.isdir("auth"), "Skipping serialize test: auth directory not found"
    )
    def test_serialize_credentials(self):
        """Test whether a credentials object can serialized."""
        serialized_file = "auth/credentials.json"

        searchconsole.authenticate(
            client_config=self.client_config,
            credentials=self.credentials,
            serialize=serialized_file,
        )

        serialized_file_exists = os.path.isfile(serialized_file)
        self.assertTrue(serialized_file_exists)

        serialized_account = searchconsole.authenticate(
            client_config=self.client_config,
            credentials=serialized_file,
        )

        self.assertIsInstance(serialized_account, searchconsole.account.Account)

        os.remove(serialized_file)


class AuthenticatedTestCase(unittest.TestCase):
    """Base test authenticated using environment variables or local auth files."""

    def setUp(self):
        self.account = searchconsole.authenticate(
            client_config=get_client_config(), credentials=get_credentials()
        )
        self.webproperty = self.account[get_webproperty_uri()]
        self.query = self.webproperty.query


class TestAccount(AuthenticatedTestCase):
    """Test whether properties of a Search Console account can
    be accessed: e.g. web properties."""

    def test_indexing(self):
        """Test whether an account can be indexed by a number or
        by the full URL of a web property."""
        a = self.account[0]
        b = self.account[a.url]

        self.assertEqual(a, b)


class TestQuerying(AuthenticatedTestCase):
    """Test whether users can query Search Analytics from a web
    property in Search Console."""

    def test_query(self):
        """It should be able to run a query and return a report."""
        q = self.query.dimension("date").range("yesterday", days=-7)
        report = q.get()

        self.assertTrue(report.rows)

    def test_multiple_dimensions(self):
        """It should return more rows for multiple dimensions. This addresses issues
        noted here: https://productforums.google.com/forum/#!msg/webmasters/PKNGqSo1t
        Kc/lAE0hcdGCQAJ"""
        a = self.query.range("today", days=-7).dimension("query").get()
        b = self.query.range("today", days=-7).dimension("query", "date").get()

        self.assertGreater(len(b), len(a))

    def test_range(self):
        """It should handle different date types."""
        a = self.query.range(start="2017-01-01", stop="2017-01-03")
        b = self.query.range(
            start=datetime.date(2017, 1, 1), stop=datetime.date(2017, 1, 3)
        )

        self.assertEqual(a.raw["startDate"], "2017-01-01")
        self.assertEqual(b.raw["startDate"], "2017-01-01")
        self.assertEqual(a.raw["startDate"], b.raw["startDate"])

    def test_range_days(self):
        """It should handle a day offset from a start or stop date."""
        a = self.query.range(start="2017-01-01", stop="2017-01-03")
        b = self.query.range(start="2017-01-01", days=3)

        self.assertEqual(a.raw["endDate"], "2017-01-03")
        self.assertEqual(b.raw["endDate"], "2017-01-03")
        self.assertEqual(a.raw["endDate"], b.raw["endDate"])

    def test_range_months(self):
        """It should handle a month offset from a start or stop date."""
        a = self.query.range(start="2017-01-01", stop="2017-01-31")
        b = self.query.range(start="2017-01-01", months=1)

        self.assertEqual(a.raw["endDate"], "2017-01-31")
        self.assertEqual(b.raw["endDate"], "2017-01-31")
        self.assertEqual(a.raw["endDate"], b.raw["endDate"])

    def test_descriptions(self):
        """It should handle some convenient date strings."""
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        a = self.query.range("yesterday", days=-1)
        b = self.query.range(yesterday, days=-1)

        self.assertEqual(a.raw["endDate"], b.raw["endDate"])

    def test_search_type(self):
        """It should be able to filter for the specific search type."""
        a = self.query.search_type("image")
        self.assertEqual(a.raw["type"], "image")

    def test_search_type_metrics(self):
        """Certain search types should not return position"""
        a = self.query.range("yesterday", days=-7).get()
        b = self.query.search_type("googleNews").range("yesterday", days=-7).get()

        self.assertTrue(hasattr(a.Row, "position"))
        self.assertFalse(hasattr(b.Row, "position"))

    def test_immutable(self):
        """Queries should be refined by creating a new query instance not
        by modifying the base query."""
        a = self.query.dimension("date")
        b = a.range("2017-11-01", "2017-11-03")

        self.assertNotEqual(a, b)
        self.assertNotEqual(a.raw, b.raw)

    def test_limit(self):
        """It can limit the total amount of results."""
        q = self.query.range("yesterday", days=-7).dimension("date")
        full_report = q.get()
        limited_report = q.limit(2).get()

        self.assertEqual(len(limited_report.rows), 2)
        self.assertEqual(len(limited_report), 2)
        self.assertEqual(full_report.rows[:2], limited_report.rows[:2])

    def test_start_limit(self):
        """It can limit the amount of results and the index at which
        to start."""
        q = self.query.range("yesterday", days=-7).dimension("date")
        full_report = q.get()
        limited_report = q.limit(2, 2).get()

        self.assertEqual(len(limited_report), 2)
        self.assertEqual(full_report[2:4], limited_report.rows)


def load_tests(loader, tests, ignore):
    """Many docstrings contain doctests. Instead of using a separate doctest
    runner, we use doctest's Unittest API."""
    client_config = get_client_config()
    credentials = get_credentials()

    account = searchconsole.authenticate(
        client_config=client_config, credentials=credentials
    )

    webproperty_uri = get_webproperty_uri()

    globs = {
        "account": account,
        "webproperty": account[webproperty_uri],
        "www_webproperty_com": webproperty_uri,
        "client_config_json": client_config,
        "credentials_json": credentials,
        "query": account[webproperty_uri].query,
    }

    kwargs = {"globs": globs, "optionflags": doctest.ELLIPSIS}

    tests.addTests(doctest.DocTestSuite(searchconsole.auth, **kwargs))
    tests.addTests(doctest.DocTestSuite(searchconsole.account, **kwargs))
    tests.addTests(doctest.DocTestSuite(searchconsole.query, **kwargs))

    return tests


if __name__ == "__main__":
    unittest.main()
