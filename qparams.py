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

    >>> add_query_params('foo', True, {"+'|äüö": 'bar'})
    'foo?%2B%27%7C%C3%A4%C3%BC%C3%B6=bar'

Order of original parameters is retained. Order of keyword arguments is not
(and can not be) retained:

    >>> add_query_params('foo?a=b&b=c&a=b&a=d', a='b')
    'foo?a=b&b=c&a=b&a=d&a=b'

    >>> add_query_params('http://example.com/a/b/c?a=b&q=c&e=d',
    ... x='y', e=1, o=2)
    'http://example.com/a/b/c?a=b&q=c&e=d&x=y&e=1&o=2'

There are three different strategies for key-value handling. The default,
``allow_dups = True`` (*allow_dups* is the second optional positional
argument) appending new parameters, allowing all duplicates, has been
demonstrated above.

Second, *allow_dups* can be ``False`` to disallow duplicates in values
and regroup keys so that different values for the same key are adjacent:

    >>> add_query_params('http://example.com/a/b/c?a=b', False, a='b')
    'http://example.com/a/b/c?a=b'

    >>> add_query_params('http://example.com/a/b/c?a=b&c=q', False, c='o',
    ... a='b', b='d')
    'http://example.com/a/b/c?a=b&c=q&c=o&b=d'

    >>> add_query_params('http://example.com/a/b/c?a=b', False, a='c', b='d')
    'http://example.com/a/b/c?a=b&a=c&b=d'

    >>> add_query_params('http://example.com/a/b/c?a', False, a='b', c=None)
    'http://example.com/a/b/c?a=b&c'

    >>> add_query_params('http://example.com/a/b/c?a=b', False,
    ... b='d', a=('q', 'b', 'c'))
    'http://example.com/a/b/c?a=b&a=q&a=c&b=d'

Third, *allow_dups* can be ``None`` to disallow duplicates in keys -- each key
can have a single value, unless explicitly given a list of values, and later
values override the value (like dict.update()):

    >>> add_query_params('http://example.com/a/b/c?a=b', None, a='b')
    'http://example.com/a/b/c?a=b'

    >>> add_query_params('http://example.com/a/b/c?a=b&c=q', None, c='o',
    ... a='b', b='d')
    'http://example.com/a/b/c?a=b&c=o&b=d'

    >>> add_query_params('http://example.com/a/b/c?a=b', None, a='c', b='d')
    'http://example.com/a/b/c?a=c&b=d'

    >>> add_query_params('http://example.com/a/b/c?a', None, a='b', c=None)
    'http://example.com/a/b/c?a=b&c'

    >>> add_query_params('http://example.com/a/b/c?a=b', None,
    ... b='d', a=('q', 'b', 'c'))
    'http://example.com/a/b/c?a=q&a=b&a=c&b=d'

If you need to retain the order of the added parameters, use an
:class:`OrderedDict` as the second argument (*params_dict*):

    >>> from collections import OrderedDict
    >>> od = OrderedDict()
    >>> od['xavier'] = 1
    >>> od['abacus'] = 2
    >>> od['janus'] = 3
    >>> add_query_params('http://example.com/a/b/c?a=b', True, od)
    'http://example.com/a/b/c?a=b&xavier=1&abacus=2&janus=3'

    >>> add_query_params('http://example.com/a/b/c?a=b', False, od)
    'http://example.com/a/b/c?a=b&xavier=1&abacus=2&janus=3'

    >>> add_query_params('http://example.com/a/b/c?a=b', None, od)
    'http://example.com/a/b/c?a=b&xavier=1&abacus=2&janus=3'

