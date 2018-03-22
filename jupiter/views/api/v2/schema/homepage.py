# coding: utf-8

from marshmallow import Schema, fields


class Banner(Schema):
    """ 每条 banner 数据 """
    #: :class:`str` id
    banner_id = fields.String(attribute='id_')
    #: :class:`str` 名称
    name = fields.String()
    #: :class:`.url` 图片url
    image_url = fields.Url()
    #: :class:`.url` 跳转url
    link_url = fields.Url()


class BannerResponseSchema(Schema):
    """ banner 请求返回 """

    #: :class:`.Banner` list of banners
    banners = fields.Nested(Banner, many=True)
    #: :class:`~int` 时间戳
    timestamp = fields.Integer()


class BulletinResponseSchema(Schema):
    """ 公告请求返回 """
    #: :class:`str` id
    bulletin_id = fields.String(attribute='id_')
    #: :class:`.url` 公告标题
    title = fields.String()
    #: :class:`.url` 公告内容
    content = fields.String()
    #: :class:`.url` 跳转url
    link_url = fields.String(attribute='target_link')
    #: :class:`~int` 时间戳
    timestamp = fields.Integer()
