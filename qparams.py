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

Duplicates are discarded:

    >>> add_query_params('http://example.com/a/b/c?a=b', a='b')
    'http://example.com/a/b/c?a=b'

    >>> add_query_params('http://example.com/a/b/c?a=b&c=q', a='b', b='d',
    ...  c='q')
    'http://example.com/a/b/c?a=b&c=q&b=d'

But different values for the same key are supported:

    >>> add_query_params('http://example.com/a/b/c?a=b', a='c', b='d')
    'http://example.com/a/b/c?a=b&a=c&b=d'

Pass different values for a single key in a list (again, duplicates are
removed):

    >>> add_query_params('http://example.com/a/b/c?a=b', a=('q', 'b', 'c'),
    ... b='d')
    'http://example.com/a/b/c?a=b&a=q&a=c&b=d'

Keys with no value are respected, pass ``None`` to create one:

    >>> add_query_params('http://example.com/a/b/c?a', b=None)
    'http://example.com/a/b/c?a&b'

But if a value is given, the empty key is considered a duplicate (i.e. the
case of a&a=b is considered nonsensical):

    >>> add_query_params('http://example.com/a/b/c?a', a='b', c=None)
    'http://example.com/a/b/c?a=b&c'

If you need to pass in key names that are not allowed in keyword arguments,
pass them via a dictionary in second argument:

    >>> add_query_params('foo', {"+'|äüö": 'bar'})
    'foo?%2B%27%7C%C3%A4%C3%BC%C3%B6=bar'

Order of original parameters is retained, although similar keys are grouped
together. Order of keyword arguments is not (and can not be) retained:

    >>> add_query_params('foo?a=b&b=c&a=b&a=d', a='b')
    'foo?a=b&a=d&b=c'

    >>> add_query_params('http://example.com/a/b/c?a=b&q=c&e=d',
    ... x='y', e=1, o=2)
    'http://example.com/a/b/c?a=b&q=c&e=d&e=1&x=y&o=2'

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
    'http://example.com/a/b/c?a=b&xavier=1&xavier=1.1&abacus=2&janus=3&zorg=a&borg=d&watt=c&alpha=b'

Do nothing with a single argument:

    >>> add_query_params('a')
    'a'

    >>> add_query_params('arbitrary strange stuff?öäüõ*()+-=42')
    'arbitrary strange stuff?\\xc3\\xb6\\xc3\\xa4\\xc3\\xbc\\xc3\\xb5*()+-=42'

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

    # preserve original query parameters and their order,
    # duplicates will be removed and keys grouped though,
    # e.g. a=b&b=c&a=b&a=d will be changed to a=b&a=d&b=c
    query_args = OrderedDict()
    if url.query:
        for chunk in url.query.split('&'):
            if '=' in chunk:
                key, val = chunk.split('=', 1)
                _update_key(query_args, key, val)
            else:
                _update_key(query_args, chunk, None)

    # merge params_dict
    if len(args) == 2 and args[1]:
        params_dict = args[1]
        try:
            params_dict.iteritems()
        except AttributeError:
            raise TypeError('The second argument of add_query_params() '
                    'is not a dict-like object (missing iteritems())')
        for key, val in params_dict.iteritems():
            _update_key(query_args, key, val)

    # merge kwargs
    for key, val in kwargs.iteritems():
        _update_key(query_args, key, val)

    encoded = []
    for key, val in query_args.iteritems():
        if val is None:
            encoded.append(quote(key, safe='')) # '/' is not safe here
        else:
            encoded.append(urlencode(((key, val),), True))

    return urlunparse((url.scheme, url.netloc, url.path, url.params,
        '&'.join(encoded), url.fragment))

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

# OrderedSet would considerably simplify the above:
#
# def _update_key(dct, key, val):
#     if key in dct:
#         if dct[key] == val:
#             return
#         s = OrderedSet(dct[key]) # without None handling
#         s.append(val)
#         dct[key] = s
#     else:
#         dct[key] = val

