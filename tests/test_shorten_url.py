# -*- coding: utf-8 -*-

from .framework import BaseTestCase

from libs.shorten.url import ShortenUrl


URL = 'http://guihua.com/' + '*' * 100


class ShortenUrlTest(BaseTestCase):
    def test_add_shorten_url(self):
        code = ShortenUrl.gen(URL)
        url = ShortenUrl.get(code)
        self.assertEqual(url, URL)

        code = ShortenUrl.gen(URL, code='rain')
        url = ShortenUrl.get(code)
        self.assertEqual(url, URL)

    def test_update_url(self):
        code = ShortenUrl.gen(URL)
        url = ShortenUrl.get(code)
        self.assertEqual(url, URL)
        _url = 'http://test.com'
        ShortenUrl.update(code, _url)
        url = ShortenUrl.get(code)
        self.assertEqual(url, _url)
