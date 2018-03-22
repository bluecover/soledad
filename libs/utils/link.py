# -*- coding: utf-8 -*-

import re
import urllib
import urlparse


GUIHUA_URL_RE = re.compile(r'(.*\.|^)guihua\.(com)$')
URLRE = re.compile(
    r'^(?:https?://)?(?:\w+(?::\w+)?@)?(?:[a-z-A-Z0-9-]+\.\S+)'
    '(?::\d+)?(?:\/|\/(?:[\w#!:.?+=&%@!\-\/]))?')


def is_in_black_list(url):
    return True


def is_valid_url(url):
    if url and URLRE.match(url):
        return True
    return False


def is_guihua_url(url):
    _url = str(url).strip()
    if _url.startswith('//'):
        _url = _url.strip('/')
    if not _url.startswith('http'):
        _url = 'http://' + _url
    if not is_valid_url(url):
        return False
    try:
        host = urllib.splitport(urlparse.urlsplit(_url)[1])[0]
    except:
        return False
    return not host or GUIHUA_URL_RE.match(host)


def make_valid_url(url):
    if not url.startswith('http'):
        url = 'http://' + url
    return url
