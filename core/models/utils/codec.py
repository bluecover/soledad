# -*- coding: utf-8 -*-

import collections


def encode(data, encoding='utf-8'):
    if isinstance(data, basestring):
        return data.encode(encoding)
    elif isinstance(data, collections.Mapping):
        return dict(map(encode, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(encode, data))
    else:
        return data


def decode(text, decoding='utf-8'):
    if isinstance(text, unicode):
        return text
    return text.decode(decoding)
