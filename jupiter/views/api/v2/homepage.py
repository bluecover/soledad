# coding: utf-8

import time
from datetime import datetime

from flask import jsonify

from core.models.site.app_banner import AppBanner
from core.models.site.bulletin import Bulletin
from jupiter.views.api.decorators import anonymous_oauth
from ..blueprint import create_blueprint_v2, conditional_for_v2
from .schema.homepage import BannerResponseSchema, BulletinResponseSchema

bp = create_blueprint_v2('homepage', 'v2', __name__, url_prefix='/homepage')


@bp.route('/banner', methods=['GET'])
@anonymous_oauth(['basic'])
def banner():
    """返回当前可用banners.

    :reqheader Authorization: OAuth 2.0 Bearer Token
    :reqheader If-None-Match: 客户端缓存的 ETag
    :resheader ETag: 客户端可缓存的 ETag
    :status 304: 客户端缓存未过期, 无需返回数据
    :status 200: 返回 :class:`.BannerResponseSchema`
    """

    active_banners = AppBanner.gets_by_status(AppBanner.Status.enabled)
    conditional_for_v2(
        u'{b.id_}#{b.name}#{b.image_url}#{b.link_url}'.format(b=b) for b in active_banners
    )

    schema_obj = {
        'banners': active_banners,
        'timestamp': int(time.time() * 1000)
    }
    response_schema = BannerResponseSchema(strict=True)
    return jsonify(success=True, data=response_schema.dump(schema_obj).data)


@bp.route('/bulletin', methods=['GET'])
@anonymous_oauth(['basic'])
def bulletin():
    """返回公告

    :reqheader Authorization: OAuth 2.0 Bearer Token
    :reqheader If-None-Match: 客户端缓存的 ETag
    :resheader ETag: 客户端可缓存的 ETag
    :status 304: 客户端缓存未过期, 无需返回数据
    :status 200: 返回 :class:`.BulletinResponseSchema`
    """
    current_time = datetime.now()
    latest_bulletin = Bulletin.get_app_latest()
    if not latest_bulletin or latest_bulletin.expire_time < current_time:
        return jsonify(success=True, data={})

    conditional_for_v2(
        u'{b.id_}#{b.title}#{b.content}#{b.target_link}'.format(b=b) for b in [latest_bulletin]
    )

    latest_bulletin.timestamp = int(time.time() * 1000)

    bulletin_response_schema = BulletinResponseSchema()
    return jsonify(success=True, data=bulletin_response_schema.dump(latest_bulletin).data)
