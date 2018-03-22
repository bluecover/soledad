# coding: utf-8

from datetime import timedelta
from flask_script import Manager

from libs.utils.log import bcolors
from core.models.oauth import OAuthToken


manager = Manager()
manager.__doc__ = 'The commands for OAuth 2.0 management.'


@manager.command
def vacuum_tokens(token_ids='', grace_days=0):
    """Clean up expired tokens from database."""
    grace_time = timedelta(days=int(grace_days))
    ids = [id_.strip() for id_ in token_ids.split(',') if id_.strip()]
    if ids:
        if all(id_.isdigit() for id_ in ids):
            OAuthToken.vacuum(ids, grace_time=grace_time)
        else:
            bcolors.fail(
                '"-t" should be comma-splited digits (e.g. "10001,10002")')
            return
    else:
        OAuthToken.vacuum(grace_time=grace_time)  # vacuum all tokens
