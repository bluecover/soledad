# coding: utf-8

from uuid import uuid4, UUID

from sms_client.client import SMSClient

from jupiter.workers.sms import sms_sender as mq_sms_sender
from libs.logger.rsyslog import rsyslog
from core.models import errors
from core.models.user.account import Account
from core.models.user.verify import Verify
from core.models.mixin.props import PropsMixin, PropsItem
from core.models.utils.validator import validate_phone
from .kind import ShortMessageKind


class ShortMessage(PropsMixin):
    """短消息"""

    # default tag
    tag = u'好规划'

    # storage of sms sending info
    receiver_mobile = PropsItem('receiver_mobile', '')
    sms_kind_id = PropsItem('sms_kind_id', '')
    sms_args = PropsItem('sms_args', {})
    is_sent = PropsItem('is_sent', False)

    def __init__(self, uuid):
        self.uuid = UUID(uuid)

    def get_db(self):
        return 'sms'

    def get_uuid(self):
        return 'item:{uuid}'.format(uuid=self.uuid.hex)

    @property
    def kind(self):
        return ShortMessageKind.get(self.sms_kind_id)

    @classmethod
    def create(cls, mobile, sms_kind, user_id=None, **sms_args):
        """为已注册用户发送短信"""
        assert isinstance(sms_kind, ShortMessageKind)

        if validate_phone(mobile) != errors.err_ok:
            raise ValueError(u'invalid mobile %s' % mobile)

        if sms_kind.need_verify:
            if not (user_id and Account.get(user_id)):
                raise ValueError(u'unable to verify user %s' % user_id)
            v = Verify.add(user_id, sms_kind.verify_type, sms_kind.verify_delta)
            sms_args.update(verify_code=v.code)

        sms = cls(uuid4().hex)
        # simply check formatting
        sms_kind.content.format(**sms_args)
        sms.update_props_items({
            u'receiver_mobile': mobile,
            u'sms_kind_id': sms_kind.id_,
            u'sms_args': sms_args
        })
        return sms

    @classmethod
    def get(cls, uuid):
        return cls(uuid) if uuid else None

    def send_async(self):
        """将短信发送加入队列进行异步发送"""
        if not self.is_sent:
            mq_sms_sender.produce(self.uuid.hex)

    def send(self, provider=None):
        """即时发送短信"""
        if self.is_sent:
            return True

        for k, v in self.sms_args.items():
            self.sms_args[k] = v.decode('utf-8')
        text = self.kind.content.format(**self.sms_args)

        # 如果不强制使用其他服务商，则经由短信类型偏好服务商发送
        channel = provider or self.kind.prefer_provider
        result = SMSClient.send(self.receiver_mobile, text, self.tag, channel)
        if result:
            rsyslog.send(u'\t'.join(
                [self.uuid.hex, self.receiver_mobile, str(self.sms_kind_id), text]),
                tag=u'sms_history')
            self.is_sent = True
        return result
