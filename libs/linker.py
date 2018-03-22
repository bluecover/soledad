# coding: utf-8

from flask import url_for
from solar.utils.aes import encode


def _make_link(url):
    return url_for('link.link', ref=url, _external=True)


def make_url(url):
    url = encode(url)
    return _make_link(url)
