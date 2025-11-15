---
icon: lucide/rocket
---

# Getting Started

This guide will help you get up and running with the Google Search Console Python library in just a few minutes.

## Prerequisites

- Python 3.8 or higher
- A Google account with access to Google Search Console
- At least one verified website property in Search Console

## Installation

Install the library directly from GitHub:

```bash
pip install git+https://github.com/joshcarty/google-searchconsole
```

## Setup Google API Credentials {#setup-credentials}

Before you can use the library, you need to set up API credentials in the Google Developers Console.

### Step 1: Create a Google Cloud Project

1. Go to the [Google Developers Console](https://console.developers.google.com/)
2. Click **Create Project**
3. Enter a project name (e.g., "Search Console API")
4. Click **Create**

### Step 2: Enable the Search Console API

1. In your project, go to **APIs & Services** > **Library**
2. Search for "Google Search Console API"
3. Click on it and press **Enable**

### Step 3: Create OAuth2 Credentials

1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth client ID**
3. If prompted, configure the OAuth consent screen:
    - Choose **External** user type (unless you have a Google Workspace account)
    - Fill in the required fields (app name, user support email, developer email)
    - Add your email as a test user
    - Click **Save and Continue** through the scopes and summary
4. Back at **Create OAuth client ID**:
    - Choose **Desktop app** as the application type
    - Give it a name (e.g., "Search Console Python Client")
    - Click **Create**
5. Download the JSON file by clicking the download icon
6. Save it as `client_secrets.json` in your project directory

!!! warning "Keep Your Credentials Secure"
    Never commit `client_secrets.json` or `credentials.json` to version control. Add them to your `.gitignore` file.

## Your First Query

Now you're ready to authenticate and run your first query!

### Step 1: Authenticate

Create a Python file and add the following code:

```python
import searchconsole

# First-time authentication (interactive)
account = searchconsole.authenticate(client_config='client_secrets.json')
```

When you run this code, it will:

1. Open a browser window for you to log in
2. Ask you to grant permissions to the application
3. Return an authenticated `Account` object

!!! tip "Save Your Credentials"
    To avoid the OAuth flow every time, save your credentials:
    
    ```python
    # First time: authenticate and save
    account = searchconsole.authenticate(client_config='client_secrets.json')
    account.serialize_credentials('credentials.json')
    
    # Future runs: load saved credentials
    account = searchconsole.authenticate(client_config='client_secrets.json', credentials='credentials.json')
    ```

### Step 2: Select a Web Property

List your available properties:

```python
# View all properties
for property in account.webproperties:
    print(f"URL: {property.url}, Permission: {property.permission}")
```

Select the property you want to work with:

```python
# By URL
webproperty = account['https://www.example.com/']

# Or by index
webproperty = account[0]  # First property
```

### Step 3: Build and Execute a Query

Query the last 7 days of search queries:

```python
# Build the query
query = webproperty.query.range('today', days=-7).dimension('query')

# Execute and get results
report = query.get()

# Print results
print(f"Found {len(report)} rows")

for row in report:
    print(f"Query: {row.query}")
    print(f"  Clicks: {row.clicks}")
    print(f"  Impressions: {row.impressions}")
    print(f"  CTR: {row.ctr:.2%}")
    print(f"  Position: {row.position:.1f}")
    print()
```

### Complete Example

Here's a complete working example:

```python
import searchconsole

# Authenticate
account = searchconsole.authenticate(client_config='client_secrets.json', credentials='credentials.json')

# Select property
webproperty = account['https://www.example.com/']

# Query top queries from the last 7 days
report = (
    webproperty.query
    .range('today', days=-7)
    .dimension('query')
    .limit(10)
    .get()
)

# Display results
print(f"Top 10 queries from the last 7 days:\n")
for i, row in enumerate(report, 1):
    print(f"{i}. {row.query}")
    print(f"   Clicks: {row.clicks}, Impressions: {row.impressions}, "
          f"CTR: {row.ctr:.2%}, Avg Position: {row.position:.1f}\n")
```

Expected output:

```
Top 10 queries from the last 7 days:

1. python tutorial
   Clicks: 150, Impressions: 2500, CTR: 6.00%, Avg Position: 5.2

2. learn python
   Clicks: 120, Impressions: 1800, CTR: 6.67%, Avg Position: 4.8

3. python for beginners
   Clicks: 95, Impressions: 1200, CTR: 7.92%, Avg Position: 3.5
...
```

## Export Data

### To Pandas DataFrame

```python
# Export to pandas (requires pandas to be installed)
df = report.to_dataframe()

print(df.head())
print(f"\nTotal clicks: {df['clicks'].sum()}")
print(f"Total impressions: {df['impressions'].sum()}")

# Save to CSV
df.to_csv('search_data.csv', index=False)
```

## Common Query Patterns

### Date Ranges

```python
# Last 7 days
query = webproperty.query.range('today', days=-7)

# Last 30 days
query = webproperty.query.range('today', days=-30)

# Specific date range
query = webproperty.query.range('2024-01-01', '2024-01-31')

# Yesterday only
query = webproperty.query.range('yesterday')

# Last 3 months
query = webproperty.query.range('today', months=-3)
```

### Multiple Dimensions

```python
# Queries by page
report = (
    webproperty.query
    .range('today', days=-7)
    .dimension('query', 'page')
    .get()
)

# Queries by date
report = (
    webproperty.query
    .range('today', days=-30)
    .dimension('query', 'date')
    .get()
)

# Pages by country and device
report = (
    webproperty.query
    .range('today', days=-7)
    .dimension('page', 'country', 'device')
    .get()
)
```

### Filtering

```python
# Filter by query containing "python"
report = (
    webproperty.query
    .range('today', days=-7)
    .dimension('query')
    .filter('query', 'python', 'contains')
    .get()
)

# Filter by specific page
report = (
    webproperty.query
    .range('today', days=-7)
    .dimension('query')
    .filter('page', 'https://www.example.com/blog/', 'equals')
    .get()
)

# Multiple filters
report = (
    webproperty.query
    .range('today', days=-7)
    .dimension('query')
    .filter('page', '/blog/', 'contains')
    .filter('country', 'usa', 'equals')
    .get()
)
```

## Troubleshooting

### Browser Doesn't Open During OAuth Flow

If your browser doesn't open or you get an error:

```
OSError: [Errno 98] Address already in use
```

Try use the console flow instead:

```python
account = searchconsole.authenticate(client_config='client_secrets.json', flow='console')
```

This will print a URL you can copy and paste into your browser.

### No Data Returned

Check:

- Your date range is valid (API has 16-month limit)
- Your filters aren't too restrictive
- The property has data for the selected period
- You're using the correct search type (web, image, etc.)

## Next Steps

Now that you've got the basics down, explore:

- **[Authentication Guide](authentication.md)** - Learn about different authentication methods
- **[API Reference](api-reference.md)** - Detailed documentation of all methods
- **[Examples](examples.md)** - More complex query examples and use cases

## Quick Reference

### Common Dimensions

| Dimension | Description | Example Values |
|-----------|-------------|----------------|
| `query` | Search query | "python tutorial", "learn coding" |
| `page` | Landing page URL | "https://example.com/blog/post" |
| `date` | Date of search | "2024-01-15" |
| `country` | Country code | "usa", "gbr", "can" |
| `device` | Device type | "desktop", "mobile", "tablet" |
| `searchAppearance` | Search feature | "RICH_RESULT", "AMP_BLUE_LINK" |

### Common Filter Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `equals` | Exact match | `.filter('country', 'usa', 'equals')` |
| `contains` | Contains substring | `.filter('query', 'python', 'contains')` |
| `notEquals` | Not equal to | `.filter('device', 'tablet', 'notEquals')` |
| `notContains` | Doesn't contain | `.filter('page', '/admin/', 'notContains')` |
| `includingRegex` | Matches regex | `.filter('page', r'/blog/\d+/', 'includingRegex')` |
| `excludingRegex` | Doesn't match regex | `.filter('query', r'^test', 'excludingRegex')` |

### Search Types

| Type | Description |
|------|-------------|
| `web` | Regular web search (default) |
| `image` | Image search |
| `video` | Video search |
| `news` | News search |
| `discover` | Google Discover (no position data) |
| `googleNews` | Google News (no position data) |
