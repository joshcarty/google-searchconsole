---
icon: lucide/book-open
---

# API Reference

Complete reference documentation for all classes, methods, and functions in the Google Search Console library.

## Module: `searchconsole`

### `authenticate()`

Primary authentication function that returns an authenticated `Account` object.

```python
searchconsole.authenticate(
    client_config=None,
    credentials=None,
    serialize=None,  # DEPRECATED
    flow="web",
    service_account=None
)
```

**Parameters:**

- **`client_config`** (str or dict, optional): OAuth2 client configuration
    - Path to JSON file containing client secrets
    - Dictionary with client configuration
    - Required for OAuth2 authentication (unless using service account)

- **`credentials`** (str or dict, optional): OAuth2 user credentials
    - Path to JSON file containing saved credentials
    - Dictionary with credential data
    - If not provided, will initiate OAuth flow

- **`serialize`** (str, optional): **DEPRECATED** - Use `Account.serialize_credentials()` instead
    - Path to save credentials after authentication

- **`flow`** (str, default="web"): OAuth2 flow type
    - `"web"`: Opens browser for authentication (default)
    - `"console"`: Prints URL for manual authentication (for remote servers)

- **`service_account`** (str or dict, optional): Service account credentials
    - Path to service account JSON key file
    - Dictionary with service account data
    - Cannot be used with `client_config` or `credentials`

**Returns:**

- **`Account`**: Authenticated account object with access to web properties

**Raises:**

- **`ValueError`**: If both OAuth2 and service account credentials are provided, or if no credentials provided

**Examples:**

```python
# First-time OAuth2 authentication
account = searchconsole.authenticate(client_config='client_secrets.json')

# With saved credentials
account = searchconsole.authenticate(
    client_config='client_secrets.json',
    credentials='credentials.json'
)

# Console flow
account = searchconsole.authenticate(
    client_config='client_secrets.json',
    flow='console'
)

# Service account
account = searchconsole.authenticate(
    service_account='service_account.json'
)

# Using dictionaries
account = searchconsole.authenticate(
    client_config={'installed': {...}},
    credentials={'token': '...', ...}
)
```

---

## Class: `Account`

Represents a Google Search Console account with access to multiple web properties.

!!! note
    `Account` objects are created by `authenticate()` and should not be instantiated directly.

### Attributes

#### `webproperties`

List of all web properties accessible to this account.

```python
account.webproperties  # List[WebProperty]
```

**Returns:** List of `WebProperty` objects

**Example:**

```python
for prop in account.webproperties:
    print(f"{prop.url} - {prop.permission}")
```

### Methods

#### `serialize_credentials()`

Save OAuth2 credentials to a file for future use.

```python
account.serialize_credentials(path)
```

**Parameters:**

- **`path`** (str): File path where credentials should be saved

**Returns:** Result of serialization operation

**Raises:**

- **`ValueError`**: If using service account (service accounts cannot be serialized)

**Example:**

```python
account = searchconsole.authenticate(client_config='client_secrets.json')
account.serialize_credentials('credentials.json')
```

### Indexing

Access web properties by index or URL:

```python
# By integer index
webproperty = account[0]  # First property
webproperty = account[1]  # Second property

# By URL string
webproperty = account['https://www.example.com/']
webproperty = account['sc-domain:example.com']
```

**Parameters:**

- **`item`** (int or str): Integer index or exact URL string

**Returns:** `WebProperty` object

**Raises:**

- **`IndexError`**: If integer index is out of range
- **`KeyError`**: If URL not found in accessible properties

---

## Class: `WebProperty`

Represents a specific website property in Google Search Console.

!!! note
    `WebProperty` objects are accessed via `Account` indexing and should not be created directly.

### Attributes

#### `account`

Parent `Account` object.

```python
webproperty.account  # Account
```

#### `url`

The property URL.

```python
webproperty.url  # str
```

**Examples:**

- `"https://www.example.com/"`
- `"sc-domain:example.com"` (Domain property)
- `"android-app://com.example.app/"` (Mobile app)

