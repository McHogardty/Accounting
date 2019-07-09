
from copy import deepcopy
from dataclasses import dataclass
from decimal import Decimal
from enum import auto, Enum
from typing import List
from uuid import UUID

from .base import Entity, Event


class Account(Entity):
    @classmethod
    def nil(cls) -> 'Account':
        return cls()

    def __init__(self):
        self.id: UUID = None
        self.balance: Decimal = Decimal('0')
        self.version = 0

    def credit(self,
               reference: str,
               amount: Decimal) -> List[Event['Account']]:
        return [AccountCredited(account_id=self.id,
                                reference=reference,
                                amount=amount,
                                expected_version=self.version + 1)]

    def debit(self,
              reference: str,
              amount: Decimal) -> List[Event['Account']]:
        return [AccountDebited(account_id=self.id,
                               reference=reference,
                               amount=amount,
                               expected_version=self.version + 1)]


class AccountFactory:
    @classmethod
    def replay(cls, events: List[Event[Account]]) -> Account:
        account = Account.nil()

        for event in events:
            account = event.apply(account)

        return account

    @classmethod
    def apply(cls, account: Account, events: List[Event[Account]]) -> Account:
        for event in events:
            account = event.apply(account)

        return account


@dataclass
class AccountCreated(Event[Account]):
    account_id: UUID

    @property
    def aggregate_id(self):
        return self.account_id

    def apply_changes(self, account: Account):
        account.id = self.aggregate_id


@dataclass
class AccountCredited(Event[Account]):
    account_id: UUID
    reference: str
    amount: Decimal

    @property
    def aggregate_id(self):
        return self.account_id

    def apply_changes(self, account: Account):
        account.balance += self.amount


@dataclass
class AccountDebited(Event[Account]):
    account_id: UUID
    reference: str
    amount: Decimal

    @property
    def aggregate_id(self):
        return self.account_id

    def apply_changes(self, account: Account):
        account.balance -= self.amount


class AccountRepository:
    class DoesNotExist(Exception):
        pass

    def add(self, events: List[Event[Account]]) -> None:
        pass

    def exists(self, account_id: UUID) -> bool:
        pass

    def get(self, account_id: UUID) -> List[Event[Account]]:
        pass


class AccountService:
    class AccountAlreadyExists(Exception):
        pass

    class AccountNotFound(Exception):
        pass

    def __init__(self, repository: AccountRepository):
        self.repository = repository

    def create(self, account_id: UUID):
        if self.repository.exists(account_id=account_id):
            raise AccountService.AccountAlreadyExists

        self.repository.add(events=[AccountCreated(account_id=account_id,
                                                   expected_version=1)])

    def credit(self,
               account_id: UUID,
               reference: str,
               amount: Decimal):
        try:
            history = self.repository.get(account_id=account_id)
        except AccountRepository.DoesNotExist:
            raise AccountService.AccountNotFound

        account = AccountFactory.replay(events=history)
        events = account.credit(reference=reference, amount=amount)

        self.repository.add(events)

    def debit(self,
              account_id: UUID,
              reference: str,
              amount: Decimal):
        try:
            history = self.repository.get(account_id=account_id)
        except AccountRepository.DoesNotExist:
            raise AccountService.AccountNotFound

        account = AccountFactory.replay(events=history)
        events = account.debit(reference=reference, amount=amount)

        self.repository.add(events)

    def transfer(self,
                 source_account_id: UUID,
                 destination_account_id: UUID,
                 reference: str,
                 amount: Decimal):
        try:
            source_account_history = self.repository.get(
                account_id=source_account_id,
            )
        except AccountRepository.DoesNotExist:
            raise AccountService.AccountNotFound

        try:
            destination_account_history = self.repository.get(
                account_id=destination_account_id,
            )
        except AccountRepository.DoesNotExist:
            raise AccountService.AccountNotFound

        source_account = AccountFactory.replay(source_account_history)
        destination_account = \
            AccountFactory.replay(destination_account_history)

        events = source_account.debit(reference=reference, amount=amount)
        events += destination_account.credit(
            reference=reference,
            amount=amount,
        )

        self.repository.add(events)
