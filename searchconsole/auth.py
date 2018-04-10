# encoding: utf-8

"""
Convenience function for authenticating with Google Search
Console. You can use saved client configuration files or a
mapping object and generate your credentials using OAuth2 or
a serialized credentials file or mapping.

For more details on formatting your configuration files, see:
http://google-auth-oauthlib.readthedocs.io/en/latest/reference/google_auth_oauthlib.flow.html
"""

import collections.abc
import json

from apiclient import discovery
import google.oauth2.credentials
import google.oauth2.service_account
from google_auth_oauthlib.flow import InstalledAppFlow

from .account import Account


def authenticate(client_config=None, credentials=None, service_account=None,
                 serialize=None):
    """
    The `authenticate` function will authenticate a user with the Google Search
    Console API.

    Args:
        client_config (collections.abc.Mapping or str): Client configuration
            parameters in the Google format specified in the module docstring.
        credentials (collections.abc.Mapping or str): OAuth2 credentials
            parameters in the Google format specified in the module docstring
        service_account (collections.abc.Mapping or str): Path OAuth2 service
            account credentials.
        serialize (str): Path to where credentials should be serialized.

    Returns:
        `searchconsole.account.Account`: Account object containing web
        properties that can be queried.

    Usage:
        >>> import searchconsole
        >>> account = searchconsole.authenticate(
        ...     client_config='auth/client_secrets.json',
        ...     credentials='auth/credentials.dat'
        ... )
    """

    if credentials:

        if isinstance(credentials, str):

            with open(credentials, 'r') as f:
                credentials = json.load(f)

        credentials = google.oauth2.credentials.Credentials(
            token=credentials['token'],
            refresh_token=credentials['refresh_token'],
            id_token=credentials['id_token'],
            token_uri=credentials['token_uri'],
            client_id=credentials['client_id'],
            client_secret=credentials['client_secret'],
            scopes=credentials['scopes']
        )

    elif client_config and not (credentials or service_account):

        if isinstance(client_config, collections.abc.Mapping):

            flow = InstalledAppFlow.from_client_config(
                client_config=client_config,
                scopes=['https://www.googleapis.com/auth/webmasters.readonly']
            )

        elif isinstance(client_config, str):

            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_file=client_config,
                scopes=['https://www.googleapis.com/auth/webmasters.readonly']
            )

        else:
            raise ValueError("Client secrets must be a mapping or path to file")

        flow.run_local_server()
        credentials = flow.credentials

    elif service_account:

        if isinstance(service_account, str):

            with open(service_account, 'r') as f:
                service_account = json.load(f)

        credentials = google.oauth2.service_account.Credentials.from_service_account_info(
            info=service_account
        )

    else:

        raise ValueError("Insufficient credentials provided.")


    service = discovery.build(
        serviceName='webmasters',
        version='v3',
        credentials=credentials,
        cache_discovery=False,
    )

    if serialize:
        serialize_credentials(credentials, serialize)

    return Account(service, credentials)


def serialize_credentials(credentials, path):
    """
    Serialize credentials as JSON file.

    Args:
        credentials (`google.oauth2.credentials.Credentials`): Credentials object.
        path (`str`): Path where serialized credentials should be stored.

    Returns:
        None
    """
    if isinstance(path, str):

        serialized = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'id_token': credentials.id_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }

        with open(path, 'w') as f:
            json.dump(serialized, f)

    else:

        raise TypeError('`serialize` must be a path.')