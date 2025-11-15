# Google Search Console for Python

[![Tests](https://github.com/joshcarty/google-searchconsole/actions/workflows/tests.yml/badge.svg)](https://github.com/joshcarty/google-searchconsole/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

`google-searchconsole` takes the pain out of working with the [Google Search
Console](https://support.google.com/webmasters/answer/4559176?hl=en) Search Analytics Query API. It is written in Python and provides
convenient features to make querying a site's search analytics data easier.

* **Authentication.** We provide a few different ways to make generating
credentials and authenticating with your account easier. You can use stored
fies as well as a way to do the OAuth2 flow interactively.
* **Querying.** Easier to query by date ranges and filter by various
dimensions. No longer posting large nested JSON, the query object lets you make
complex queries with ease.
* **Exploration.** You can traverse your account hierarchy, with an account
containing webproperties with clear permission levels.
* **Exports.** Clean JSON and pandas.DataFrame outputs so you can easily
analyse your data in Python or Excel.

This package is built on top of
[Google's own API Client](https://developers.google.com/webmaster-tools/search-console-api-original/v3/prereqs)
and is heavily inspired, from design to implementation, by [@debrouwere](https://github.com/debrouwere)'s
fantastic [`google-analytics`](https://github.com/debrouwere/google-analytics) package.

Check out the full [documentation](https://joshcarty.github.io/google-searchconsole/).

## Quickstart

First, install the package using:

`$ pip install git+https://github.com/joshcarty/google-searchconsole`

Then, create a new project in the [Google Developers Console](https://console.developers.google.com),
enable the  Google Search Console API under "APIs & Services". Next, create credentials
for an OAuth client ID, choosing the Other Application type. Download a JSON copy of
your client secrets.

After that, executing your first query is as easy as

```python
import searchconsole
account = searchconsole.authenticate(client_config='client_secrets.json')
webproperty = account['https://www.example.com/']
report = webproperty.query.range('today', days=-7).dimension('query').get()
print(report.rows)
```

The above example will use your client configuration file to interactively
generate your credentials.


### Saving Credentials
If you wish to save your credentials, to avoid going
through the OAuth consent screen in the future, you can specify a path to save
them by specifying `serialize='path/to/credentials.json`.

When you want to authenticate a new account you run:

```python
account = searchconsole.authenticate(client_config='client_secrets.json',
                                     serialize='credentials.json')
```
Which will save your credentials to a file called `credentials.json`.

From then on, you can authenticate with:

```python
account = searchconsole.authenticate(client_config='client_secrets.json',
                                     credentials='credentials.json')
```

### Integration with Pandas DataFrame 
If you wish to load your data directly into a pandas
DataFrame, to avoid loading it manually after the extraction, 
you can do it easily: 

```python
report = webproperty.query.range('today',days=-7).dimension('page').get().to_dataframe()
```

### Search types
You can specify the search type data you want to retrieve by using the **search_type** method with your query. The following values are currently [supported by the API](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query): *news, video, image, web, discover & googleNews*. If you don't use this method, the default value used will be **web**, 

```python
report = webproperty.query.search_type('discover').range('today',days=-7).dimension('page').get().to_dataframe()
```

### Filters
You can apply filters while executing a query. The filter types supported by the API are the same available in the UI: *contains, equals, notContains, notEquals, includingRegex & excludingRegex.*

```python
report = webproperty.query.range('today',days=-7).dimension('page').filter('page','/blog/','contains').get().to_dataframe()
```

Note that if you use Regex in your filter, you must follow [RE2 syntax](https://github.com/google/re2/wiki/Syntax).

## Development

### Setting Up for Development

To contribute to this project or run tests locally, you'll need to install the package in development mode.

We recommend using [uv](https://docs.astral.sh/uv/) for faster dependency management, but pip also works.

1. **Clone the repository:**
   ```bash
   $ git clone https://github.com/joshcarty/google-searchconsole.git
   $ cd google-searchconsole
   ```

2. **Install the package in editable mode:**

   **Using uv (recommended):**
   ```bash
   $ uv sync
   ```

   **Using pip:**
   ```bash
   $ python -m venv .venv
   $ source .venv/bin/activate
   $ (.venv) pip install -e .
   ```

   This installs the package from the `src/` directory in editable mode, so any changes you make to the source code are immediately reflected without needing to reinstall.

### Running Tests

The project uses Python's built-in `unittest` framework. Tests require authentication credentials to be set as environment variables.

1. **Set up authentication credentials:**
   ```bash
   $ export SEARCHCONSOLE_CLIENT_CONFIG='{"installed": {...}}'
   $ export SEARCHCONSOLE_CREDENTIALS='{"token": "...", ...}'
   $ export SEARCHCONSOLE_WEBPROPERTY_URI='https://www.example.com/'
   ```

2. **Run the tests:**

   **Using uv (recommended):**
   ```bash
   $ uv run python -m unittest tests
   ```

   **Using pip:**
   ```bash
   $ python -m unittest tests
   ```

The test suite includes both unit tests and doctests embedded in the module docstrings.