If both *params_dict* and keyword arguments are provided, values from the
former are used before the latter:

    >>> add_query_params('http://example.com/a/b/c?a=b', True, od, xavier=1.1,
    ... zorg='a', alpha='b', watt='c', borg='d')
    'http://example.com/a/b/c?a=b&xavier=1&abacus=2&janus=3&zorg=a&xavier=1.1&borg=d&watt=c&alpha=b'

    >>> add_query_params('http://example.com/a/b/c?a=b', False, od, xavier=1.1,
    ... zorg='a', alpha='b', watt='c', borg='d')
    'http://example.com/a/b/c?a=b&xavier=1&xavier=1.1&abacus=2&janus=3&zorg=a&borg=d&watt=c&alpha=b'

    >>> add_query_params('http://example.com/a/b/c?a=b', None, od, xavier=1.1,
    ... zorg='a', alpha='b', watt='c', borg='d')
    'http://example.com/a/b/c?a=b&xavier=1.1&abacus=2&janus=3&zorg=a&borg=d&watt=c&alpha=b'

Do nothing with a single argument:

    >>> add_query_params('a')
    'a'

    >>> add_query_params('a', False, None)
    'a'

    >>> add_query_params('a', None, None)
    'a'

    >>> add_query_params('arbitrary strange stuff?öäüõ*()+-=42')
    'arbitrary strange stuff?\\xc3\\xb6\\xc3\\xa4\\xc3\\xbc\\xc3\\xb5*()+-=42'

The separator used for key-value pairs can be either '&' (the default) or ';'.
It can be specified in the fourth optional postitional argument, *separator*.

    >>> add_query_params('foo?a=1&b=2', True, None, ';', b=None, c=3)
    'foo?a=1;b=2;c=3;b'

    >>> add_query_params('foo?a=1&b=2', False, None, ';', b=None, c=3)
    'foo?a=1;b=2;c=3'

    >>> add_query_params('foo?a=1&b=2', None, None, ';', b=None, c=3)
    'foo?a=1;b;c=3'

    >>> add_query_params('foo?a=1;b=2', True, None, '&', b=None, c=3)
    'foo?a=1&b=2&c=3&b'

If no separator is provided, '&' will be used *unless* the query already
contains ';':

    >>> add_query_params('foo?a=1', b=None, c=3)
    'foo?a=1&c=3&b'

    >>> add_query_params('foo?a=1;b=2', b=None, c=3)
    'foo?a=1;b=2;c=3;b'

Some edge cases with empty values:

    >>> add_query_params('foo?a&a', b=None)
    'foo?a&a&b'

    >>> add_query_params('foo?a&a', False, b=None)
    'foo?a&b'

    >>> add_query_params('foo?a&a', None, b=None)
    'foo?a&b'

Exceptions:

    >>> add_query_params()
    Traceback (most recent call last):
        ...
    TypeError: add_query_params() takes at least 1 argument (0 given)

    >>> add_query_params(url='a')
    Traceback (most recent call last):
        ...
    TypeError: add_query_params() takes at least 1 argument (0 given)

    >>> add_query_params('a', 'b', 'c', 'd', 'e')
    Traceback (most recent call last):
        ...
    TypeError: add_query_params() takes at most 4 arguments (5 given)

    >>> add_query_params('a', True, 'b')
    Traceback (most recent call last):
        ...
    TypeError: The third argument of add_query_params() is not a dict-like object (missing iteritems())

    >>> add_query_params('a', True, None, 'b', a='b')
    Traceback (most recent call last):
        ...
    TypeError: add_query_params() fourth argument has to be either ';' or '&' ('b' given)
