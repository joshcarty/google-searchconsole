---
icon: lucide/home
---

# Google Search Console for Python

[![Tests](https://github.com/joshcarty/google-searchconsole/actions/workflows/tests.yml/badge.svg)](https://github.com/joshcarty/google-searchconsole/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**google-searchconsole** is a Python library that makes working with the Google Search Console API simple and easy.

The Google Search Console API can be complex to work with directly. This library makes it easy to:

- **Authenticate** - Access your Google Account using OAuth2 or a Service Account
- **Query** - Build complex queries in a simple way
- **Explore** - See all of the web properties in your account
- **Export** - Export data as a Pandas DataFrames or JSON to share or for further analysis

Built on top of [Google's official API Client](https://developers.google.com/webmaster-tools), this library is inspired by [@debrouwere](https://github.com/debrouwere)'s excellent [google-analytics](https://github.com/debrouwere/google-analytics) package.

## Quickstart

Make sure the package is installed with:

```bash
pip install git+https://github.com/joshcarty/google-searchconsole
```

Then:

```python
import searchconsole

# Authenticate with your browser:
account = searchconsole.authenticate(client_config='client_secrets.json')

# Select your site
webproperty = account['https://www.example.com/']

# Query and analyze
report = webproperty.query.range('today', days=-7).dimension('query').get()

# Export to pandas for analysis
df = report.to_dataframe()
print(df.head())

```

## Quick Links
<div class="grid cards" markdown>

- :material-rocket-launch: **[Getting Started](getting-started.md)**

    Set up your credentials and run your first query

- :material-key: **[Authentication Guide](authentication.md)**

    Learn about OAuth2 and service account authentication

- :material-book-open-variant: **[API Reference](api-reference.md)**

    Complete API documentation for all classes and methods

- :material-lightbulb: **[Examples](examples.md)**

    Practical examples and common use cases

</div>


## Key Features

### Simple Authentication

```python
# Interactive OAuth2 flow
account = searchconsole.authenticate(client_config='client_secrets.json')

# Save credentials for future use
account.serialize_credentials('credentials.json')

# Subsequent authentication with saved credentials
account = searchconsole.authenticate(
    client_config='client_secrets.json',
    credentials='credentials.json'
)
```

### Fluent Query API

Build complex queries with method chaining:

```python
report = (
    webproperty.query
    .range('today', days=-30)
    .dimension('query', 'page')
    .filter('query', 'python', 'contains')
    .filter('page', '/blog/', 'contains')
    .limit(1000)
    .get()
)
```

### Multiple Search Types

Query different search types beyond regular web search:

```python
# Image search
image_data = webproperty.query.search_type('image').range('today', days=-7).get()

# Google Discover
discover_data = webproperty.query.search_type('discover').range('today', days=-7).get()

# Video, news, and more
video_data = webproperty.query.search_type('video').range('today', days=-7).get()
```

### Filtering

Apply sophisticated filters to your queries:

```python
# Contains filter
report = query.filter('query', 'python', 'contains').get()

# Regex filter (RE2 syntax)
report = query.filter('page', r'/blog/\d{4}/\d{2}/', 'includingRegex').get()

# Multiple filters
report = (
    query
    .filter('country', 'usa', 'equals')
    .filter('device', 'mobile', 'equals')
    .get()
)
```

### Easy Data Export

```python
# Export to pandas DataFrame
df = report.to_dataframe()
df.to_csv('search_data.csv', index=False)
```

## Getting Started

1. **[Set up Google API credentials](getting-started.md#setup-credentials)** - Create a project in Google Developers Console
2. **[Authenticate](authentication.md)** - Choose OAuth2 or service account authentication
3. **[Build your first query](getting-started.md#your-first-query)** - Start exploring your data
4. **[Explore examples](examples.md)** - Learn from practical use cases

## Available Dimensions

Query your data across multiple dimensions:

- **`query`** - Search queries that triggered your pages
- **`page`** - Landing page URLs
- **`date`** - Dates of searches
- **`country`** - Country codes (ISO 3166-1 alpha-2)
- **`device`** - Device types (desktop, mobile, tablet)
- **`searchAppearance`** - How results appeared in search

## Available Metrics

All queries return these metrics:

- **`clicks`** - Number of clicks from search results
- **`impressions`** - Number of times your page appeared in search
- **`ctr`** - Click-through rate (clicks ÷ impressions)
- **`position`** - Average position in search results (not available for Discover/Google News)

## Search Types Supported

- `web` - Regular web search (default)
- `image` - Image search
- `video` - Video search
- `news` - News search
- `discover` - Google Discover
- `googleNews` - Google News

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/joshcarty/google-searchconsole/blob/master/LICENSE) file for details.

## Contributing

Contributions are welcome! Please see our [Contributing Guide](contributing.md) for details on how to get started.

## Support

- :fontawesome-brands-github: [Report an issue](https://github.com/joshcarty/google-searchconsole/issues)
- :fontawesome-brands-github: [View source code](https://github.com/joshcarty/google-searchconsole)
