# coding: utf-8

from datetime import timedelta

from weakref import WeakValueDictionary

from sms_client.provider import YUNPIAN, YIMEI_AD

from core.models.base import EntityModel
from core.models.user.consts import VERIFY_CODE_TYPE
from core.models.welfare.package.kind import newcomer_package


class ShortMessageKind(EntityModel):

    storage = WeakValueDictionary()

    def __init__(self, id_, content, is_advertisement=False, need_verify=False,
                 verify_type=None, verify_delta=None):
        if id_ in self.storage:
            raise ValueError('id_ %s has been used' % id_)

        if need_verify:
            if verify_type not in VERIFY_CODE_TYPE.values():
                raise ValueError('invalid verify code type %s' % verify_type)
            if not isinstance(verify_delta, timedelta):
                # TODO: 规范不同类型验证码校验时限
                raise ValueError('invalid verify delta %s' % verify_delta)

        self.id_ = id_
        self.content = content
        self.is_advertisement = is_advertisement
        self.prefer_provider = YIMEI_AD if is_advertisement else YUNPIAN
        self.need_verify = need_verify
        self.verify_type = verify_type
        self.verify_delta = verify_delta
        self.storage[id_] = self

    @classmethod
    def get(cls, id_):
        return cls.storage.get(id_)

register_sms = ShortMessageKind(
    id_=1,
    content=u'欢迎注册好规划网，本次验证码为：{verify_code}，请勿将验证码告知他人',
    need_verify=True,
    verify_type=VERIFY_CODE_TYPE.REG_MOBILE,
    verify_delta=timedelta(hours=1)
)


mobile_bind_sms = ShortMessageKind(
    id_=2,
    content=u'您正在使用好规划手机号绑定服务，本次验证码为：{verify_code}，'
            u'请勿将验证码告知他人',
    need_verify=True,
    verify_type=VERIFY_CODE_TYPE.BIND_MOBILE,
    verify_delta=timedelta(hours=1)
)


forgot_password_sms = ShortMessageKind(
    id_=3,
    content=u'您正使用找回密码功能，验证码：{verify_code}，请勿将验证码告知他人',
    need_verify=True,
    verify_type=VERIFY_CODE_TYPE.FORGOT_PASSWORD_MOBILE,
    verify_delta=timedelta(hours=1)
)


change_mobile_verify_origin_sms = ShortMessageKind(
    id_=4,
    content=u'您正申请修改登录手机号，此次验证原手机号的验证码为：'
            u'{verify_code}，如非本人操作请立刻联系微信客服。',
    need_verify=True,
    verify_type=VERIFY_CODE_TYPE.CHANGE_MOBILE_VERIFY_OLD,
    verify_delta=timedelta(hours=1)
)


change_mobile_set_new_sms = ShortMessageKind(
    id_=5,
    content=u'您正申请修改登录手机号，此次设置新手机号的验证码为：'
            u'{verify_code}，如非本人操作请立刻联系微信客服。',
    need_verify=True,
    verify_type=VERIFY_CODE_TYPE.CHANGE_MOBILE_SET_NEW,
    verify_delta=timedelta(hours=1)
)

withdraw_sms = ShortMessageKind(
    id_=6,
    content=u'您正申请提现{withdraw_amount}元，验证码{verify_code}，如非本人操'
            u'作请立刻联系微信客服。',
    need_verify=True,
    verify_type=VERIFY_CODE_TYPE.REBATE_WITHDRAW,
    verify_delta=timedelta(hours=1)
)

bind_mobile_and_withdraw_sms = ShortMessageKind(
    id_=7,
    content=u'您正申请绑定该手机号并提现{withdraw_amount}元，验证码'
            u'{verify_code}，请勿将验证码告知他人。',
    need_verify=True,
    verify_type=VERIFY_CODE_TYPE.REBATE_WITHDRAW,
    verify_delta=timedelta(hours=1)
)

withdraw_notify_sms = ShortMessageKind(
    id_=8,
    content=u'尊敬的好规划用户，已经向您尾号为{tail_number}的银行卡发放'
            u'{amount}元返现福利，如有任何问题请咨询微信（plan141)客服。',
)

savings_order_exited_sms = ShortMessageKind(
    id_=9,
    content=u'您的{order_amount}元攒钱助手已转出，收益{profit}元。'
            u'送你0.3%加息券，要坚持攒钱哦！http://dwz.cn/2n4EF3',
    is_advertisement=True,
)

birthday_package_remind_sms = ShortMessageKind(
    id_=10,
    content=u'今天好像是个特别的日子哦：）送您「生日祝福券」，全场加息0.6%，快'
            u'来攒钱助手看看吧。http://dwz.cn/2jyo7U',
    is_advertisement=True
)

broken_bankcard_remind_sms = ShortMessageKind(
    id_=11,
    content=u'尊敬的好规划用户，您有一笔即将到期的交易由于银行卡信息问题无法顺'
            u'利回款，请及时与好规划微信客服（plan141）联系解决',
)

savings_first_asset_exited_sms = ShortMessageKind(
    id_=12,
    content=u'您的{order_amount}元攒钱助手已转出，收益{profit}元。'
            u'送您全场加息券与满减券，要坚持攒钱哦！http://dwz.cn/2xbp0J',
    is_advertisement=True,
)

register_package_sms = ShortMessageKind(
    id_=13,
    content=u'您已成功注册好规划！{}元新手大礼包已发放到您的账户，'
            u'立即下载客户端查看 http://dwz.cn/2ylxtn '.format(
                newcomer_package.sum_deduct),
    is_advertisement=True
)

women_day_2016_register_sms = ShortMessageKind(
    id_=14,
    content=u'女王节快乐，欢迎加入好规划，请访问官网 guihua.com 完成注册即可使用115元礼券和0.38%加息券',
    is_advertisement=True,
)

savings_order_success_sms = ShortMessageKind(
    id_=15,
    content=u'恭喜，您于{time}在好规划攒钱助手成功购买{amount}元'
            u'{product}(期限{period}，预期年化收益{rate}%)。'
)

savings_order_success_sms_sxb = ShortMessageKind(
    id_=16,
    content=u'恭喜，您于{time}在好规划成功购买{amount}元随心攒产品。'
            u'起息日为{value_date}，首次查看收益日期为{earnings_day}。邀请好友攒钱可获攒钱红包。'
)

savings_redeem_success_sms_sxb = ShortMessageKind(
    id_=17,
    content=u'您于{time}在好规划成功提交{amount}元随心攒提现申请，'
            u'将于0-3个工作日后回款至{bankname}（尾号{bankno}）账户，请注意查收。'
)
