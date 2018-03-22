# coding: utf-8

from __future__ import print_function, absolute_import, unicode_literals

from wtforms.fields.core import SelectField, Field
from gb2260 import Division

from core.models.bank import Partner, bank_collection
from core.models.bank.errors import UnavailableBankError


class BankField(SelectField):
    def __init__(self, label=None, validators=None, partner=None, **kwargs):
        banks = bank_collection.banks

        if partner is not None:
            assert isinstance(partner, Partner)
            banks = [bank for bank in banks if partner in bank.available_in]

        kwargs.setdefault('coerce', self.coerce)
        kwargs.setdefault('choices', [(bank.id_, bank.name) for bank in banks])

        super(BankField, self).__init__(label, validators, **kwargs)
        self.partner = partner

    def coerce(self, value):
        if value in bank_collection.banks:
            return value
        return bank_collection.get_bank(value)

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = self.coerce(valuelist[0])
            if not self.data:
                raise ValueError(self.gettext('请选择正确的开户银行'))

    def pre_validate(self, form):
        if self.data:
            if self.partner is None:
                return
            try:
                self.data.raise_for_unavailable(self.partner)
            except UnavailableBankError as e:
                raise ValueError(self.gettext(unicode(e)))


class DivisionField(Field):
    YEAR_CHOICES = frozenset(['2012'])
    LEVEL_CHOICES = frozenset(['province', 'prefecture', 'county'])

    def __init__(self, label=None, validators=None, year=None, level=None,
                 **kwargs):
        super(DivisionField, self).__init__(label, validators, **kwargs)
        assert year in self.YEAR_CHOICES or year is None
        assert level in self.LEVEL_CHOICES or level is None
        self.year = year
        self.level = level

    def _value(self):
        if self.raw_data:
            return self.raw_data[0]
        elif self.data is not None:
            return self.data.code
        else:
            return ''

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = Division.search(valuelist[0])
            if not self.data:
                raise ValueError(self._error)

    def pre_validate(self, form):
        if self.data:
            if self.year and self.year != self.data.year:
                raise ValueError(self._error)
            if self.level == 'province' and not self.data.is_province:
                raise ValueError(self._error)
            if self.level == 'prefecture' and not self.data.is_prefecture:
                raise ValueError(self._error)
            if self.level == 'county' and not self.data.is_county:
                raise ValueError(self._error)

    @property
    def _error(self):
        return self.gettext('请选择正确的%s') % self.label
