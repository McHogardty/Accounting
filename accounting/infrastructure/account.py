
from uuid import UUID
from typing import List

from ..entities import Account, AccountRepository, Event


class InMemoryAccountRepository(AccountRepository):
    def __init__(self, store):
        self.store = store

    def add(self, events: List[Event[Account]]) -> None:
        for event in events:
            self.store.add('account', event)

    def get(self, account_id: UUID) -> List[Event[Account]]:
        events = self.store.get('account', account_id)

        if not events:
            raise AccountRepository.DoesNotExist("No events for account {}."
                                                 .format(account_id))

        return events

    def exists(self, account_id: UUID):
        return self.store.exists('topic', account_id)
