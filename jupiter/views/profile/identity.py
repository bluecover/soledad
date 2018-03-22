# coding: utf-8

from __future__ import print_function, absolute_import, unicode_literals

from flask import g, request, redirect, url_for
from flask.views import View
from flask_mako import render_template

from core.models.profile.identity import Identity, has_real_identity


class IdentityBindingView(View):
    """实名信息绑定的 Pluggable View.

    :param channel_endpoint: 绑定后触发动作的 AJAX View
    :param channel_name: 实名绑定关联的渠道, 例如``"宜人贷"``
    :param subtitle: 显示在页面上方的子标题
    """

    methods = ['GET']

    def __init__(self, channel_endpoint=None, channel_name=None,
                 subtitle=None):
        self.channel_endpoint = channel_endpoint
        self.channel_name = channel_name
        self.subtitle = subtitle

    @property
    def identity(self):
        return Identity.get(g.user.id_)

    @property
    def channel_url(self):
        if self.channel_endpoint:
            return url_for(self.channel_endpoint)

    @property
    def next_url(self):
        return request.args.get('next') or url_for('home.home')

    def make_context(self):
        return {
            'identity': self.identity,
            'mobile_phone': g.user.mobile,
            'subtitle': self.subtitle,
            'channel_name': self.channel_name,
            'channel_url': self.channel_url,
            'next_url': self.next_url,
        }

    def render_template(self, **kwargs):
        context = self.make_context()
        context.update(kwargs)
        return render_template('profile/auth.html', **context)

    def dispatch_request(self):
        if not g.user:
            return redirect(url_for('accounts.login.login', next=request.url))
        if has_real_identity(g.user):
            return redirect(self.next_url)
        return self.render_template()
