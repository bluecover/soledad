# coding: utf-8

from itertools import chain
from flask import jsonify, g, Blueprint, request, abort, url_for
from flask_wtf import Form
from wtforms import IntegerField
from wtforms.validators import DataRequired, NumberRange

from core.models.hoard import HoardProfile, HoardRebate
from core.models.hoard.manager import SavingsManager
from core.models.hoard.providers import yirendai, zhiwang, placebo, xmpay
from core.models.hoard.zhiwang import ZhiwangAsset, ZhiwangProfile
from core.models.hoard.xinmi import XMProfile, XMAsset
from core.models.hoard.placebo import PlaceboOrder
from core.models.utils.switch import spring_promotion_switch
from core.models.utils import round_half_up

bp = Blueprint('jsavings', __name__, url_prefix='/j/savings')


@bp.route('/update_amount', methods=['POST'])
def update_savings_amount():
    if not g.user:
        abort(401)

    form = PlanAmountForm()
    if not form.validate():
        return jsonify(r=False, error='\n'.join(chain(*form.errors.values())))

    profile = HoardProfile.add(g.user.id)
    profile.plan_amount = form.data['amount']

    return jsonify(r=True)


class PlanAmountForm(Form):
    amount = IntegerField('amount', validators=[
        DataRequired(message=u'请输入目标金额'),
        NumberRange(min=1000, max=9999999,
                    message='金额应在 %(min)s 至 %(max)s 之间'),
    ])


