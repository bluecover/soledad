# coding: utf-8

from __future__ import print_function, absolute_import, unicode_literals

import json
import logging
import hashlib

from flask import current_app
from requests import Session

from jupiter.ext import sentry
from libs.cache import mc


class BearyChat(object):
    """The API client for BearyChat.

    You need to configure the URL of BearyChat robot in your environment
    variables::

        export FOOBAR_BEARYCHAT_URL='"http://..."'

    Then you could use the client::

        bearychat = BearyChat('foobar')  # "foobar" means "FOOBAR_" prefix
        bearychat.say('yo~')
    """

    def __init__(self, name, channel=None):
        self.name = name
        self.channel = channel
        self.session = Session()

    @property
    def url(self):
        if current_app:
            return current_app.config.get('%s_BEARYCHAT_URL' % self.name.upper())

    @property
    def configured(self):
        return self.url is not None

    def attachment(self, title, text, color, images):
        data = {
            'title': unicode(title) if title else None,
            'text': unicode(text) if text else None,
            'color': unicode(color) if color else None,
            'images': [{'url': unicode(url)} for url in images]}
        return {k: v for k, v in data.items() if v}

    def say(self, text, markdown=True, channel=None, attachments=None,
            skip_duplication=True):
        data = {
            'text': unicode(text),
            'markdown': bool(markdown)}
        channel = channel or self.channel
        if channel is not None:
            data['channel'] = unicode(channel)
        if attachments is not None:
            data['attachments'] = list(attachments)

        payload = json.dumps(data, sort_keys=True)
        payload_digest = hashlib.sha1(bytes(payload)).hexdigest()
        payload_extra = {'payload': data, 'channel': self.channel}

        if skip_duplication and mc.sismember(self.url, payload_digest):
            sentry.captureMessage(
                'BearyChat Robot "%s" skipped duplicated messages' % self.name,
                level=logging.INFO, extra=payload_extra)
            return

        response = self.session.post(self.url, data={'payload': payload})
        if response.status_code == 410:
            sentry.captureMessage(
                'BearyChat Robot "%s" has been paused' % self.name,
                level=logging.INFO, extra=payload_extra)
            return
        else:
            response.raise_for_status()

        # mark as sent
        mc.sadd(self.url, payload_digest)

        return response
