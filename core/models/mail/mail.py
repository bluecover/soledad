# coding:utf-8

from datetime import datetime

from werkzeug.utils import cached_property
from flask import current_app
from flask_mako import render_template

from jupiter.workers.email import email_sender
from libs.db.store import db
from core.models import errors
from core.models.mixin.props import PropsMixin, PropsItem
from core.models.utils.validator import validate_email
from .kind import MailKind


class Mail(PropsMixin):
    table_name = 'email'

    def __init__(self, id_, sender, receiver, kind_id, creation_time):
        self.id_ = str(id_)
        self.sender = sender
        self.receiver = receiver
        self.kind_id = kind_id
        self.creation_time = creation_time

    mail_args = PropsItem('mail_args', '')
    sender_name = PropsItem('sender_name', '')

    def __repr__(self):
        return '<Mail id=%s>' % (self.id_)

    def get_uuid(self):
        return 'email:%s' % (self.id_)

    def get_db(self):
        return 'email'

    @cached_property
    def kind(self):
        return MailKind.get(self.kind_id)

    @cached_property
    def mail_body(self):
        return render_template(self.kind.template, **self.mail_args)

    @classmethod
    def _create(cls, sender, receiver, mail_kind, sender_name, commit_=True, **mail_args):
        if validate_email(receiver) != errors.err_ok:
            raise ValueError('email format is not valid!')

        sql = ('insert into {.table_name}'
               ' (sender, receiver, kind_id, creation_time)'
               ' values (%s, %s, %s, %s)').format(cls)
        params = (sender, receiver, mail_kind.id_, datetime.now())

        id_ = db.execute(sql, params)
        if commit_:
            db.commit()

        instance = cls.get(id_)
        instance.update_props_items({
            'mail_args': mail_args,
            'sender_name': sender_name,
        })
        return instance

    @classmethod
    def create(cls, receivers, mail_kind, sender='', sender_name='',
               callback=None, **mail_args):
        assert isinstance(mail_kind, MailKind)

        if isinstance(receivers, basestring):
            return cls._create(sender, receivers, mail_kind, sender_name, **mail_args)
        elif isinstance(receivers, list):
            multi_mails = []
            try:
                for receiver in receivers:
                    multi_mails.append(cls._create(
                        sender, receiver, mail_kind, sender_name, commit_=False, **mail_args))
            except:
                db.rollback()
                raise
            else:
                db.commit()
            return multi_mails
        else:
            raise TypeError('receivers need to be string or list!')

    def send(self):
        if not (current_app and current_app.debug):
            email_sender.produce(self.id_)

    @classmethod
    def send_multi(cls, mails):
        for mail in mails:
            mail.send()

    @classmethod
    def get(cls, id_):
        sql = ('select id, sender, receiver, kind_id, creation_time'
               ' from {.table_name} where id=%s').format(cls)
        params = (id_,)
        rs = db.execute(sql, params)
        if rs:
            return cls(*rs[0])

    @classmethod
    def gets(cls, ids):
        return [cls.get(id) for id in ids]

    def delete(self):
        sql = 'delete from {.table_name} where id=%s'.format(self)
        params = (self.id_,)
        db.execute(sql, params)
        db.commit()
        self.clean_props_item()
