# Google Search Console for Python

[![Build Status](https://travis-ci.org/joshcarty/google-searchconsole.svg?branch=master)](https://travis-ci.org/joshcarty/google-searchconsole)
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

## Quickstart

First, install the package using:

`pip3 install git+https://github.com/joshcarty/google-searchconsole`

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