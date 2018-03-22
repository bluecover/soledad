# coding: utf-8

from __future__ import print_function, absolute_import, unicode_literals

from flask import Blueprint, g
from flask_mako import render_template

from core.models.bank import Partner, bank_collection
from core.models.wallet import PublicDashboard


bp = Blueprint('help', __name__)


@bp.before_request
def list_banks():
    g.savings_banks = [
        b for b in bank_collection.banks
        if Partner.zw in b.available_in]


@bp.route('/help')
def help():
    return render_template('help/help_savings.html')


@bp.route('/help/childins')
def help_childins():
    return render_template('help/help_childins.html')


@bp.route('/help/ins')
def help_ins():
    return render_template('help/help_ins.html')


@bp.route('/help/savings')
def help_savings():
    return render_template('help/help_savings.html')


@bp.route('/help/fund')
def help_fund():
    return render_template('help/help_fund.html')


@bp.route('/help/wallet')
def help_wallet():
    return render_template(
        'help/help_wallet.html', provider=PublicDashboard.provider)
