---
icon: lucide/lightbulb
---

# Examples

Practical examples and common use cases for the Google Search Console library.

## Basic Examples

### Top Performing Queries

Get your top 10 performing queries for the last 30 days:

```python
import searchconsole

account = searchconsole.authenticate(
    client_config='client_secrets.json',
    credentials='credentials.json'
)

webproperty = account['https://www.example.com/']

# Query top queries
report = (
    webproperty.query
    .range('today', days=-30)
    .dimension('query')
    .limit(10)
    .get()
)

print("Top 10 Queries (Last 30 Days)\n" + "="*50)
for i, row in enumerate(report, 1):
    print(f"{i:2d}. {row.query}")
    print(f"    Clicks: {row.clicks:>6,} | Impressions: {row.impressions:>8,}")
    print(f"    CTR: {row.ctr:>6.2%} | Avg Position: {row.position:>5.1f}\n")
```

### Top Pages by Traffic

Find which pages are driving the most traffic:

```python
report = (
    webproperty.query
    .range('today', days=-30)
    .dimension('page')
    .limit(20)
    .get()
)

# Convert to DataFrame for easier analysis
df = report.to_dataframe()

# Sort by clicks
top_pages = df.nlargest(10, 'clicks')

print("Top 10 Pages by Clicks\n")
for idx, row in top_pages.iterrows():
    print(f"{row['page']}")
    print(f"  {row['clicks']:,} clicks, {row['impressions']:,} impressions\n")
```

### Track Specific Keywords

Monitor performance of specific keywords over time:

```python
keywords = ['python tutorial', 'learn python', 'python for beginners']

for keyword in keywords:
    report = (
        webproperty.query
        .range('today', days=-90)
        .dimension('date')
        .filter('query', keyword, 'equals')
        .get()
    )
    
    df = report.to_dataframe()
    
    print(f"\n{keyword.upper()}")
    print(f"Total clicks: {df['clicks'].sum():,}")
    print(f"Total impressions: {df['impressions'].sum():,}")
    print(f"Average position: {df['position'].mean():.1f}")
```

## Analysis Examples

### Click-Through Rate Analysis

Analyze CTR by position range:

```python
import pandas as pd

# Get query-level data
report = (
    webproperty.query
    .range('today', days=-30)
    .dimension('query')
    .get()
)

df = report.to_dataframe()

# Categorize by position
df['position_range'] = pd.cut(
    df['position'],
    bins=[0, 3, 5, 10, 20, 100],
    labels=['1-3', '4-5', '6-10', '11-20', '20+']
)

# Analyze by position range
analysis = df.groupby('position_range').agg({
    'clicks': 'sum',
    'impressions': 'sum',
    'ctr': 'mean',
    'position': 'mean'
}).round(4)

print(analysis)
```

### Geographic Performance

Compare performance across countries:

```python
report = (
    webproperty.query
    .range('today', days=-30)
    .dimension('country')
    .get()
)

df = report.to_dataframe()

# Sort by clicks
df = df.sort_values('clicks', ascending=False)

print("Performance by Country\n")
print(df.head(10).to_string(index=False))

# Calculate percentage of total
df['click_share'] = (df['clicks'] / df['clicks'].sum() * 100).round(2)

top_5 = df.head(5)
print(f"\nTop 5 Countries Account for {top_5['click_share'].sum():.1f}% of Clicks")
```

### Device Breakdown

Analyze traffic by device type:

```python
report = (
    webproperty.query
    .range('today', days=-30)
    .dimension('device')
    .get()
)

df = report.to_dataframe()

print("Performance by Device\n")
for _, row in df.iterrows():
    print(f"{row['device'].upper()}")
    print(f"  Clicks: {row['clicks']:,}")
    print(f"  Impressions: {row['impressions']:,}")
    print(f"  CTR: {row['ctr']:.2%}")
    print(f"  Avg Position: {row['position']:.1f}\n")

# Calculate device share
df['device_share'] = (df['clicks'] / df['clicks'].sum() * 100)

print("Click Share by Device:")
for _, row in df.iterrows():
    print(f"  {row['device']}: {row['device_share']:.1f}%")
```

