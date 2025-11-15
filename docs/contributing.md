---
icon: lucide/users
---

# Contributing

Thank you for your interest in contributing to the Google Search Console Python library! This guide will help you get started.

## Ways to Contribute

There are many ways to contribute to this project:

- **Report bugs** - Found an issue? Let us know!
- **Suggest features** - Have an idea for improvement? We'd love to hear it!
- **Share examples** - Show others how you're using the library
- **Improve documentation** - Help make the docs clearer and more comprehensive
- **Submit code** - Fix bugs or implement new features

## Getting Started

### 1. Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:

```bash
git clone https://github.com/YOUR_USERNAME/google-searchconsole.git
cd google-searchconsole
```

### 2. Set Up Development Environment

We recommend using [uv](https://docs.astral.sh/uv/) for dependency management:

```bash
# Install dependencies
uv sync

# Or using pip
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### 3. Create a Branch

Create a branch for your work:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

Use descriptive branch names:
- `feature/add-bulk-query-support`
- `fix/pagination-edge-case`
- `docs/improve-authentication-guide`

## Development Workflow

### Running Tests

The project uses Python's built-in `unittest` framework.

#### Prerequisites

Tests require authentication credentials set as environment variables:

```bash
export SEARCHCONSOLE_CLIENT_CONFIG='{"installed": {...}}'
export SEARCHCONSOLE_CREDENTIALS='{"token": "...", ...}'
export SEARCHCONSOLE_WEBPROPERTY_URI='https://www.example.com/'
```

Or use a `.env` file with `python-dotenv`:

```bash
# .env
SEARCHCONSOLE_CLIENT_CONFIG={"installed": {...}}
SEARCHCONSOLE_CREDENTIALS={"token": "...", ...}
SEARCHCONSOLE_WEBPROPERTY_URI=https://www.example.com/
```

#### Run Tests

```bash
# Using uv
uv run python -m unittest tests

# Using pip
python -m unittest tests

# Run with tox (tests multiple Python versions)
tox

# Run specific test file
python -m unittest tests.TestQuery
```

### Code Quality

#### Linting and Formatting

The project uses [Ruff](https://docs.astral.sh/ruff/) for linting and formatting:

```bash
# Check code quality
tox -e lint

# Auto-format code
tox -e format

# Or run ruff directly
ruff check src/searchconsole tests.py
ruff format src/searchconsole tests.py
```

#### Code Style Guidelines

- Follow [PEP 8](https://pep8.org/) style guide

Example:

```python
def filter(dimension=expression, operator="equals", group_type="and"):
    """
    Filter results by dimension values.
    
    Args:
        dimension: Dimension to filter on (query, page, date, country, device, searchAppearance)
        expression: Value to filter by
        operator: Filter operator (equals, contains, notContains, etc.)
        group_type: How to combine multiple filters (default: "and")
    
    Returns:
        New Query object with filter applied
    
    Example:
        >>> query.filter('country', 'usa', 'equals')
        >>> query.filter('query', 'python', 'contains')
    """
    # Implementation
    pass
```

### Testing Guidelines

#### Writing Tests

Add tests for new features or bug fixes:

```python
import unittest
from searchconsole import Query

class TestNewFeature(unittest.TestCase):
    def test_feature_works(self):
        """Test that the new feature works as expected."""
        # Setup
        query = Query(...)
        
        # Execute
        result = query.new_feature()
        
        # Assert
        self.assertEqual(result.something, expected_value)
    
    def test_feature_edge_case(self):
        """Test edge case handling."""
        query = Query(...)
        
        with self.assertRaises(ValueError):
            query.new_feature(invalid_input)
```

#### Test Coverage

Run tests with coverage reporting:

```bash
# Using tox
tox -e coverage

# Or directly
coverage run -m unittest tests
coverage report -m
coverage html  # Generates HTML report in htmlcov/
```

## Documentation

### Writing Documentation

Documentation is built with [Zensical](https://zensical.org/). Source files are in `docs/`:

```
docs/
├── index.md           # Home page
├── getting-started.md # Getting started guide
├── authentication.md  # Authentication guide
├── api-reference.md   # API reference
├── examples.md        # Examples and cookbook
└── contributing.md    # This file
```

#### Preview Documentation Locally

```bash
zensical serve
```

Visit `http://localhost:8000` to preview.

### Docstrings

All public APIs should have docstrings:

```python
def range(self, start=None, stop=None, months=0, days=0):
    """
    Define the date range for the query.
    
    Args:
        start: Start date (str, datetime.date, or None). Supports "today", "yesterday",
               date strings like "2024-01-01", or datetime.date objects. Default: yesterday.
        stop: End date. Same formats as start. Default: same as start.
        months: Month offset from start date. Negative for past, positive for future.
        days: Day offset from start date. Negative for past, positive for future.
    
    Returns:
        New Query object with date range set.
    
    Examples:
        >>> query.range('today', days=-7)  # Last 7 days
        >>> query.range('2024-01-01', '2024-01-31')  # Specific range
        >>> query.range('today', months=-3)  # Last 3 months
    
    Note:
        API has a 16-month data retention limit.
    """
```

## Submitting Changes

### 1. Commit Your Changes

Write clear, descriptive commit messages:

```bash
git add .
git commit -m "Add support for bulk query execution

- Implement BulkQuery class
- Add tests for concurrent execution
- Update documentation with examples"
```

Good commit message format:
```
Short summary (50 chars or less)

Longer explanation if needed. Explain what changed and why.

- Bullet points are fine
- Reference issue numbers: Fixes #123
```

### 2. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 3. Open a Pull Request

1. Go to the [repository on GitHub](https://github.com/joshcarty/google-searchconsole)
2. Click "New Pull Request"
3. Select your fork and branch

### Feature Requests

When suggesting features, include:

1. **Use case**: Why is this feature needed?
2. **Proposed solution**: How should it work?
3. **Alternatives**: Other approaches you've considered
4. **Examples**: Code examples of how it would be used

### Code Organization

```
google-searchconsole/
├── src/
│   └── searchconsole/
│       ├── __init__.py      # Public API exports
│       ├── auth.py          # Authentication
│       ├── account.py       # Account & WebProperty
│       ├── query.py         # Query & Report
│       └── utils.py         # Utilities
├── tests.py                 # Test suite
├── docs/                    # Documentation
├── pyproject.toml          # Project metadata
└── README.md               # Quick start guide
```

## Communication

### Getting Help

- **Documentation**: Check the [docs](https://joshcarty.github.io/google-searchconsole/) first
- **Issues**: Search [existing issues](https://github.com/joshcarty/google-searchconsole/issues)
- **Discussions**: Start a [discussion](https://github.com/joshcarty/google-searchconsole/discussions)

### Asking Questions

When asking for help:

1. Search existing issues/discussions first
2. Provide a minimal reproducible example
3. Include relevant error messages
4. Be specific about what you've tried

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

If you have questions about contributing, feel free to:

- Open an issue with the "question" label
- Start a discussion on GitHub
- Check the documentation for more details

Thank you for contributing to the Google Search Console Python library!
