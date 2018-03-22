from warnings import warn
from itertools import chain
from collections import namedtuple, OrderedDict

from more_itertools import first

from .errors import UnknownBankError, UnavailableBankError, UnsupportedBankError


class BankMixin(object):
    """The extra methods of bank tuple."""

    icon_url_prefix = 'https://dn-guihua-static.qbox.me/img/logo/banks'

    @property
    def amount_limit(self):
        warn(DeprecationWarning('Please use yxlib_amount_limit instead.'))
        return self.yxlib_amount_limit

    @property
    def icon_url(self):
        return {
            'mdpi': '%s/%s.png' % (self.icon_url_prefix, self.id_),
            'hdpi': '%s/%s@2x.png' % (self.icon_url_prefix, self.id_),
        }

    def raise_for_unavailable(self, partner=None):
        if not self.available_in:
            raise UnsupportedBankError
        if partner and partner not in self.available_in:
            raise UnavailableBankError


class BankCollection(object):
    """The collection of banks."""

    def __init__(self, suites):
        self._banks = OrderedDict()
        self._name_to_bank = {}
        self.suites = suites
        fields = [
            'id_',
            'name',
            'telephone',
            'aliases',
            'available_in',
        ] + [field for fields in suites.values() for field in fields]
        self.banktuple = namedtuple('Bank', fields)
        self.banktuple.__bases__ += (BankMixin,)

    @property
    def banks(self):
        """The read-only list of banks."""
        return [bank for bank in self._banks.values() if bank.available_in]

    def add_bank(self, **kwargs):
        """Adds new supported bank.

        :param id_: The bank identity.
        :param name: The display name of bank.
        :param telephone: The official telephone of bank.
        :param aliases: The list of alias.
        :param available_in: The list of available partner.
        :param kwargs: The extra arguments which are defined by partner
                       (``suites``).
        """
        available_in = kwargs.setdefault('available_in', set())

        for partner, fields in self.suites.items():
            if any(field in kwargs for field in fields):
                if not all(field in kwargs for field in fields):
                    raise ValueError('%r are required for %r' % (fields, partner))
                available_in.add(partner)
            else:
                for field in fields:
                    kwargs.setdefault(field, None)

        # freeze nested lists
        kwargs['available_in'] = frozenset(kwargs['available_in'])
        kwargs['aliases'] = frozenset(kwargs['aliases'])

        bank = self.banktuple(**kwargs)
        self._banks[str(bank.id_)] = bank
        for name in chain([bank.name], bank.aliases):
            self._name_to_bank[name] = bank

    def get_bank(self, id_, partner=None):
        """Gets bank by its identity.

        :param id_: The bank identity.
        :param partner: The option partner.
        :return: The bank tuple or ``None``.
        :raises UnsupportedBankError: if the name points to an unsupported bank.
        :raises UnavailableBankError: if the name points to a bank which is
                                      unavailable with this partner.
        """
        bank = self._banks.get(str(id_))
        if bank is not None:
            bank.raise_for_unavailable(partner)
            return bank

    def get_bank_by_name(self, name, partner=None):
        """Gets bank tuple by its name or alias.

        :param name: The name or alias of bank.
        :param partner: The option partner.
        :return: The bank tuple.
        :raises UnsupportedBankError: if the name points to an unsupported bank.
        :raises UnavailableBankError: if the name points to a bank which is
                                      unavailable with this partner.
        :raises UnknownBankError: if the name is unknown.
        """
        if name is None:
            raise UnsupportedBankError
        bank = first(self._iter_by_name(name), default=None)
        if bank is None:
            raise UnknownBankError(name)
        bank.raise_for_unavailable(partner)
        return bank

    def _iter_by_name(self, name):
        """Iterates possible bank tuples by a specific name."""
        # finds by name
        if name in self._name_to_bank:
            yield self._name_to_bank[name]

        # finds by alias
        for item_name, item_bank in self._name_to_bank.iteritems():
            if name.startswith(item_name):
                yield item_bank
