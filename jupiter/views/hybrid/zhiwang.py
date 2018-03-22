# coding:utf-8

from __future__ import absolute_import

from flask import g, abort
from flask_mako import render_template

from jupiter.utils.hybrid import hybrid_view
from core.models.hoard.zhiwang import ZhiwangAsset
from core.models.hoard.zhiwang.loan import ZhiwangLoansDigest
from core.models.hoard.zhiwang.consts import FETCH_LOANS_TIMEOUT, FETCH_LOANS_LIMIT_TIMES
from core.models.hoard.zhiwang.transaction import fetch_loans_digest
from core.models.hoard.zhiwang.errors import FetchLoansDigestError
from core.models.utils.limit import Limit, LIMIT
from .blueprint import create_blueprint


bp = create_blueprint('zhiwang', __name__, url_prefix='/hybrid/savings')


@bp.route('/loans-digest/<int:asset_id>', methods=['GET'])
@hybrid_view(['savings_r'])
def fetch_digest(asset_id):
    error = ''
    asset = ZhiwangAsset.get(asset_id)

    if not asset:
        abort(404)

    if not asset.is_owner(g.user):
        abort(403)

    loans_digest = ZhiwangLoansDigest.get_by_asset_id(asset.id_)
    if loans_digest:
        l = Limit.get(LIMIT.USER_FETCH_ZW_LOANS % g.user.id_,
                      timeout=FETCH_LOANS_TIMEOUT, limit=FETCH_LOANS_LIMIT_TIMES)
        loans_digest = fetch_loans_digest(asset) if not l.is_limited() else loans_digest
        l.touch()
    else:
        try:
            loans_digest = fetch_loans_digest(asset)
        except FetchLoansDigestError as e:
            error = unicode(e)
    return render_template('savings/loans.html', loans_digest=loans_digest, error=error)