### Trend Analysis

Track performance trends over time:

```python
import matplotlib.pyplot as plt

# Get daily data for the last 90 days
report = (
    webproperty.query
    .range('today', days=-90)
    .dimension('date')
    .get()
)

df = report.to_dataframe()
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date')

# Plot trends
fig, axes = plt.subplots(2, 2, figsize=(15, 10))

# Clicks trend
axes[0, 0].plot(df['date'], df['clicks'], marker='o')
axes[0, 0].set_title('Clicks Over Time')
axes[0, 0].set_xlabel('Date')
axes[0, 0].set_ylabel('Clicks')

# Impressions trend
axes[0, 1].plot(df['date'], df['impressions'], marker='o', color='orange')
axes[0, 1].set_title('Impressions Over Time')
axes[0, 1].set_xlabel('Date')
axes[0, 1].set_ylabel('Impressions')

# CTR trend
axes[1, 0].plot(df['date'], df['ctr'] * 100, marker='o', color='green')
axes[1, 0].set_title('CTR Over Time')
axes[1, 0].set_xlabel('Date')
axes[1, 0].set_ylabel('CTR (%)')

# Position trend
axes[1, 1].plot(df['date'], df['position'], marker='o', color='red')
axes[1, 1].set_title('Average Position Over Time')
axes[1, 1].set_xlabel('Date')
axes[1, 1].set_ylabel('Position')
axes[1, 1].invert_yaxis()  # Lower position is better

plt.tight_layout()
plt.savefig('search_console_trends.png')
print("Trend chart saved to search_console_trends.png")
```

## Content Analysis Examples

### Blog Post Performance

Analyze all blog posts:

```python
# Get all pages containing '/blog/'
report = (
    webproperty.query
    .range('today', days=-30)
    .dimension('page')
    .filter('page', '/blog/', 'contains')
    .get()
)

df = report.to_dataframe()

print(f"Total blog posts: {len(df)}")
print(f"Total blog clicks: {df['clicks'].sum():,}")
print(f"Total blog impressions: {df['impressions'].sum():,}")

# Top performing blog posts
top_blogs = df.nlargest(10, 'clicks')

print("\nTop 10 Blog Posts:\n")
for idx, row in top_blogs.iterrows():
    # Extract title from URL (customize as needed)
    title = row['page'].split('/')[-2].replace('-', ' ').title()
    print(f"{title}")
    print(f"  URL: {row['page']}")
    print(f"  Clicks: {row['clicks']:,} | Impressions: {row['impressions']:,}")
    print(f"  CTR: {row['ctr']:.2%} | Position: {row['position']:.1f}\n")
```

### Find Underperforming Pages

Identify pages with high impressions but low clicks:

```python
report = (
    webproperty.query
    .range('today', days=-30)
    .dimension('page')
    .get()
)

df = report.to_dataframe()

# Filter for pages with significant impressions
significant_pages = df[df['impressions'] >= 100].copy()

# Sort by CTR (ascending) to find underperformers
underperformers = significant_pages.nsmallest(10, 'ctr')

print("Top 10 Underperforming Pages (High Impressions, Low CTR)\n")
for idx, row in underperformers.iterrows():
    print(f"{row['page']}")
    print(f"  Impressions: {row['impressions']:,} | Clicks: {row['clicks']}")
    print(f"  CTR: {row['ctr']:.2%} | Position: {row['position']:.1f}")
    print(f"  💡 Opportunity: Improve meta description or title tag\n")
```

### Content Gap Analysis

Find queries where you rank but have low clicks:

```python
# Get queries with position in top 10 but low CTR
report = (
    webproperty.query
    .range('today', days=-30)
    .dimension('query')
    .get()
)

df = report.to_dataframe()

# Filter for top 10 positions with at least 50 impressions
top_10 = df[(df['position'] <= 10) & (df['impressions'] >= 50)].copy()

# Sort by CTR to find opportunities
opportunities = top_10.nsmallest(20, 'ctr')

print("Ranking Opportunities (Top 10 Position, Low CTR)\n")
for idx, row in opportunities.iterrows():
    print(f"Query: {row['query']}")
    print(f"  Position: {row['position']:.1f} | CTR: {row['ctr']:.2%}")
    print(f"  Clicks: {row['clicks']} | Impressions: {row['impressions']}")
    print(f"  💡 Consider: Optimizing for featured snippets or improving title\n")
```

