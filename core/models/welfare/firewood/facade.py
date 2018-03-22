# coding: utf-8

import uuid


from jupiter.integration.firewood import (
    firewood, FirewoodException as RemoteFirewoodException)
from core.models.user.account import Account
from core.models.user.consts import ACCOUNT_REG_TYPE
from core.models.profile.identity import Identity, has_real_identity
from core.models.welfare.firewood.consts import FIREWOOD_BURNING_RATIO
from core.models.welfare.firewood.errors import (
    AccountUncreatedError, BalanceUnenjoyableError,
    ProductUnsupportedError, InsufficientBalanceError,
    ServiceValidationError, DealingError)
from .burn import FirewoodBurning


class FirewoodWorkflow(object):
    """The base workflow of firewood service"""

    def __init__(self, user_id):
        self.user = Account.get(user_id)
        self.identity = Identity.get(user_id)

        if not self.user:
            raise ValueError('user %r not found' % user_id)
        if has_real_identity(self.user) and not self.user.firewood_id:
            self.identity = Identity.get(user_id)
            resp = firewood.create_account(self.identity.person_name, self.identity.person_ricn)
            self.user.add_alias(resp.json()['uid'], ACCOUNT_REG_TYPE.FIREWOOD_ID)

    @property
    def account_uid(self):
        return uuid.UUID(self.user.firewood_id) if self.user.firewood_id else None

    @property
    def balance(self):
        if not self.account_uid:
            return 0
        return firewood.list_transactions(self.account_uid).json()['balance']

    def check_deduction_enjoyable(self, product, order_amount, pocket_deduction_amount):
        if not product.is_accepting_bonus:
            raise ProductUnsupportedError()

        if (pocket_deduction_amount > order_amount / FIREWOOD_BURNING_RATIO) or (
                pocket_deduction_amount > self.balance):
            raise BalanceUnenjoyableError()

    def _check_before_piling_transaction(self, user):
        assert user.id_ == self.user.id_

        if not self.account_uid:
            raise AccountUncreatedError()

    def _check_before_burning_transaction(self, local_burning, starting_status):
        assert isinstance(local_burning, FirewoodBurning)
        assert local_burning.user_id == self.user.id_

        if not self.account_uid:
            raise AccountUncreatedError()

        if local_burning.status not in (starting_status,
                                        FirewoodBurning.Status.ready,
                                        FirewoodBurning.Status.canceled):
            raise DealingError()

    def pile(self, user, amount, welfare_package, tags):
        """用户充值红包"""
        from .pile import FirewoodPiling

        self._check_before_piling_transaction(user)

        # 创建并确认抵扣金交易
        resp = firewood.create_transaction(self.account_uid, +amount, tags)
        transaction_id = uuid.UUID(resp.json()['uid'])
        firewood.confirm_transaction(self.account_uid, transaction_id)

        # 本地记录
        return FirewoodPiling.add(self.user, amount, welfare_package, transaction_id.hex)

    def pick(self, local_burning, tags):
        """用户选择红包抵扣金额(冻结)"""
        self._check_before_burning_transaction(local_burning, FirewoodBurning.Status.ready)

        try:
            resp = firewood.create_transaction(self.account_uid, -local_burning.amount, tags)
        except RemoteFirewoodException as e:
            # 抵扣金服务异常处理
            if e.errors[0].kind == 'insufficient_balance':
                raise InsufficientBalanceError()
            elif e.errors[0].kind == 'validation_error':
                raise ServiceValidationError()
            else:
                raise
        else:
            transaction_id = uuid.UUID(resp.json()['uid'])
            local_burning.lay_up(transaction_id.hex)

    def burn(self, local_burning):
        """用户使用红包抵扣金额(使用)"""
        self._check_before_burning_transaction(local_burning, FirewoodBurning.Status.placed)

        firewood.confirm_transaction(self.account_uid, local_burning.remote_transaction_id)
        local_burning.burn_out()

    def release(self, local_burning):
        """红包抵扣金额放回(解冻)"""
        self._check_before_burning_transaction(local_burning, FirewoodBurning.Status.placed)

        firewood.cancel_transaction(self.account_uid, local_burning.remote_transaction_id)
        local_burning.take_back()
