# coding: utf-8

import datetime
import urlparse

import requests
from flask import current_app

from jupiter.utils import ensure_app_context
from libs.db.store import db
from libs.cache import mc, cache
from libs.logger.rsyslog import rsyslog
from core.models.base import EntityModel
from core.models.mixin.props import PropsMixin, PropsItem
from core.models.utils import coerce_to_unicode
from core.models.utils.validator import validate_identity, validate_han
from core.models.errors import err_ok
from .signals import identity_saved

__all__ = ['Identity', 'has_real_identity', 'IdentityValidationError',
           'IdentityUsedError', 'RealIdentityRequiredError']


class Identity(EntityModel):
    """The real identity of a person."""

    table_name = 'profile_identity'
    cache_key = 'profile:identity:{user_id}'

    class Meta:
        repr_attr_names = ['person_name', 'person_ricn']

    def __init__(self, id_, person_name, person_ricn, updated_time):
        self.id_ = str(id_)
        #: the real name
        self.person_name = person_name
        #: the Resident Identity Card Number
        self.person_ricn = person_ricn
        self.updated_time = updated_time

    @property
    def masked_name(self):
        masked_length = len(self.person_name) - 1
        return (u'*' * masked_length) + self.person_name[-1]

    @classmethod
    def save(cls, user_id, person_name, person_ricn):
        if not cls._validate(person_name, person_ricn):
            raise IdentityValidationError(person_name, person_ricn)

        person_ricn = person_ricn.upper()
        if cls.get_by_ricn(person_ricn):
            raise IdentityUsedError

        if not is_matched_in_mathilde(person_name, person_ricn):
            raise IdentityDismatchError

        updated_time = datetime.datetime.now()
        sql = ('insert into {0} (id, person_name, person_ricn, updated_time) '
               'values (%s, %s, %s, %s) on duplicate key update'
               ' person_name = %s, person_ricn = %s,'
               ' updated_time = %s').format(cls.table_name)
        params = (user_id, person_name, person_ricn, updated_time,
                  person_name, person_ricn, updated_time)

        db.execute(sql, params)
        db.commit()

        cls.clear_cache(user_id)
        instance = cls.get(user_id)
        identity_saved.send(instance)
        return instance

    @classmethod
    @cache(cache_key)
    def get(cls, user_id):
        sql = ('select id, person_name, person_ricn, updated_time '
               'from {0} where id = %s').format(cls.table_name)
        params = (user_id,)
        rs = db.execute(sql, params)
        if rs:
            return cls(*rs[0])
        return cls._get_legacy(user_id)

    @classmethod
    def get_by_ricn(cls, ricn):
        sql = 'select id from {0} where person_ricn = %s'.format(cls.table_name)
        params = (ricn,)

        rs = db.execute(sql, params)
        if rs:
            return cls.get(rs[0][0])

    @classmethod
    def _get_legacy(cls, user_id):
        backward = BackwardProfile(user_id)
        if backward.person_name and backward.person_ricn:
            person_name = coerce_to_unicode(backward.person_name)
            person_ricn = coerce_to_unicode(backward.person_ricn)

            backward.person_name = person_name
            backward.person_ricn = person_ricn

            if cls.get_by_ricn(person_ricn):
                cls._remove_legacy(user_id)
            try:
                modern = cls.save(
                    user_id,
                    person_name.strip(),
                    person_ricn.strip())
            except IdentityBindingError as error:
                cls._remove_legacy(user_id, error)
            else:
                rsyslog.send(
                    '%s\t%s\t%s' % (
                        modern.id_, modern.person_name, modern.person_ricn),
                    tag='profile_identity_migration')
                return modern

    @classmethod
    def _remove_legacy(cls, user_id, error=None):
        backward = BackwardProfile(user_id)
        rsyslog.send(
            '%s\t%s\t%s\t%r' % (
                backward.account_id,
                backward.person_name,
                backward.person_ricn,
                error),
            tag='profile_identity_used_error')
        backward.remove()

    @classmethod
    def _validate(cls, person_name, person_ricn):
        results = [
            validate_han(person_name, 2, 20),
            validate_identity(person_ricn),
        ]
        return all(r == err_ok for r in results)

    @classmethod
    def remove(cls, user_id):
        identity = cls.get(user_id)
        if not identity:
            return
        cls._remove_legacy(user_id)
        params = (user_id,)
        sql = 'delete from {0.table_name} where id = %s'.format(cls)
        db.execute(sql, params)
        db.commit()
        rsyslog.send(
            '%s\t%s\t%s' % (
                identity.id_,
                identity.person_name,
                identity.person_ricn),
            tag='profile_identity_used_remove')
        cls.clear_cache(user_id)

    @classmethod
    def clear_cache(cls, user_id):
        mc.delete(cls.cache_key.format(**locals()))


class BackwardProfile(PropsMixin):
    """Do not use this outside."""

    person_name = PropsItem('person_name', default='', secret=True)
    person_ricn = PropsItem('person_ricn', default='', secret=True)

    def get_uuid(self):
        return 'user:profile:{account_id}'.format(account_id=self.account_id)

    def get_db(self):
        return 'hoard'

    def __init__(self, account_id):
        self.account_id = account_id

    def remove(self):
        self.update_props_items({
            'person_name': '',
            'person_ricn': '',
        })


def has_real_identity(user):
    """Checks an user's real identity and mobile phone.

    :param user: The user instance.
    :type user: :class:`~core.models.user.account.Account`
    :return: True if the mobile phone and real identity are available both.
    """
    return bool(user.mobile and Identity.get(user.id_))


@ensure_app_context
def is_matched_in_mathilde(person_name, person_ricn):
    """Checks whether the real name is matched with RIC number.

    It is provided by a third-party paid service. Please use it carefully.
    """
    if current_app.debug and 'MATHILDE_DSN' not in current_app.config:
        return True

    url = urlparse.urljoin(current_app.config['MATHILDE_DSN'], 'v1/validation')
    data = {'name': person_name, 'ricn': person_ricn}

    response = requests.put(url, data=data)
    response.raise_for_status()

    rsyslog.send(
        '{0}\t{1.status_code}\t{1.text}'.format(data, response),
        tag='profile_identity_mathilde')

    return response.json()['data']


class IdentityException(Exception):
    pass


class IdentityBindingError(IdentityException):
    def __unicode__(self):
        raise NotImplementedError


class IdentityValidationError(IdentityBindingError):
    def __unicode__(self):
        return u'姓名或身份证输入有误，请检查后重新填写'


class IdentityUsedError(IdentityBindingError):
    def __unicode__(self):
        return u'该身份证已绑定其他账号，请登录对应账号继续使用'


class IdentityDismatchError(IdentityBindingError):
    def __unicode__(self):
        return u'姓名与身份证号不匹配，请仔细检查身份信息后重试'


class RealIdentityRequiredError(Exception):
    pass
