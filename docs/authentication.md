---
icon: lucide/key
---

# Authentication

The library supports multiple authentication methods to suit different use cases. This guide covers all authentication options in detail.

## Authentication Methods

There are two primary authentication methods:

1. **OAuth2 Flow** - For personal use or applications where users authenticate themselves
2. **Service Account** - For server-side applications or automated scripts

## OAuth2 Authentication

OAuth2 is the recommended method for most users. It allows you to authenticate as yourself and access properties you own or have access to.

### Interactive OAuth2 Flow

The simplest authentication method for getting started:

```python
import searchconsole

# First-time authentication
account = searchconsole.authenticate(client_config='client_secrets.json')
```

This will:

1. Open your default web browser
2. Prompt you to log in to Google
3. Ask you to grant permissions
4. Redirect back to confirm success
5. Return an authenticated `Account` object

!!! tip "One-Time Setup"
    After your first authentication, save your credentials to skip the browser flow in the future.

### Saving Credentials

To avoid repeating the OAuth flow every time:

```python
# First authentication - opens browser
account = searchconsole.authenticate(client_config='client_secrets.json')

# Save credentials for future use
account.serialize_credentials('credentials.json')
```

Then in future sessions:

```python
# Load saved credentials - no browser needed
account = searchconsole.authenticate(
    client_config='client_secrets.json',
    credentials='credentials.json',
)
```

!!! warning "Security Notice"
    The `credentials.json` file contains access tokens for your account. Keep it secure and add it to `.gitignore` to prevent committing it to version control.

### Console Flow (For Remote Development Environments)

If you're running on a remote development environment (like Google Colab) where you can't use the web flow, use the console flow instead:

```python
account = searchconsole.authenticate(client_config='client_secrets.json', flow='console')
```

This will:

1. Print an authorization URL to the console
2. You manually open the URL in a browser
3. After granting permissions, Google redirects you to a localhost URL
4. Copy the entire redirect URL from your browser's address bar
5. Paste it back into the console

Example console output:

```
Please visit this URL to authorize this application:
https://accounts.google.com/o/oauth2/auth?client_id=...

Enter the authorization code: 
```

After authorization, copy the full URL:

```
http://localhost:8080/?code=4/0AX4XfWh...&scope=https://www.googleapis.com/auth/webmasters.readonly
```

And paste it into the console.

### Using Configuration Dictionaries

Instead of file paths, you can pass configuration as dictionaries:

```python
client_config = {
    "installed": {
        "client_id": "your_client_id.apps.googleusercontent.com",
        "client_secret": "your_client_secret",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["http://localhost"]
    }
}

credentials = {
    "token": "ya29.a0AfH6SMBx...",
    "refresh_token": "1//0gZ9K8W...",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_id": "your_client_id.apps.googleusercontent.com",
    "client_secret": "your_client_secret",
    "scopes": ["https://www.googleapis.com/auth/webmasters.readonly"]
}

account = searchconsole.authenticate(client_config=client_config, credentials=credentials)
```

This is useful when storing credentials in environment variables or secret management systems.

## Service Account Authentication

Service accounts are ideal for:

- Server-side applications
- Automated scripts and cron jobs
- CI/CD pipelines
- Applications that don't require user interaction

### Setting Up a Service Account

1. **Create a Service Account**:
    - Go to [Google Cloud Console](https://console.cloud.google.com/)
    - Navigate to **IAM & Admin** > **Service Accounts**
    - Click **Create Service Account**
    - Enter a name and description
    - Click **Create and Continue**

2. **Create a Key**:
    - Click on the newly created service account
    - Go to the **Keys** tab
    - Click **Add Key** > **Create new key**
    - Choose **JSON** format
    - Click **Create**
    - Save the downloaded JSON file as `service_account.json`

3. **Grant Access to Search Console**:
    - Go to [Google Search Console](https://search.google.com/search-console/)
    - Select your property
    - Click **Settings** > **Users and permissions**
    - Click **Add user**
    - Enter the service account email (found in the JSON file: `client_email`)
    - Set permission level (Owner or Full)
    - Click **Add**

### Using Service Account Authentication

```python
import searchconsole

# Authenticate with service account
account = searchconsole.authenticate(service_account='service_account.json')

# Use as normal
webproperty = account['https://www.example.com/']
report = webproperty.query.range('today', days=-7).get()
```

You can also use a dictionary.

!!! warning "Service Account Limitations"
    - Cannot use both OAuth2 and service account credentials simultaneously
    - Service account credentials cannot be serialized/saved like OAuth2 credentials
    - The service account must be explicitly granted access to each property in Search Console

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

## Security Best Practices

1. **Never commit credentials to version control**

2. **Use environment variables in production**
    ```python
    credentials = os.environ.get('GOOGLE_CREDENTIALS')
    ```

3. **Rotate service account keys regularly**
    - Create new keys periodically
    - Delete old keys after rotation

4. **Use the principle of least privilege**
    - Only grant necessary permissions
    - Use "Restricted User" when full access isn't needed

5. **Monitor access logs**
    - Check [Google Account Activity](https://myaccount.google.com/permissions) regularly
    - Review service account usage in Cloud Console

## Next Steps

- **[Getting Started](getting-started.md)** - Run your first query
- **[API Reference](api-reference.md)** - Detailed API documentation
- **[Examples](examples.md)** - Real-world usage examples
