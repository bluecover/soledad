# coding: utf-8

from flask import Blueprint, redirect, url_for


bp = Blueprint('welfare.compat', __name__)


@bp.route('/savings/withdraw/')
@bp.route('/savings/withdraw')
def withdraw():
    return redirect(url_for('welfare.index', dcm='guihua', dcs='withdraw'))
