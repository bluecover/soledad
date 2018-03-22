# coding:utf-8

import uuid

from werkzeug.security import gen_salt

from libs.cache import cache
from libs.db.store import db
from libs.logger.rsyslog import rsyslog
from core.models import errors
from core.models.user.consts import ACCOUNT_REG_TYPE
from core.models.user.errors import RemovingMobileAliasPreventedError
from core.models.utils.validator import validate_phone, validate_email


class AliasMixin(object):

    table_name = 'account_alias'
    alias_cache_key = 'user_account_alias:v1:data:%s'
    alias_cache_by_type_key = 'user_account_alias:v1:type:%s:%s'

    @property
    def reg_type(self):
        return self.get_type_alias().keys()

    @property
    def reg_alias(self):
        return self.get_type_alias().values()

    @property
    def email(self):
        return self.get_type_alias().get(ACCOUNT_REG_TYPE.EMAIL)

    @property
    def mobile(self):
        return self.get_type_alias().get(ACCOUNT_REG_TYPE.MOBILE)

    @property
    def display_mobile(self):
        if self.mobile:
            return '{0}****{1}'.format(self.mobile[:3], self.mobile[-4:])

    @property
    def screen_ident(self):
        return self.display_mobile or self.email or ''

    @property
    def weixin_openid(self):
        return self.get_type_alias().get(ACCOUNT_REG_TYPE.WEIXIN_OPENID)

    @property
    def firewood_id(self):
        return self.get_type_alias().get(ACCOUNT_REG_TYPE.FIREWOOD_ID)

    @cache(alias_cache_key % '{self.id_}')
    def get_type_alias(self):
        sql = 'select reg_type, alias from {.table_name} where id=%s'.format(self)
        rs = db.execute(sql, (self.id_,))
        return {str(reg_type): alias for reg_type, alias in rs}

    def has_email(self):
        return ACCOUNT_REG_TYPE.EMAIL in self.get_type_alias()

    def has_mobile(self):
        return ACCOUNT_REG_TYPE.MOBILE in self.get_type_alias()

    def has_weixin_openid(self):
        return ACCOUNT_REG_TYPE.WEIXIN_OPENID in self.get_type_alias()

    def has_firewood_id(self):
        return ACCOUNT_REG_TYPE.FIREWOOD_ID in self.get_type_alias()

    @classmethod
    def get_by_alias(cls, alias):
        reg_type = get_reg_type_from_alias(alias)
        return cls.get_by_alias_type(alias, reg_type)

    @classmethod
    @cache(alias_cache_by_type_key % ('{alias}', '{type_}'))
    def get_by_alias_type(cls, alias, type_):
        sql = 'select id from {.table_name} where alias=%s and reg_type=%s'.format(cls)
        params = (alias, type_)
        rs = db.execute(sql, params)
        if rs:
            return cls.get(rs[0][0]) if rs else None

    def add_alias(self, alias, alias_type=None):
        assert alias is not None

        parsed_type = get_reg_type_from_alias(alias)
        if alias_type is None:
            if parsed_type is None:
                raise InvalidAliasType(alias, alias_type)
        else:
            # 单独判断firewoodid/weixinopenid是否合法
            if alias_type == ACCOUNT_REG_TYPE.FIREWOOD_ID:
                alias = uuid.UUID(alias).hex
            elif parsed_type is not None and alias_type != parsed_type:
                raise InvalidAliasType(alias, alias_type)

        alias_type = alias_type or parsed_type

        # verify there's no alias conflict in self
        existed_alias = self.get_type_alias().get(alias_type)
        if existed_alias and existed_alias != alias:
            raise AliasTypeUsedError(alias_type)

        # verify there's no alias conflict in global
        existence = self.get_by_alias_type(alias, alias_type)
        if existence and existence.id_ != self.id_:
            raise AliasOccupiedError(alias)

        self._add_alias(alias, alias_type)
        return True

    def _add_alias(self, alias, type_):
        """Adds alias to this account."""
        sql = ('insert into {.table_name} (`id`, alias, reg_type) values(%s, %s, %s) '
               'on duplicate key update id=id').format(self)
        params = (self.id_, alias, type_)
        db.execute(sql, params)
        db.commit()
        self.clear_cache()

    def update_alias(self, type_, new_alias):
        if type_ not in self.reg_type:
            return False

        if new_alias in self.reg_alias:
            return False

        user = self.get_by_alias(new_alias)
        if user:
            return False

        if (
            type_ in (ACCOUNT_REG_TYPE.EMAIL, ACCOUNT_REG_TYPE.MOBILE) and
            type_ != get_reg_type_from_alias(new_alias)
        ):
            return False

        self._update_alias(type_, new_alias)
        return True

    def _update_alias(self, type_, new_alias):
        sql = 'update {.table_name} set alias=%s where `id`=%s and reg_type=%s'.format(self)
        params = (new_alias, self.id_, type_)
        db.execute(sql, params)
        db.commit()

        self.clear_cache()

    def remove_alias(self, type_, alias=None):
        if type_ not in self.reg_type:
            return False

        if alias:
            if alias not in self.reg_alias:
                return False
            if (
                type_ in (ACCOUNT_REG_TYPE.EMAIL, ACCOUNT_REG_TYPE.MOBILE) and
                type_ != get_reg_type_from_alias(alias)
            ):
                return False

        if not self.is_failed_account():
            if len(self.reg_alias) < 2:
                return False
            if type_ == ACCOUNT_REG_TYPE.EMAIL and \
                    ACCOUNT_REG_TYPE.MOBILE not in self.reg_type:
                return False
            if type_ == ACCOUNT_REG_TYPE.MOBILE and \
                    ACCOUNT_REG_TYPE.EMAIL not in self.reg_type:
                return False

        self._remove_alias(type_, alias)
        return True

    def _remove_alias(self, type_, alias=None):
        """Removes alias from this account.

        :param type_: the type of removing records.
        :param alias: the value of removing record. ``None`` means remove all
                      records of this account with specified type.
        """
        sql = 'delete from {.table_name} where `id`=%s and reg_type=%s'.format(self)
        params = (self.id_, type_)

        if alias is not None:
            sql += ' and alias=%s'
            params += (alias,)

        db.execute(sql, params)
        db.commit()
        self.clear_cache()

    def unbind_mobile(self):
        # 更新手机alias为邮箱
        if not self.mobile:
            return False

        mobile = self.mobile
        new_alias = '%s@%s.com' % (mobile, gen_salt(8))
        # 用户不存在邮箱
        if not self.has_email():
            self.add_alias(new_alias, ACCOUNT_REG_TYPE.EMAIL)

        is_removed = self.remove_alias(ACCOUNT_REG_TYPE.MOBILE)
        if not is_removed:
            raise RemovingMobileAliasPreventedError()
        rsyslog.send(
            '%s alias %s changed %s\t' % (self.id_, mobile, new_alias),
            tag='account_unbind_mobile')
        return True


def get_reg_type_from_alias(alias):
    # only support mobile/email parse
    if validate_phone(alias) == errors.err_ok:
        return ACCOUNT_REG_TYPE.MOBILE
    elif validate_email(alias) == errors.err_ok:
        return ACCOUNT_REG_TYPE.EMAIL


class AliasException(Exception):
    pass


class AliasTypeUsedError(AliasException):
    pass


class AliasOccupiedError(AliasException):
    pass


class InvalidAliasType(AliasException):
    pass