#### `permission`

Your permission level for this property.

```python
webproperty.permission  # str
```

**Possible values:**

- `"siteOwner"` - Owner
- `"siteFullUser"` - Full user
- `"siteRestrictedUser"` - Restricted user
- `"siteUnverifiedUser"` - Unverified user

#### `query`

Query builder for this property. Starting point for all Search Analytics queries.

```python
webproperty.query  # Query
```

**Example:**

```python
report = webproperty.query.range('today', days=-7).dimension('query').get()
```

#### `raw`

Raw API response data for this property.

```python
webproperty.raw  # dict
```

---

## Class: `Query`

Fluent, immutable query builder for Search Analytics data.

!!! info "Immutable Design"
    All query methods return **new** `Query` objects rather than modifying the original. This allows safe query reuse:
    
    ```python
    base = webproperty.query.range('today', days=-7)
    queries_report = base.dimension('query').get()
    pages_report = base.dimension('page').get()
    # base remains unchanged
    ```

### Query Building Methods

#### `range()`

Define the date range for the query.

```python
query.range(start=None, stop=None, months=0, days=0)
```

**Parameters:**

- **`start`** (str or datetime.date, optional): Start date
    - Date string: `"2024-01-01"`, `"2024/01/01"`
    - Special strings: `"today"`, `"yesterday"`
    - `datetime.date` object
    - Default: yesterday

- **`stop`** (str or datetime.date, optional): End date
    - Same formats as `start`
    - Default: same as `start` (single day)

- **`months`** (int, default=0): Month offset from start date
    - Positive: future
    - Negative: past
    - Cannot combine with both `start` and `stop`

- **`days`** (int, default=0): Day offset from start date
    - Positive: future
    - Negative: past
    - Cannot combine with both `start` and `stop`

**Returns:** New `Query` object

**Examples:**

```python
# Last 7 days
query.range('today', days=-7)

# Last 30 days
query.range('today', days=-30)

# Specific date range
query.range('2024-01-01', '2024-01-31')

# Single day
query.range('yesterday')
query.range('2024-01-15')

# Last 3 months
query.range('today', months=-3)

# Using datetime objects
import datetime
query.range(
    start=datetime.date(2024, 1, 1),
    stop=datetime.date(2024, 1, 31)
)

# 28 days forward from date
query.range('2024-01-01', days=28)
```

!!! warning "Data Retention"
    The API has a 16-month data retention limit. Queries beyond this will return no data.

---

#### `dimension()`

Specify dimensions to include in the report.

```python
query.dimension(*dimensions)
```

**Parameters:**

- **`*dimensions`** (str): One or more dimension names

**Available Dimensions:**

| Dimension | Description | Example Values |
|-----------|-------------|----------------|
| `query` | Search query string | "python tutorial", "learn python" |
| `page` | Landing page URL | "https://example.com/blog/post" |
| `date` | Date of search | "2024-01-15" |
| `country` | Country code (ISO 3166-1 alpha-2) | "usa", "gbr", "fra" |
| `device` | Device type | "desktop", "mobile", "tablet" |
| `searchAppearance` | How result appeared | "RICH_RESULT", "AMP_BLUE_LINK" |

**Returns:** New `Query` object

**Examples:**

```python
# Single dimension
query.dimension('query')
query.dimension('page')

# Multiple dimensions
query.dimension('query', 'page')
query.dimension('query', 'date')
query.dimension('page', 'country', 'device')

# All dimensions
query.dimension('query', 'page', 'date', 'country', 'device', 'searchAppearance')
```

!!! info "Dimension Cardinality"
    More dimensions = more rows. A query with `dimension('query', 'date')` will have many more rows than just `dimension('query')` because each query is broken down by date.

---

#### `filter()`

Filter results by dimension values.

```python
query.filter(dimension, expression, operator="equals", group_type="and")
```

**Parameters:**

- **`dimension`** (str): Dimension to filter on
    - One of: `query`, `page`, `date`, `country`, `device`, `searchAppearance`

