# coding: utf-8

from __future__ import absolute_import

import hashlib

from flask import Blueprint, jsonify, request, current_app, g
from marshmallow import ValidationError, UnmarshallingError
from werkzeug.exceptions import HTTPException

from jupiter.ext import sentry, limiter
from core.models.welfare.coupon.errors import CouponError


class BlueprintFactory(object):
    def __init__(self, allowed_versions, conditional_version,
                 common_rate_limit, blueprint_class):
        self.allowed_versions = list(allowed_versions)
        self.conditional_version = conditional_version
        self.common_limit_for = limiter.shared_limit(
            common_rate_limit, scope=lambda endpoint: endpoint)
        self.blueprint_class = blueprint_class

    def __call__(self, name, version, package_name, **kwargs):
        """Creates blueprint to sort the API views.

        :param name: The endpoint name.
        :param version: The API version.
        :param package_name: Always be ``__name__``.
        :param url_prefix: The prefix of relative URL.
        """
        blueprint = self.make_blueprint(name, version, package_name, **kwargs)
        blueprint = self.init_blueprint(blueprint)
        return blueprint

    def make_blueprint(self, name, version, package_name, **kwargs):
        assert version in self.allowed_versions
        url_prefix = kwargs.pop('url_prefix', '')
        url_prefix = '/api/{version}{url_prefix}'.format(
            version=version, url_prefix=url_prefix)
        blueprint_name = 'api-{version}.{name}'.format(
            name=name, version=version)
        return Blueprint(
            blueprint_name, package_name, url_prefix=url_prefix, **kwargs)

    def init_blueprint(self, blueprint):
        blueprint.errorhandler(ValidationError)(self.handle_validation_error)
        blueprint.errorhandler(UnmarshallingError)(self.handle_unmarshalling_error)
        blueprint.errorhandler(CouponError)(self.handle_coupon_error)
        blueprint.errorhandler(400)(self.handle_http_exception)
        blueprint.errorhandler(401)(self.handle_http_exception)
        blueprint.errorhandler(403)(self.handle_http_exception)
        blueprint.errorhandler(404)(self.handle_http_exception)
        blueprint.errorhandler(405)(self.handle_http_exception)
        blueprint.errorhandler(410)(self.handle_http_exception)
        blueprint.errorhandler(503)(self.handle_http_exception)
        blueprint.errorhandler(429)(self.handle_rate_limit_exceeded)

        blueprint.before_request(self.before_request_raven)
        blueprint.before_request(self.before_request_lint)
        blueprint.after_request(self.after_request_conditional)

        self.common_limit_for(blueprint)
        return blueprint

    def before_request_raven(self):
        if not hasattr(request, 'oauth'):
            return
        sentry.user_context({
            'id': request.oauth.user.id_,
            'email': request.oauth.user.email,
            'mobile': request.oauth.user.display_mobile,
            'via': 'oauth'})

    def before_request_lint(self):
        if current_app.debug and request.cookies:
            return jsonify(success=False, messages={
                '_': [u'Cookies should be excluded from requests.'],
            }), 400

    def handle_validation_error(self, error):
        return jsonify(success=False, messages=error.messages), 400

    def handle_unmarshalling_error(self, error):
        return jsonify(success=False, messages={'_': [error.args[0]]}), 400

    def handle_coupon_error(self, error):
        sentry.captureException()
        return jsonify(success=False, messages={'_': [error.args[0]]}), 403

    def handle_http_exception(self, error):
        messages = {'_': [unicode(error.description)]}
        return jsonify(success=False, messages=messages), error.code

    def handle_rate_limit_exceeded(self, error):
        if isinstance(error.description, unicode):
            messages = {'_': [error.description]}
        else:
            messages = {'_': [u'您访问的速度太快了，请稍后再试']}
        return jsonify(success=False, messages=messages), error.code

    def after_request_conditional(self, response):
        etag = g.get('conditional_etag')
        if etag is not None:
            response.set_etag(etag)
        return response

    def conditional_for(self, iterable, version=None):
        """Setup conditional request with specific identities.

        The current request will be terminated as ``304 Not Modified`` while
        accessing unchanged resources.
        """
        version = self.conditional_version if version is None else version
        origin = u'{0}|{1}:{2}'.format(
            request.endpoint, ''.join(iterable), version)
        digest = hashlib.sha1(origin.encode('utf-8')).hexdigest()
        if request.if_none_match(digest):
            raise NotModified()
        g.conditional_etag = digest


class NotModified(HTTPException):
    code = 304
    description = (
        u'The resource has not been modified since the version specified in '
        u'If-Modified-Since or If-Match headers. The resource will not be '
        u'returned in response body.'
    )
