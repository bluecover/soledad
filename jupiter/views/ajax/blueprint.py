# coding: utf-8

from __future__ import print_function, absolute_import, unicode_literals

from flask import Blueprint, jsonify


def create_blueprint(name, package_name, **kwargs):
    blueprint_name = 'ajax.{name}'.format(name=name)
    blueprint = Blueprint(blueprint_name, package_name, **kwargs)

    @blueprint.errorhandler(ValidationMixin.ValidationError)
    def handle_validation_error(error):
        errors = [e for errors in error.args[0].values() for e in errors]
        return jsonify(r=False, error='\n'.join(errors)), 400

    @blueprint.errorhandler(400)
    @blueprint.errorhandler(401)
    @blueprint.errorhandler(403)
    @blueprint.errorhandler(404)
    @blueprint.errorhandler(405)
    @blueprint.errorhandler(410)
    def handle_http_exception(error):
        return jsonify(r=False, error=unicode(error.description)), error.code

    return blueprint


class ValidationMixin(object):
    """The validation trait which integrates with WTForms."""

    class ValidationError(ValueError):
        pass

    def raise_for_validation(self):
        if not self.validate():
            raise self.ValidationError(self.errors)
