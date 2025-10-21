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
import json
import urllib
import warnings

from apiclient import discovery
from google.oauth2.credentials import Credentials as _OAuth2Credentials
from google.oauth2.service_account import Credentials as _ServiceAccountCredentials
from google_auth_oauthlib.flow import InstalledAppFlow

from .account import Account
from .utils import parse_config


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
        data = parse_config(data_or_file_path)
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
        oauth2_flow = OAuth2Flow(client_config, cls.WEBMASTER_SCOPES)

        if flow == "web":
            return oauth2_flow.web_flow()
        elif flow == "console":
            return oauth2_flow.console_flow()
        else:
            raise ValueError("Authentication flow '{}' not supported".format(flow))

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


class OAuth2Flow:
    def __init__(self, client_config, scopes):
        self.client_config = parse_config(client_config)
        self.scopes = scopes

    def web_flow(self):
        flow = self._create_flow()
        flow.run_local_server()
        return OAuth2Credentials(flow.credentials)

    def console_flow(self):
        flow = self._create_flow()
        flow.redirect_uri = "http://localhost:8080/"
        auth_url, _ = flow.authorization_url(prompt="consent")
        print(
            "To use the console flow, you must complete the following steps:\n"
            "1. Go to the URL below\n"
            "2. Complete the steps to authenticate with your Google Account\n"
            "3. You will be taken to an error page with a URL starting with localhost:8080\n"
            "4. Copy the entire URL into the input below.\n"
            "\n"
            "Go to the following URL and complete the steps:\n",
            auth_url,
        )

        callback_url = input("Paste the url: ").strip()
        try:
            code = self._extract_callback_url_code(callback_url)
        except KeyError:
            raise ValueError("Could not extract token from URL")
        flow.fetch_token(code=code)
        return OAuth2Credentials(flow.credentials)

    def _create_flow(self):
        return InstalledAppFlow.from_client_config(
            client_config=self.client_config, scopes=self.scopes
        )

    @staticmethod
    def _extract_callback_url_code(callback_url):
        parsed = urllib.parse.urlparse(callback_url)
        params = urllib.parse.parse_qs(parsed.query)
        return params["code"][0]
