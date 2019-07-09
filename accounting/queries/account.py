
from dataclasses import dataclass
from decimal import Decimal
from enum import auto, Enum
from typing import List
from uuid import UUID

from ..entities.account import AccountCreated, AccountCredited, AccountDebited


class TransactionType(Enum):
    DEBIT = auto()
    CREDIT = auto()


@dataclass
class Transaction:
    amount: Decimal
    reference: str
    type: TransactionType


class Account:
    def __init__(self, id: UUID):
        self.id = id
        self.transactions: List[Transaction] = []
        self.balance = Decimal('0')

    def credit(self, reference: str, amount: Decimal):
        self.transactions.append(Transaction(reference=reference,
                                             amount=amount,
                                             type=TransactionType.CREDIT))
        self.balance += amount

    def debit(self, reference: str, amount: Decimal):
        self.transactions.append(Transaction(reference=reference,
                                             amount=amount,
                                             type=TransactionType.DEBIT))
        self.balance -= amount

    def __repr__(self) -> str:
        properties = ['='.join((k, repr(v))) for k, v in self.__dict__.items()]
        properties.sort()
        return '{}({})'.format(self.__class__.__name__, ', '.join(properties))


class AccountReadModel:
    class DoesNotExist(Exception):
        pass

    def __init__(self):
        self.accounts = {}

    def get(self, account_id: UUID):
        try:
            return self.accounts[account_id]
        except KeyError:
            raise AccountReadModel.DoesNotExist

    def handle_event(self, event):
        if isinstance(event, AccountCreated):
            self.accounts[event.account_id] = Account(id=event.account_id)
        elif isinstance(event, AccountCredited):
            self.accounts[event.account_id].credit(reference=event.reference,
                                                   amount=event.amount)
        elif isinstance(event, AccountDebited):
            self.accounts[event.account_id].debit(reference=event.reference,
                                                  amount=event.amount)
