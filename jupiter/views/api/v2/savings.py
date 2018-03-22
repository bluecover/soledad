# coding: utf-8

from flask import request, g, jsonify, abort

from core.models.hoard.xinmi.account import XMAccount
from core.models.hoarder.vendor import Vendor, Provider
from core.models.hoarder.account import Account as HoardAccount
from core.models.profile.bankcard import BankCardManager
from core.models.welfare import CouponManager
from core.models.hoarder.errors import (
    AccountError as SxbAccountError, ProductError as SxbProductError, OrderError as SxbOrderError,
    TradeError as SxbTradeError)
from core.models.hoard.xinmi.errors.account_errors import (
        AccountError as XMAccountError, SignUpError as XMSignUpError)
from core.models.hoard.xinmi.errors.trade_errors import TradeError as XMTradeError
from core.models.hoard.xinmi.errors.product_errors import ProductError as XMProductError
from core.models.hoard.xinmi.errors.payment_errors import PayError as XMPayError
from core.models.hoard.zhiwang.profit_hike import ProfitHikeLockedError
from core.models.welfare.coupon.errors import (CouponError, CouponUsageError)
from core.models.welfare.firewood.errors import FirewoodException
from jupiter.views.api.decorators import require_oauth
from .products.sxb import (
    purchase as sxb_purchase, sxb_auth, purchase_verify as sxb_purchase_verify)
from .products.xinmi import purchase as xm_purchase, xm_auth, purchase_verify as xm_purchase_verify
from .products.errors import SmsEmptyError, XMError, BankCardError, CouponOwnershipError
from ..blueprint import create_blueprint_v2


bp = create_blueprint_v2('savings', 'v2', __name__, url_prefix='/savings')


@bp.before_request
@require_oauth(['savings_r'])
def initialize_user():
    if hasattr(request, 'oauth'):
        g.user = request.oauth.user
    else:
        g.user = None


@bp.before_request
@require_oauth(['savings_r'])
def initialize_remote_account():
    if hasattr(request, 'oauth'):
        g.xm_account = XMAccount.get_by_local(request.oauth.user.id_)
        vendor = Vendor.get_by_name(Provider.sxb)
        if vendor:
            g.sxb_account = HoardAccount.get_by_local(vendor.id_, request.oauth.user.id_)
    else:
        g.xm_account = None
        g.sxb_account = None


@bp.before_request
@require_oauth(['user_info'])
def initialize_bankcard_manager():
    if hasattr(request, 'oauth'):
        g.bankcard_manager = BankCardManager(request.oauth.user.id_)
    else:
        g.bankcard_manager = None


@bp.before_request
@require_oauth(['user_info'])
def initialize_coupons():
    if hasattr(request, 'oauth'):
        g.coupon_manager = CouponManager(request.oauth.user.id_)


@bp.route('/order', methods=['POST'])
@require_oauth(['savings_w'])
def purchase():
    """选购规划产品, 创建理财单.

    :request: :class:`.products.xinmi.XinmiPurchaseSchema`
              or :class:`.products.sxb.PurchaseSchema`

    :reqheader Authorization: OAuth 2.0 Bearer Token
    :status 403: 因为未完成实名认证或产品方面原因, 购买请求被拒
    :status 201: 订单已创建, 返回 :class:`.products.xinmi.XinmiOrderSchema`
                                  or :class:`.products.sxb.OrderSchema`
    """
    result = request.get_json(force=True)
    if result['vendor'] == Provider.xm.value:
        if not g.xm_account:
            try:
                xm_auth(request.oauth.user.id_)
                g.xm_account = XMAccount.get_by_local(request.oauth.user.id_)
            except (XMAccountError, XMSignUpError) as e:
                abort(403, unicode(e))
        try:
            order = xm_purchase(result, g)
        except (BankCardError, CouponOwnershipError, XMError) as e:
            abort(403, unicode(e))
        except (XMProductError, XMTradeError) as e:
            abort(403, unicode(e))
        except (CouponError, CouponUsageError) as e:
            abort(403, unicode(e))
        except FirewoodException as e:
            abort(403, unicode(e))
        return jsonify(success=True, data=order), 201

    if result['vendor'] == Provider.sxb.value:
        if not g.sxb_account:
            try:
                sxb_auth(request.oauth.user.id_)
                vendor = Vendor.get_by_name(Provider.sxb)
                if vendor:
                    g.sxb_account = HoardAccount.get_by_local(vendor.id_, request.oauth.user.id_)
            except SxbAccountError as e:
                abort(403, unicode(e))
        try:
            order = sxb_purchase(result, g)
        except (BankCardError, CouponOwnershipError) as e:
            abort(403, unicode(e))
        except SxbProductError as e:
            abort(403, unicode(e))
        except SxbOrderError as e:
            abort(403, unicode(e))
        except SxbTradeError as e:
            abort(403, unicode(e))
        except (CouponError, CouponUsageError) as e:
            abort(403, unicode(e))
        except FirewoodException as e:
            abort(403, unicode(e))

        return jsonify(success=True, data=order), 201


@bp.route('/order/<int:order_id>/verify', methods=['POST'])
@require_oauth(['savings_w'])
def purchase_verify(order_id):
    """提供短信验证码, 支付理财单.

    :request: :class:`.products.xinmi.XinmiVerifySchema` or :class:`.products.sxb.VerifySchema`

    :reqheader Authorization: OAuth 2.0 Bearer Token
    :status 403: 支付出错
    :status 200: 支付成功, 返回 :class:`.XinmiOrderSchema` or :class:`.products.sxb.OrderSchema`
    """
    result = request.get_json(force=True)
    if result['vendor'] == Provider.xm.value:
        try:
            order = xm_purchase_verify(order_id, result, request)
        except (XMError, SmsEmptyError) as e:
            abort(403, unicode(e))
        except (XMTradeError, XMPayError) as e:
            abort(403, unicode(e))
        except (CouponError, CouponUsageError) as e:
            abort(403, unicode(e))
        except FirewoodException as e:
            abort(403, unicode(e))
        return jsonify(success=True, data=order), 201

    if result['vendor'] == Provider.sxb.value:
        try:
            order = sxb_purchase_verify(order_id, result, request)
        except SmsEmptyError:
            abort(400)
        except ProfitHikeLockedError as e:
            abort(403, unicode(e))
        except SxbOrderError as e:
            abort(403, unicode(e))
        except SxbTradeError as e:
            abort(403, unicode(e))
        except (CouponError, CouponUsageError) as e:
            abort(403, unicode(e))
        except FirewoodException as e:
            abort(403, unicode(e))
        return jsonify(success=True, data=order), 201
