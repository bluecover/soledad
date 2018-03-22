# coding: utf-8

"""
    product ui
"""

from flask import abort
from flask_mako import render_template

from core.models.product.consts import FUND_TYPE, INSURE_TYPE
from core.models.product.p2p import P2P
from core.models.product.fund import Fund
from core.models.product.insure import Insure

from ._blueprint import create_blueprint


bp = create_blueprint('product', __name__)


@bp.route('/product')
@bp.route('/product/p2p')
def p2p():
    cur_path = 'p2p'
    ps = P2P.get_all()
    p2p_property = [('预期年化收益率', 'year_rate'),
                    ('返还方式', 'pay_return_type'),
                    ('投资期限', 'deadline'),
                    ('购买起点', 'min_money'),
                    ('保障', 'protect')]
    return render_template('product/p2p.html', **locals())


@bp.route('/product/insurance')
@bp.route('/product/insurance/<insure_type>')
def insurance(insure_type='disease'):
    if insure_type not in ('disease', 'life', 'accident', 'children'):
        abort(403, 'not valid insure type')
    cur_path = insure_type
    i_type = INSURE_TYPE.get(insure_type.upper())
    ps = Insure.gets_by_type(i_type)
    insure_property = [('保险期间', 'duration'),
                       ('缴费期限', 'pay_duration'),
                       ('保险责任', 'insure_duty'),
                       ('适合人群', 'throng'),
                       ('保费预估', 'prospect')]
    return render_template('product/insurance.html', **locals())


@bp.route('/product/funds')
@bp.route('/product/funds/<funds_type>')
def funds(funds_type='mmf'):
    if funds_type not in ('mmf', 'bond', 'index', 'stock'):
        abort(403, 'not valid funds type')
    cur_path = funds_type
    f_type = FUND_TYPE.get(funds_type.upper())
    ps = Fund.gets_by_type(f_type)
    funds_property = [('基金代码', 'code'),
                      ('成立日期', 'found_date'),
                      ('跟踪指数', 'index'),
                      ('风险', 'risk'),
                      ('基金经理', 'manager'),
                      ('近一年涨幅', 'year_rate'),
                      ('别名', 'nickname')]
    return render_template('product/funds.html', **locals())
