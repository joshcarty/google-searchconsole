# encoding: utf-8

"""
Convenience function for authenticating with Google Search
Console. You can use saved client configuration files or a
mapping object and generate your credentials using OAuth2 or
a serialized credentials file or mapping.

For more details on formatting your configuration files, see:
http://google-auth-oauthlib.readthedocs.io/en/latest/reference/google_auth_oauthlib.flow.html
"""

import abc
import collections.abc
import json
import warnings

from apiclient import discovery
from google.oauth2.credentials import Credentials as _OAuth2Credentials
from google.oauth2.service_account import Credentials as _ServiceAccountCredentials
from google_auth_oauthlib.flow import InstalledAppFlow

from .account import Account


def authenticate(
    client_config=None,
    credentials=None,
    serialize=None,
    flow="web",
    service_account=None,
):
    """
    The `authenticate` function will authenticate a user with the Google Search
    Console API.

    Args:
        client_config (collections.abc.Mapping or str): Client configuration
            parameters in the Google format specified in the module docstring.
        credentials (collections.abc.Mapping or str): OAuth2 credentials
            parameters in the Google format specified in the module docstring
        serialize (str): Path to where credentials should be serialized.
        flow (str): Authentication environment. Specify "console" for environments (like Google Colab)
            where the standard "web" flow isn't possible.
        service_account (collections.abc.Mapping or str): Service account credentials as a mapping or
            path to a JSON file. To be used instead of OAuth2 client_config or credentials.

    Returns:
        `searchconsole.account.Account`: Account object containing web
        properties that can be queried.

    Usage:
        >>> import searchconsole
        >>> account = searchconsole.authenticate(
        ...     client_config=client_config_json,
        ...     credentials=credentials_json
        ... )
    """

    if (client_config or credentials) and service_account:
        raise ValueError("Only one of client_config or service_account can be used")

    if credentials:
        credentials = OAuth2Credentials.from_config(credentials)

    elif client_config and not credentials:
        credentials = OAuth2Credentials.authenticate(client_config, flow=flow)

    elif service_account:
        credentials = ServiceAccountCredentials.from_config(service_account)

    else:
        raise ValueError(
            "One of client_config, credentials, or service_account must be provided"
        )

    service = discovery.build(
        serviceName="searchconsole",
        version="v1",
        credentials=credentials._credentials,
        cache_discovery=False,
    )

    if serialize:
        warnings.warn(
            "\n"
            "`searchconsole.authenticate(*, serialize='credentials.json')` will be deprecated in a future version of `google-searchconsole`.\n\n"
            "Please use `Account.serialize_credentials('credentials.json')` after authenticating instead:\n"
            "    >>> account = searchconsole.authenticate(client_config='client_config.json')\n"
            "    >>> account.serialize_credentials('credentials.json')\n"
            "    >>> account = searchconsole.authenticate(credentials='credentials.json')",
            FutureWarning,
        )

        credentials.serialize(serialize)

    return Account(service, credentials)


class Credentials(abc.ABC):
    WEBMASTER_SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]

    @property
    @abc.abstractmethod
    def identifier(self): ...

    @abc.abstractmethod
    def to_dict(self): ...

    @abc.abstractmethod
    def from_dict(cls, data): ...

    @classmethod
    def from_serialized(cls, file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def serialize(self, file_path):
        with open(file_path, "w") as f:
            json.dump(self.to_dict(), f)

    @classmethod
    def from_config(cls, data_or_file_path):
        if isinstance(data_or_file_path, str):
            with open(data_or_file_path, "r") as f:
                data = json.load(f)
        elif isinstance(data_or_file_path, collections.abc.Mapping):
            data = dict(data_or_file_path)
        else:
            raise ValueError(
                "Credentials must be either a file path or mapping object like a dict"
            )

        return cls.from_dict(data)


class OAuth2Credentials(Credentials):
    def __init__(
        self,
        credentials,
    ):
        self._credentials = credentials

    @property
    def identifier(self):
        return self._credentials.client_id

    @classmethod
    def authenticate(cls, client_config, flow="web"):
        if isinstance(client_config, str):
            with open(client_config, "r") as f:
                client_config = json.load(f)
        elif isinstance(client_config, collections.abc.Mapping):
            client_config = dict(client_config)
        else:
            raise ValueError(
                "Client config must be a file path or mapping object like a dict"
            )

        auth_flow = InstalledAppFlow.from_client_config(
            client_config=client_config, scopes=cls.WEBMASTER_SCOPES
        )

        if flow == "web":
            auth_flow.run_local_server() if flow == "web" else auth_flow.run_console()
        elif flow == "console":
            auth_flow.run_console()
        else:
            raise ValueError("Authentication flow '{}' not supported".format(flow))

        return cls(auth_flow.credentials)

    @classmethod
    def from_dict(cls, data):
        credentials = _OAuth2Credentials(
            token=data["token"],
            refresh_token=data["refresh_token"],
            id_token=data["id_token"],
            token_uri=data["token_uri"],
            client_id=data["client_id"],
            client_secret=data["client_secret"],
        )
        return cls(credentials)

    def to_dict(self):
        return {
            "token": self._credentials.token,
            "refresh_token": self._credentials.refresh_token,
            "id_token": self._credentials.id_token,
            "token_uri": self._credentials.token_uri,
            "client_id": self._credentials.client_id,
            "client_secret": self._credentials.client_secret,
            "scopes": self._credentials.scopes,
        }


class ServiceAccountCredentials(Credentials):
    def __init__(
        self,
        credentials,
    ):
        self._credentials = credentials

    @property
    def identifier(self):
        return self._credentials.service_account_email

    @classmethod
    def from_dict(cls, data):
        credentials = _ServiceAccountCredentials.from_service_account_info(
            info=data, scopes=cls.WEBMASTER_SCOPES
        )
        return cls(credentials)

    def to_dict(self):
        raise ValueError(
            "Serialization is not supported for service accounts since there is no interactive\n"
            " authentication flow. Simply use the service account key you used to authenticate."
        )