- **`expression`** (str): Value to filter by
    - Exact string for `equals`/`notEquals`
    - Substring for `contains`/`notContains`
    - Regex pattern for `includingRegex`/`excludingRegex`

- **`operator`** (str, default="equals"): Filter operator

**Filter Operators:**

| Operator | Description | Example |
|----------|-------------|---------|
| `equals` | Exact match | `filter('country', 'usa', 'equals')` |
| `contains` | Contains substring | `filter('query', 'python', 'contains')` |
| `notEquals` | Not equal to | `filter('device', 'tablet', 'notEquals')` |
| `notContains` | Doesn't contain | `filter('page', '/admin/', 'notContains')` |
| `includingRegex` | Matches regex | `filter('page', r'/blog/\d+/', 'includingRegex')` |
| `excludingRegex` | Doesn't match | `filter('query', r'^test', 'excludingRegex')` |

- **`group_type`** (str, default="and"): How to combine filters
    - Currently only `"and"` is supported by the API

**Returns:** New `Query` object

**Examples:**

```python
# Contains filter
query.filter('query', 'python', 'contains')

# Page filter
query.filter('page', '/blog/', 'contains')
query.filter('page', 'https://www.example.com/about/', 'equals')

# Country filter
query.filter('country', 'usa', 'equals')

# Device filter
query.filter('device', 'mobile', 'equals')

# Regex filters (RE2 syntax)
query.filter('page', r'/blog/\d{4}/\d{2}/', 'includingRegex')
query.filter('query', r'^(buy|purchase|order)', 'includingRegex')

# Exclude filters
query.filter('page', '/admin/', 'notContains')
query.filter('query', 'test', 'notContains')

# Multiple filters (chain them)
(
    query
    .filter('query', 'python', 'contains')
    .filter('page', '/blog/', 'contains')
    .filter('country', 'usa', 'equals')
    .filter('device', 'mobile', 'equals')
)
```

