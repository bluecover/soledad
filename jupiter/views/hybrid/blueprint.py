# coding: utf-8

from __future__ import absolute_import

from flask import Blueprint
from flask_mako import render_template


def create_blueprint(name, package_name, **kwargs):
    bp = Blueprint('hybrid.' + name, package_name, **kwargs)

    @bp.errorhandler(401)
    def handle_unauthorized(error):
        return render_template('errors/hybrid_401.html', error=error), 401

    return bp