## Comparison Examples

### Month-over-Month Comparison

Compare current month to previous month:

```python
import datetime

# Current month data
this_month_start = datetime.date.today().replace(day=1)
this_month_report = (
    webproperty.query
    .range(this_month_start, 'today')
    .dimension('query')
    .get()
)

# Previous month data
last_month_end = this_month_start - datetime.timedelta(days=1)
last_month_start = last_month_end.replace(day=1)
last_month_report = (
    webproperty.query
    .range(last_month_start, last_month_end)
    .dimension('query')
    .get()
)

# Convert to DataFrames
this_month_df = this_month_report.to_dataframe()
last_month_df = last_month_report.to_dataframe()

# Compare totals
this_month_clicks = this_month_df['clicks'].sum()
last_month_clicks = last_month_df['clicks'].sum()
change = ((this_month_clicks - last_month_clicks) / last_month_clicks * 100)

print(f"Month-over-Month Performance\n{'='*50}")
print(f"\nThis Month:")
print(f"  Clicks: {this_month_clicks:,}")
print(f"  Impressions: {this_month_df['impressions'].sum():,}")

print(f"\nLast Month:")
print(f"  Clicks: {last_month_clicks:,}")
print(f"  Impressions: {last_month_df['impressions'].sum():,}")

print(f"\nChange: {change:+.1f}%")
```

### Year-over-Year Comparison

Compare to the same period last year:

```python
import datetime

# This year (last 30 days)
this_year_report = (
    webproperty.query
    .range('today', days=-30)
    .dimension('date')
    .get()
)

# Last year (same 30-day period)
days_ago_365 = datetime.date.today() - datetime.timedelta(days=365)
days_ago_395 = days_ago_365 - datetime.timedelta(days=30)

last_year_report = (
    webproperty.query
    .range(days_ago_395, days_ago_365)
    .dimension('date')
    .get()
)

# Compare
this_year_df = this_year_report.to_dataframe()
last_year_df = last_year_report.to_dataframe()

metrics = {
    'Clicks': ('clicks', this_year_df['clicks'].sum(), last_year_df['clicks'].sum()),
    'Impressions': ('impressions', this_year_df['impressions'].sum(), last_year_df['impressions'].sum()),
    'CTR': ('ctr', this_year_df['ctr'].mean(), last_year_df['ctr'].mean()),
    'Position': ('position', this_year_df['position'].mean(), last_year_df['position'].mean()),
}

print("Year-over-Year Comparison (Last 30 Days)\n")
for metric_name, (col, this_year, last_year) in metrics.items():
    change = ((this_year - last_year) / last_year * 100) if last_year > 0 else 0
    print(f"{metric_name}:")
    print(f"  This Year: {this_year:,.2f}")
    print(f"  Last Year: {last_year:,.2f}")
    print(f"  Change: {change:+.1f}%\n")
```

## Search Type Examples

### Image Search Analysis

Analyze image search performance:

```python
# Get image search data
image_report = (
    webproperty.query
    .search_type('image')
    .range('today', days=-30)
    .dimension('page')
    .get()
)

df = image_report.to_dataframe()

print("Image Search Performance\n")
print(f"Total clicks: {df['clicks'].sum():,}")
print(f"Total impressions: {df['impressions'].sum():,}")
print(f"Average CTR: {df['ctr'].mean():.2%}")

# Top performing image pages
top_images = df.nlargest(10, 'clicks')
print("\nTop 10 Pages for Image Search:\n")
for idx, row in top_images.iterrows():
    print(f"{row['page']}")
    print(f"  Clicks: {row['clicks']:,} | Impressions: {row['impressions']:,}\n")
```

### Compare Search Types

Compare performance across different search types:

