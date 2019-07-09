
from decimal import Decimal
from uuid import uuid4

from accounting.entities import (
    AccountFactory,
    AccountService,
)
from accounting.infrastructure import (
    InMemoryAccountRepository,
    InMemoryEventStore,
)
from accounting.queries import AccountReadModel

read_model = AccountReadModel()
event_store = InMemoryEventStore()
event_store.register('account', read_model.handle_event)
repository = InMemoryAccountRepository(store=event_store)
account_service = AccountService(repository=repository)


account_id = uuid4()
recipient_account_id = uuid4()
account_service.create(account_id)
account_service.create(recipient_account_id)
account_service.credit(account_id=account_id,
                       reference=str(uuid4()),
                       amount=Decimal('10'))
account_service.transfer(source_account_id=account_id,
                         destination_account_id=recipient_account_id,
                         reference=str(uuid4()),
                         amount=Decimal('3'))

account = AccountFactory.replay(repository.get(account_id))
recipient = AccountFactory.replay(repository.get(recipient_account_id))
print(account)
print(recipient)
print(read_model.get(account_id))
print(read_model.get(recipient_account_id))