!!! note "Regex Syntax"
    Regex patterns must follow [RE2 syntax](https://github.com/google/re2/wiki/Syntax), which is similar to but not identical to Python's `re` module.

---

#### `search_type()`

Filter by search type.

```python
query.search_type(search_type)
```

**Parameters:**

- **`search_type`** (str): Type of search

**Available Search Types:**

| Type | Description | Position Data? |
|------|-------------|----------------|
| `web` | Regular web search (default) | ✅ Yes |
| `image` | Image search | ✅ Yes |
| `video` | Video search | ✅ Yes |
| `news` | News search | ✅ Yes |
| `discover` | Google Discover | ❌ No |
| `googleNews` | Google News | ❌ No |

**Returns:** New `Query` object

**Examples:**

```python
# Image search
query.search_type('image')

# Video search
query.search_type('video')

# Google Discover (no position data)
query.search_type('discover')

# News search
query.search_type('news')
```

!!! warning "Position Metric"
    `discover` and `googleNews` search types do **not** return position data. The `position` metric will not be available in reports.

---

#### `data_state()`

Include fresh (non-finalized) data in results.

```python
query.data_state(data_state)
```

**Parameters:**

- **`data_state`** (str): Data freshness level
    - `"final"` (default): Only finalized data
    - `"all"`: Both finalized and fresh data (< 1 day old)

**Returns:** New `Query` object

**Examples:**

```python
# Include fresh data
query.data_state('all')

# Only final data (default)
query.data_state('final')
```

!!! info "Data Freshness"
    Fresh data may be replaced with final data after a few days. Use `"all"` for the most up-to-date data.

---

#### `limit()`

Limit the number of rows returned.

```python
query.limit(limit)
query.limit(limit, start)
```

**Parameters:**

- **`limit`** (int): Number of rows to return
- **`start`** (int, optional): Starting position (0-indexed)

**Returns:** New `Query` object

**Examples:**

```python
# First 10 rows
query.limit(10)

# First 100 rows
query.limit(100)

# Rows 100-199 (pagination)
query.limit(100, 100)

# Rows 200-299
query.limit(100, 200)

# Large limit (auto-paginated)
query.limit(50000)  # Will make multiple API calls
```

!!! note "API Limit"
    The API returns a maximum of 25,000 rows per request. The library automatically handles pagination for larger limits.

---

### Query Execution Methods

#### `get()`

Execute the query and return all results.

```python
query.get()
```

**Returns:** `Report` object with all matching rows

**Examples:**

```python
# Build and execute
report = (
    webproperty.query
    .range('today', days=-7)
    .dimension('query')
    .get()
)

# With multiple operations
report = (
    webproperty.query
    .range('today', days=-30)
    .dimension('query', 'page')
    .filter('query', 'python', 'contains')
    .limit(1000)
    .get()
)
```

!!! info "Automatic Pagination"
    `get()` automatically handles pagination if results exceed the per-request limit or your specified limit.

---

#### `execute()`

Execute a single request (one page of results).

```python
query.execute()
```

**Returns:** `Report` object with single page of results

!!! note
    Usually you want `get()` instead, which fetches all pages automatically.

---

### Utility Methods

#### `build()`

Build the query parameters without executing.

```python
query.build(copy=True)
```

**Parameters:**

- **`copy`** (bool, default=True): Whether to return a copy of parameters

**Returns:** Dictionary of query parameters

**Example:**

```python
params = (
    webproperty.query
    .range('today', days=-7)
    .dimension('query')
    .filter('page', '/blog/', 'contains')
    .build()
)

print(params)
# {
#     'startDate': '2024-11-08',
#     'endDate': '2024-11-15',
#     'dimensions': ['query'],
#     'dimensionFilterGroups': [{
#         'filters': [{
#             'dimension': 'page',
#             'expression': '/blog/',
#             'operator': 'contains'
#         }]
#     }],
#     'startRow': 0,
#     'rowLimit': 25000
# }
```

---

## Class: `Report`

Contains the results of an executed query.

!!! note
    `Report` objects are created by `Query.get()` or `Query.execute()` and should not be instantiated directly.

### Attributes

#### `dimensions`

List of dimension names in the report.

```python
report.dimensions  # List[str]
```

**Example:**

```python
report = query.dimension('query', 'page').get()
print(report.dimensions)  # ['query', 'page']
```

#### `metrics`

List of metric names in the report.

```python
report.metrics  # List[str]
```

**Standard metrics:**

- `clicks` (int)
- `impressions` (int)
- `ctr` (float)
- `position` (float) - Not available for discover/googleNews

**Example:**

```python
print(report.metrics)  # ['clicks', 'impressions', 'ctr', 'position']
```

#### `columns`

All column names (dimensions + metrics).

```python
report.columns  # List[str]
```

**Example:**

```python
print(report.columns)  # ['query', 'page', 'clicks', 'impressions', 'ctr', 'position']
```

#### `rows`

List of data rows as named tuples.

```python
report.rows  # List[Row]
```

**Example:**

```python
for row in report.rows:
    print(row.query, row.clicks)
```

#### `Row`

Named tuple class for rows. Provides both attribute and dictionary-style access.

```python
row = report.rows[0]

# Attribute access
print(row.query)
print(row.clicks)
print(row.impressions)

# Dictionary access
print(row['query'])
print(row['clicks'])
```

#### `is_complete`

Whether all data has been fetched.

```python
report.is_complete  # bool
```

### Properties

#### `first`

First row in the report, or `None` if empty.

```python
report.first  # Row or None
```

**Example:**

```python
if report.first:
    print(f"Top query: {report.first.query}")
```

#### `last`

Last row in the report, or `None` if empty.

```python
report.last  # Row or None
```

### Methods

#### `to_dict()`

Convert report to list of dictionaries.

```python
report.to_dict()
```

**Returns:** List of dictionaries, one per row

**Example:**

```python
data = report.to_dict()
print(data[0])
# {
#     'query': 'python tutorial',
#     'clicks': 150,
#     'impressions': 2500,
#     'ctr': 0.06,
#     'position': 5.2
# }

# Save to JSON
import json
with open('data.json', 'w') as f:
    json.dump(data, f, indent=2)
```

---

#### `to_dataframe()`

Convert report to pandas DataFrame.

```python
report.to_dataframe()
```

**Returns:** `pandas.DataFrame`

**Requires:** pandas library

**Example:**

```python
df = report.to_dataframe()

print(df.head())
print(df.info())
print(df.describe())

# Pandas operations
print(df['clicks'].sum())
print(df.groupby('country')['clicks'].sum())

# Save to CSV
df.to_csv('report.csv', index=False)

# Save to Excel
df.to_excel('report.xlsx', index=False)
```

### Iteration and Indexing

#### Iteration

```python
for row in report:
    print(row.query, row.clicks)
```

#### Length

```python
num_rows = len(report)
print(f"Report has {num_rows} rows")
```

#### Indexing

```python
# First row
first = report[0]

# Last row
last = report[-1]

# Slice
first_ten = report[:10]
next_ten = report[10:20]
```

#### Contains

```python
if some_row in report:
    print("Row found in report")
```

---

## Utility Functions

### `serialize()`

Convert date object to ISO format string.

```python
searchconsole.utils.serialize(date)
```

**Parameters:**

- **`date`** (datetime.date or str): Date to serialize

**Returns:** ISO format string (YYYY-MM-DD) or original string

---

### `normalize()`

Normalize various date formats to `datetime.date`.

```python
searchconsole.utils.normalize(obj)
```

**Parameters:**

- **`obj`** (str, datetime.date, or None): Date in various formats

**Returns:** `datetime.date` object or `None`

**Supported formats:**

- `None` → `None`
- `datetime.date` objects → returned as-is
- `datetime.datetime` objects → converted to date
- Date strings: `"2024-01-01"`, `"2024/01/01"`, etc.
- Special strings: `"today"`, `"yesterday"`

---

### `daterange()`

Calculate date range with offsets.

```python
searchconsole.utils.daterange(start=None, stop=None, days=0, months=0)
```

**Parameters:**

- **`start`** (str, datetime.date, or None): Start date (default: yesterday)
- **`stop`** (str, datetime.date, or None): End date (default: same as start)
- **`days`** (int): Day offset
- **`months`** (int): Month offset

**Returns:** Tuple of two ISO format date strings (start, stop), sorted chronologically

**Example:**

```python
from searchconsole.utils import daterange

# Last 7 days
start, end = daterange('today', days=-7)
print(start, end)  # ('2024-11-08', '2024-11-15')
```

---

## Complete Example

Putting it all together:

```python
import searchconsole

# 1. Authenticate
account = searchconsole.authenticate(
    client_config='client_secrets.json',
    credentials='credentials.json'
)

# 2. Select property
webproperty = account['https://www.example.com/']
print(f"Permission: {webproperty.permission}")

# 3. Build complex query
report = (
    webproperty.query
    .range('today', days=-30)
    .dimension('query', 'page', 'country')
    .filter('query', 'python', 'contains')
    .filter('page', '/blog/', 'contains')
    .filter('country', 'usa', 'equals')
    .search_type('web')
    .data_state('all')
    .limit(1000)
    .get()
)

# 4. Analyze results
print(f"Total rows: {len(report)}")
print(f"Dimensions: {report.dimensions}")
print(f"Metrics: {report.metrics}")

# 5. Access data
for row in report[:10]:
    print(f"{row.query} on {row.page}")
    print(f"  Country: {row.country}")
    print(f"  Clicks: {row.clicks}, Impressions: {row.impressions}")
    print(f"  CTR: {row.ctr:.2%}, Position: {row.position:.1f}\n")

# 6. Export
df = report.to_dataframe()
df.to_csv('search_console_data.csv', index=False)

data = report.to_dict()
import json
with open('search_console_data.json', 'w') as f:
    json.dump(data, f, indent=2)
```