```python
search_types = ['web', 'image', 'video', 'news']

results = []
for search_type in search_types:
    try:
        report = (
            webproperty.query
            .search_type(search_type)
            .range('today', days=-30)
            .dimension('page')
            .get()
        )
        
        df = report.to_dataframe()
        
        results.append({
            'search_type': search_type,
            'clicks': df['clicks'].sum(),
            'impressions': df['impressions'].sum(),
            'ctr': df['ctr'].mean()
        })
    except Exception as e:
        print(f"No data for {search_type}: {e}")

# Display comparison
import pandas as pd
comparison_df = pd.DataFrame(results)

print("Search Type Comparison\n")
print(comparison_df.to_string(index=False))

# Visualize
comparison_df.plot(
    x='search_type',
    y=['clicks', 'impressions'],
    kind='bar',
    title='Clicks and Impressions by Search Type'
)
```

### Google Discover Performance

Analyze Google Discover traffic:

```python
# Note: Discover doesn't return position data
discover_report = (
    webproperty.query
    .search_type('discover')
    .range('today', days=-30)
    .dimension('page')
    .get()
)

df = discover_report.to_dataframe()

print("Google Discover Performance (Last 30 Days)\n")
print(f"Total clicks: {df['clicks'].sum():,}")
print(f"Total impressions: {df['impressions'].sum():,}")
print(f"Average CTR: {df['ctr'].mean():.2%}")

# Top Discover pages
top_discover = df.nlargest(10, 'clicks')
print("\nTop 10 Pages in Discover:\n")
for idx, row in top_discover.iterrows():
    print(f"{row['page']}")
    print(f"  Clicks: {row['clicks']:,} | CTR: {row['ctr']:.2%}\n")
```

## Advanced Filtering Examples

### Multi-Filter Analysis

Analyze mobile traffic from USA for blog posts:

```python
report = (
    webproperty.query
    .range('today', days=-30)
    .dimension('query', 'page')
    .filter('page', '/blog/', 'contains')
    .filter('country', 'usa', 'equals')
    .filter('device', 'mobile', 'equals')
    .get()
)

df = report.to_dataframe()

print("Mobile Traffic (USA) for Blog Posts\n")
print(f"Total clicks: {df['clicks'].sum():,}")
print(f"Unique queries: {df['query'].nunique()}")
print(f"Unique pages: {df['page'].nunique()}")

# Top queries for this segment
top_queries = df.groupby('query').agg({
    'clicks': 'sum',
    'impressions': 'sum'
}).nlargest(10, 'clicks')

print("\nTop 10 Mobile Queries (USA, Blog):\n")
print(top_queries)
```

### Regex Filtering

Find all date-based URLs:

```python
# Find URLs matching pattern /blog/YYYY/MM/
report = (
    webproperty.query
    .range('today', days=-30)
    .dimension('page')
    .filter('page', r'/blog/\d{4}/\d{2}/', 'includingRegex')
    .get()
)

df = report.to_dataframe()

print(f"Found {len(df)} blog posts with date-based URLs\n")

# Extract year and month
import re

def extract_date(url):
    match = re.search(r'/blog/(\d{4})/(\d{2})/', url)
    if match:
        return f"{match.group(1)}-{match.group(2)}"
    return None

df['year_month'] = df['page'].apply(extract_date)

# Analyze by year-month
monthly_performance = df.groupby('year_month').agg({
    'clicks': 'sum',
    'impressions': 'sum',
    'page': 'count'
}).rename(columns={'page': 'num_posts'})

print("Performance by Publication Month:\n")
print(monthly_performance.sort_index(ascending=False))
```

### Exclude Internal Pages

Filter out admin and internal pages:

```python
# Get all pages except admin, staging, or test pages
report = (
    webproperty.query
    .range('today', days=-30)
    .dimension('page')
    .filter('page', '/admin/', 'notContains')
    .filter('page', 'staging.', 'notContains')
    .filter('page', '/test/', 'notContains')
    .get()
)

df = report.to_dataframe()

print(f"Public pages: {len(df)}")
print(f"Total clicks: {df['clicks'].sum():,}")
```

## Next Steps

- **[API Reference](api-reference.md)** - Complete API documentation
- **[Contributing](contributing.md)** - Help improve the library
