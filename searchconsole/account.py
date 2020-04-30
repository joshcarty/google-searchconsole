# encoding: utf-8

from . import query


class Account:
    """
    An account can be associated with a number of web
    properties.

    You should navigate to a web property to run queries.

    Usage:
    >>> import searchconsole
    >>> account = searchconsole.authenticate(
    ...     client_config='auth/client_secrets.json',
    ...     credentials='auth/credentials.dat'
    ... )
    >>> account
    <searchconsole.account.Account(client_id='...')>
    >>> account[0]
    <searchconsole.account.WebProperty(url='...')>
    >>> account[www_webproperty_com]
    <searchconsole.account.WebProperty(url='...')>
    """

    def __init__(self, service, credentials):
        self.service = service
        self.credentials = credentials

    @property
    def webproperties(self):
        """
        A list of all web properties associated with this account. You may
        select a specific web property using an index or by indexing the
        account directly with the properties exact URI.

        Usage:
        >>> account.webproperties[0]
        <searchconsole.account.WebProperty(url='...')>
        """
        raw_properties = self.service.sites().list().execute().get(
            'siteEntry', [])

        return [WebProperty(raw, self) for raw in raw_properties]

    def __getitem__(self, item):
        if isinstance(item, str):
            properties = [p for p in self.webproperties if p.url == item]
            web_property = properties[0] if properties else None
        else:
            web_property = self.webproperties[item]

        return web_property

    def __repr__(self):
        return "<searchconsole.account.Account(client_id='{}')>".format(
            self.credentials.client_id
        )


class WebProperty:
    """
    A web property is a particular website you're tracking
    in Google Search Console. You will use a web property
    to make your Search Analytics queries.

    Usage:
    >>> webproperty = account[www_webproperty_com]
    >>> webproperty.query.range(start='today', days=-7).dimension('date').get()
    <searchconsole.query.Report(rows=...)>
    """

    permission_levels = {
        'siteFullUser': 1,
        'siteOwner': 2,
        'siteRestrictedUser': 3,
        'siteUnverifiedUser': 4
    }

    def __init__(self, raw, account):
        self.account = account
        self.raw = raw
        self.url = raw['siteUrl']
        self.permission = raw['permissionLevel']
        self.query = query.Query(self)

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __repr__(self):
        return "<searchconsole.account.WebProperty(url='{site_url}')>".format(
            site_url=self.url
        )
