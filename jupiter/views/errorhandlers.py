# coding: utf-8

from flask import Blueprint
from flask_mako import render_template

from .errors import ChallengeFailError


bp = Blueprint('errors', __name__)


@bp.app_errorhandler(ChallengeFailError)
def challenge_error(error):
    return render_template('errors/challenge_error.html'), 403
