# -*- coding: utf-8 -*-

from .framework import BaseTestCase

from libs.markdown import sanitize_html


class MarkdownTest(BaseTestCase):
    def test_markdown_parse(self):
        text = 'hello world'
        assert sanitize_html(text) == 'hello world'

        text = 'some valid tag <b>strong</b> <i>here</i>'
        assert sanitize_html(text) == text

        text = 'some invalid tag <input name="input"/>'
        assert sanitize_html(text) == 'some invalid tag '

        text = 'empty tag will be removed <b></b>'
        assert sanitize_html(text) == 'empty tag will be removed '

        text = '<p color="red">This is a content with attrs.</p>'
        assert sanitize_html(text) == '<p>This is a content with attrs.</p>'

        text = '<a href="someurl">This is a link with no target.</a>'
        assert sanitize_html(text) == ('<a href="someurl" target="_blank">'
                                       'This is a link with no target.</a>')

        text = ('<a href="someurl" target="">'
                'This is a link with invalid target.</a>')
        assert sanitize_html(text) == (
            '<a href="someurl" target="_blank">'
            'This is a link with invalid target.</a>')

        text = ('<a href="someurl" target="_blank">'
                'This is a link with valid target.</a>')
        assert sanitize_html(text) == ('<a href="someurl" target="_blank">'
                                       'This is a link with valid target.</a>')