"""

from collections import OrderedDict
from urlparse import urlparse, urlunparse
from urllib import urlencode, quote

_OTHER_SEPARATOR = { ';': '&', '&': ';' }

def add_query_params(*args, **kwargs):
    """
    add_query_parms(url, [allow_dups, [args_dict, [separator]]], **kwargs)

    Appends query parameters to an URL and returns the result.

    :param url: the URL to update, a string.
    :param allow_dups: if
        * True: plainly append new parameters, allowing all duplicates
          (default),
        * False: disallow duplicates in values and regroup keys so that
          different values for the same key are adjacent,
        * None: disallow duplicates in keys -- each key can have a single
          value and later values override the value (like dict.update()).
    :param args_dict: optional dictionary of parameters, default is {}.
    :param separator: either ';' or '&', the separator between key-value
        pairs, default is '&'.
    :param kwargs: parameters as keyword arguments.

    :return: original URL with updated query parameters or the original URL
        unchanged if no parameters given.
    """
    if not args:
        raise TypeError('add_query_params() takes at least 1 argument '
                '(0 given)')
    if len(args) > 4:
        raise TypeError('add_query_params() takes at most 4 arguments '
                '(%s given)' % len(args))
    if (len(args) == 1 and not kwargs or
            len(args) > 2 and not args[2] and not kwargs):
        return args[0]

    url = urlparse(args[0])
    query = url.query

    # params dict handling
    if len(args) > 2 and args[2]:
        params_dict = args[2]
        try:
            params_dict.iteritems()
        except AttributeError:
            raise TypeError('The third argument of add_query_params() '
                    'is not a dict-like object (missing iteritems())')
    else:
        params_dict = {}

    # separator handling
    if len(args) > 3:
        separator = args[3]
        if separator not in _OTHER_SEPARATOR:
            raise TypeError("add_query_params() fourth argument has to be "
                    "either ';' or '&' ('%s' given)" % separator)
        # make the result consistent
        if (query and separator not in query and
                _OTHER_SEPARATOR[separator] in query):
            query = query.replace(_OTHER_SEPARATOR[separator], separator)
    else:
        separator = (';' if query and ';' in query else '&')

    allow_dups = (args[1] if len(args) > 1 else True)
    if allow_dups:
        encoded = _append_params(query, params_dict, kwargs, separator)
    elif allow_dups is None:
        encoded = _update_params(query, params_dict, kwargs, separator,
                _set_key)
    else:
        encoded = _update_params(query, params_dict, kwargs, separator,
                _update_key)

    return urlunparse((url.scheme, url.netloc, url.path, url.params,
        encoded, url.fragment))

def _update_params(query, params_dict, kwargs, sep, key_update_fn):
    query_args = OrderedDict()

    # first preserve the original query
    if query:
        for chunk in query.split(sep):
            if '=' in chunk:
                key, val = chunk.split('=', 1)
                key_update_fn(query_args, key, val)
            else:
                key_update_fn(query_args, chunk, None)

    # merge params dict
    for key, val in params_dict.iteritems():
        key_update_fn(query_args, key, val)

    # merge kwargs
    for key, val in kwargs.iteritems():
        key_update_fn(query_args, key, val)

    encoded = []
    for key, val in query_args.iteritems():
        _append_encoded_params(encoded, key, val)

    return sep.join(encoded)

def _append_params(query, params_dict, kwargs, sep):

    query_args = []

    # merge params_dict
    for key, val in params_dict.iteritems():
        query_args.append((key, val))

    # merge kwargs
    for key, val in kwargs.iteritems():
        query_args.append((key, val))

    encoded = []
    for key, val in query_args:
        _append_encoded_params(encoded, key, val)

    if query:
        # preserve original query parameters intact
        return query + sep + sep.join(encoded)
    else:
        return sep.join(encoded)

def _append_encoded_params(encoded, key, val):
    if val is None:
        encoded.append(quote(key, safe='')) # '/' is not safe here
    else:
        encoded.append(urlencode(((key, val),), True))

def _set_key(dct, key, val):
    dct[key] = val

def _update_key(dct, key, val):
    """
    Update a key in dict *dct*. If they key already exists in *dct*, but the
    value doesn't, a list of values is created and the value appended to it.
    """
    if key in dct:
        if val == dct[key]:
            return
        dct[key] = _unique_list(dct[key], val)
    else:
        dct[key] = val

def _unique_list(a, b):
    """
    Merges two lists, retaining only unique elements.
    Based on Dave Kirby's recipe from
    http://www.peterbe.com/plog/uniqifiers-benchmark/uniqifiers_benchmark.py
    """
    # this is ugly and should really be solved with an OrderedSet, see below
    assert not isinstance(a, tuple)
    assert not (a is None and b is None) # already handled with ==
    if not isinstance(a, list):
        a = [a]
    if isinstance(b, tuple):
        a = a + list(b)
    elif isinstance(b, list):
        a = a + b
    else:
        a.append(b)
    seen = set()
    return [x for x in a if x is not None and x not in seen and not seen.add(x)]

if __name__ == '__main__':
    import doctest
    doctest.testmod()
