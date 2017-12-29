# encoding: utf-8

import doctest

import searchconsole

account = searchconsole.authenticate(
    client_config='auth/client_secrets.json',
    credentials='auth/credentials.dat'
)
webproperty = account['https://www.johnlewis.com/']
query = webproperty.query

globs = {
    'account': account,
    'webproperty': webproperty,
    'query': query
}

doctest.testmod(searchconsole.account, optionflags=doctest.ELLIPSIS, globs=globs)
doctest.testmod(searchconsole.query, optionflags=doctest.ELLIPSIS, globs=globs)
doctest.testmod(searchconsole.auth, optionflags=doctest.ELLIPSIS, globs=globs)