@bp.route('/orders')
def orders():
    if not g.user:
        abort(401)

    limit = int(request.args.get('limit', 0))
    filtered = bool(request.args.get('filter'))
    info = {}
    savings_records = []

    yx_profile = HoardProfile.add(g.user.id_)
    zw_profile = ZhiwangProfile.add(g.user.id_)
    xm_profile = XMProfile.add(g.user.id_)
    yx_orders = yx_profile.orders(filter_due=filtered)
    zw_mixins = zw_profile.mixins(filter_due=filtered)
    xm_mixins = xm_profile.mixins(filter_due=filtered)

    placebo_order_ids = PlaceboOrder.get_ids_by_user(g.user.id_)
    placebo_orders = PlaceboOrder.get_multi(placebo_order_ids)
    if filtered:
        placebo_orders = [
            o for o in placebo_orders if o.status is not PlaceboOrder.Status.exited]
    placebo_mixins = [(order,) for order in placebo_orders]

    records = yx_orders + zw_mixins + xm_mixins + placebo_mixins
    if filtered:
        records = sorted(records, key=lambda x: x[0].due_date)
    else:
        records = sorted(records, key=lambda x: x[0].creation_time, reverse=True)
    saving_manager = SavingsManager(g.user.id_)

    info['plan_amount'] = yx_profile.plan_amount
    info['on_account_invest_amount'] = round_half_up(saving_manager.on_account_invest_amount, 2)
    info['fin_ratio'] = round_half_up(saving_manager.fin_ratio, 2)
    info['daily_profit'] = round_half_up(saving_manager.daily_profit, 2)
    info['total_profit'] = round_half_up(saving_manager.total_profit, 2)
    limit = limit if 0 < limit < len(records) else len(records)

    for record_info in records[:limit]:
        data = dict()
        base_record = record_info[0]
        exit_type = u'到期自动转回银行卡'

        if base_record.provider is yirendai:
            order, order_info, order_status = record_info
            rebates = HoardRebate.get_by_order_pk(order.id_)

            data['annual_rate'] = order.service.expected_income
            data['frozen_time'] = '%s 个月' % order.service.frozen_time
            data['order_status'] = order_status
            data['savings_money'] = order_info['investAmount']
            data['invest_date'] = order_info['investDate']
            data['exit_type'] = exit_type if order_info['exitType'] == u'退回到划扣银行卡' else order_info[
                'exitType']

            if rebates:
                data['rebates'] = HoardRebate.get_display(rebates)

            if order_status == u'确认中':
                data['interest_start_date'] = u'攒钱后1-3工作日'
            else:
                data['interest_start_date'] = order_info['startCalcDate']

            if order_status == u'已转出':
                data['income_amount'] = u'%s 元' % order_info['incomeAmount']
            else:
                data['expect_income_amount'] = u'%s 元' % order_info[
                    'expectedIncomeAmount']

            data['due_date'] = order.due_date.strftime('%Y-%m-%d')

            if order.bankcard:
                data['bankcard'] = u'%s (%s)' % (
                    order.bankcard.bank_name, order.bankcard.display_card_number)
        elif base_record.provider is zhiwang:
            order, asset = record_info

            data['annual_rate'] = round_half_up(order.actual_annual_rate, 2)
            if order.profit_period.unit == 'day':
                data['frozen_time'] = '%s 天' % order.profit_period.value
            elif order.profit_period.unit == 'month':
                data['frozen_time'] = '%s 个月' % order.profit_period.value
            else:
                raise ValueError('invalid unit %s' % order.profit_period.unit)

            data['order_status'] = asset.display_status if asset else order.display_status
            if order.profit_hikes:
                data['hikes'] = {h.kind.label: h.display_text for h in order.profit_hikes}
            data['savings_money'] = int(order.amount)
            data['invest_date'] = unicode(order.creation_time.date())
            data['exit_type'] = exit_type
            data['interest_start_date'] = order.start_date.strftime('%Y-%m-%d')
            if asset and asset.status == ZhiwangAsset.Status.redeemed:
                data['income_amount'] = u'%s 元' % round_half_up(
                    asset.current_interest, 2)
            else:
                # 尽可能显示已加息收益
                # FIXME (tonyseek) 这个做法太粗暴，有赖于资产的更新
                if order.asset:
                    expect_interest = order.asset.expect_interest
                else:
                    expect_interest = order.expect_interest
                data['expect_income_amount'] = u'%s 元' % round_half_up(
                    expect_interest, 2)
            data['due_date'] = order.due_date.strftime('%Y-%m-%d')

            data['contract_url'] = url_for(
                'savings.zhiwang.asset_contract', asset_no=asset.asset_no) if asset else ''
            if asset and asset.bankcard:
                # 指旺回款卡以资产的银行卡为准，可能会与订单中的不一致
                data['bankcard'] = u'%s (%s)' % (
                    asset.bankcard.bank.name, asset.bankcard.display_card_number)
        elif base_record.provider is placebo:
            if base_record.status is PlaceboOrder.Status.failure:
                continue
            order = base_record
            profit_amount = order.calculate_profit_amount()
            profit_amount_text = u'%s 元' % round_half_up(profit_amount, 2)
            if base_record.status is PlaceboOrder.Status.exited:
                data['income_amount'] = profit_amount_text
            else:
                data['expect_income_amount'] = profit_amount_text
            data['annual_rate'] = round_half_up(order.profit_annual_rate, 2)
            data['frozen_time'] = order.profit_period.display_text
            data['order_status'] = order.status.display_text
            data['order_type'] = u'体验金'

            data['spring_festival'] = spring_promotion_switch.is_enabled

            data['savings_money'] = int(order.amount)
            data['invest_date'] = unicode(order.start_date)
            data['due_date'] = unicode(order.due_date.date())
            data['bankcard'] = u'%s (%s)' % (
                order.bankcard.bank.name, order.bankcard.display_card_number)
        elif base_record.provider is xmpay:
            order, asset = record_info

            data['annual_rate'] = round_half_up(order.actual_annual_rate, 2)
            if order.profit_period.unit == 'day':
                data['frozen_time'] = '%s 天' % order.profit_period.value
            elif order.profit_period.unit == 'month':
                data['frozen_time'] = '%s 个月' % order.profit_period.value
            else:
                raise ValueError('invalid unit %s' % order.profit_period.unit)

            data['order_status'] = asset.display_status if asset else order.display_status
            if order.profit_hikes:
                data['hikes'] = {h.kind.label: h.display_text for h in order.profit_hikes}
            data['savings_money'] = int(order.amount)
            data['invest_date'] = unicode(order.creation_time.date())
            data['exit_type'] = exit_type
            data['interest_start_date'] = order.start_date.strftime('%Y-%m-%d')
            if asset and asset.status == XMAsset.Status.redeemed:
                data['income_amount'] = u'%s 元' % round_half_up(
                    asset.current_interest, 2)
            else:
                # 尽可能显示已加息收益
                if order.asset:
                    expect_interest = order.asset.expect_interest
                else:
                    expect_interest = order.expect_interest
                data['expect_income_amount'] = u'%s 元' % round_half_up(
                    expect_interest, 2)
            # 尽量使用第三方返回的到期日期。
            if order.asset:
                data['due_date'] = order.asset.interest_end_date.strftime('%Y-%m-%d')
            else:
                data['due_date'] = order.due_date.strftime('%Y-%m-%d')

            data['contract_url'] = url_for(
                'savings.xinmi.asset_contract', asset_no=asset.asset_no) if asset else ''
            if asset and asset.bankcard:
                # 投米回款卡以资产的银行卡为准，可能会与订单中的不一致
                data['bankcard'] = u'%s (%s)' % (
                    asset.bankcard.bank_name, asset.bankcard.display_card_number)
        savings_records.append(data)
    return jsonify(r=True, records=savings_records, info=info)
