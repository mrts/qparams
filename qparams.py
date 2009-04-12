# coding=utf8
"""
Appends query parameters to an URL and returns the result.

In the simplest form, parameters can be passed via keyword arguments:

    >>> add_query_params('foo', bar='baz')
    'foo?bar=baz'

    >>> add_query_params('http://example.com/a/b/c?a=b', b='d')
    'http://example.com/a/b/c?a=b&b=d'

Note that '/', if given in arguments, is encoded:

    >>> add_query_params('http://example.com/a/b/c?a=b', b='d', foo='/bar')
    'http://example.com/a/b/c?a=b&b=d&foo=%2Fbar'

Duplicates are retained and different values for the same key supported:

    >>> add_query_params('http://example.com/a/b/c?a=b', a='b')
    'http://example.com/a/b/c?a=b&a=b'

    >>> add_query_params('http://example.com/a/b/c?a=b&c=q', a='b', b='d',
    ...  c='q')
    'http://example.com/a/b/c?a=b&c=q&a=b&c=q&b=d'

    >>> add_query_params('http://example.com/a/b/c?a=b', a='c', b='d')
    'http://example.com/a/b/c?a=b&a=c&b=d'

Pass different values for a single key in a list:

    >>> add_query_params('http://example.com/a/b/c?a=b', a=('q', 'b', 'c'),
    ... b='d')
    'http://example.com/a/b/c?a=b&a=q&a=b&a=c&b=d'

Keys with no value are respected, pass ``None`` to create one:

    >>> add_query_params('http://example.com/a/b/c?a', b=None)
    'http://example.com/a/b/c?a&b'

A key can be both empty and have a value:

    >>> add_query_params('http://example.com/a/b/c?a', a='b', c=None)
    'http://example.com/a/b/c?a&a=b&c'

If you need to pass in key names that are not allowed in keyword arguments,
pass them via a dictionary in second argument:

    >>> add_query_params('foo', {"+'|äüö": 'bar'})
    'foo?%2B%27%7C%C3%A4%C3%BC%C3%B6=bar'

Order of original parameters is retained, although similar keys are grouped
together. Order of keyword arguments is not (and can not be) retained:

    >>> add_query_params('foo?a=b&b=c&a=b&a=d', a='b')
    'foo?a=b&b=c&a=b&a=d&a=b'

    >>> add_query_params('http://example.com/a/b/c?a=b&q=c&e=d',
    ... x='y', e=1, o=2)
    'http://example.com/a/b/c?a=b&q=c&e=d&x=y&e=1&o=2'

If you need to retain the order of the added parameters, use an
:class:`OrderedDict` as the second argument (*params_dict*):

    >>> from collections import OrderedDict
    >>> od = OrderedDict()
    >>> od['xavier'] = 1
    >>> od['abacus'] = 2
    >>> od['janus'] = 3
    >>> add_query_params('http://example.com/a/b/c?a=b', od)
    'http://example.com/a/b/c?a=b&xavier=1&abacus=2&janus=3'

If both *params_dict* and keyword arguments are provided, values from the
former are used before the latter:

    >>> add_query_params('http://example.com/a/b/c?a=b', od, xavier=1.1,
    ... zorg='a', alpha='b', watt='c', borg='d')
    'http://example.com/a/b/c?a=b&xavier=1&abacus=2&janus=3&zorg=a&xavier=1.1&borg=d&watt=c&alpha=b'

Do nothing with a single argument:

    >>> add_query_params('a')
    'a'

    >>> add_query_params('arbitrary strange stuff?öäüõ*()+-=42')
    'arbitrary strange stuff?\\xc3\\xb6\\xc3\\xa4\\xc3\\xbc\\xc3\\xb5*()+-=42'

Some edge cases:

    >>> add_query_params('foo?a&a', b=None)
    'foo?a&a&b'

Exceptions:

    >>> add_query_params()
    Traceback (most recent call last):
        ...
    TypeError: add_query_params() takes at least 1 argument (0 given)

    >>> add_query_params(url='a')
    Traceback (most recent call last):
        ...
    TypeError: add_query_params() takes at least 1 argument (0 given)

    >>> add_query_params('a', 'b', 'c')
    Traceback (most recent call last):
        ...
    TypeError: add_query_params() takes at most 2 arguments (3 given)

    >>> add_query_params('a', 'b')
    Traceback (most recent call last):
        ...
    TypeError: The second argument of add_query_params() is not a dict-like object (missing iteritems())
"""

from collections import OrderedDict
from urlparse import urlparse, urlunparse
from urllib import urlencode, quote

def add_query_params(*args, **kwargs):
    if not args:
        raise TypeError('add_query_params() takes at least 1 argument '
                '(0 given)')
    if len(args) > 2:
        raise TypeError('add_query_params() takes at most 2 arguments '
                '(%s given)' % len(args))
    if (len(args) == 1 and not kwargs or
            len(args) == 2 and not args[1] and not kwargs):
        return args[0]

    url = urlparse(args[0])

    # preserve original query parameters and their order
    query_args = []
    if url.query:
        # support semicolon separators
        query = url.query.replace(';', '&')
        for chunk in url.query.split('&'):
            if '=' in chunk:
                key, val = chunk.split('=', 1)
                query_args.append((key, val))
            else:
                query_args.append((chunk, None))

    # merge params_dict
    if len(args) == 2 and args[1]:
        params_dict = args[1]
        try:
            params_dict.iteritems()
        except AttributeError:
            raise TypeError('The second argument of add_query_params() '
                    'is not a dict-like object (missing iteritems())')
        for key, val in params_dict.iteritems():
            query_args.append((key, val))

    # merge kwargs
    for key, val in kwargs.iteritems():
        query_args.append((key, val))

    encoded = []
    for key, val in query_args:
        if val is None:
            encoded.append(quote(key, safe='')) # '/' is not safe here
        else:
            encoded.append(urlencode(((key, val),), True))

    return urlunparse((url.scheme, url.netloc, url.path, url.params,
        '&'.join(encoded), url.fragment))

if __name__ == '__main__':
    import doctest
    doctest.testmod()
