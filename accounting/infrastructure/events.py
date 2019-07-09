
from typing import Callable, List
from uuid import UUID

from ..entities import Event


class InMemoryEventStore:
    def __init__(self):
        self.history = {}
        self.topic_handlers = {}

    def add(self, topic: str, event: Event):
        topic_history = self.history.setdefault(topic, {})
        aggregate_history = topic_history.setdefault(event.aggregate_id, [])
        aggregate_history.append(event)

        try:
            for handler in self.topic_handlers[topic]:
                handler(event)
        except KeyError:
            pass

    def get(self, topic: str, aggregate_id: UUID) -> List[Event]:
        return self.history.get(topic, {}).get(aggregate_id, [])

    def exists(self, topic: str, aggregate_id: UUID) -> bool:
        return aggregate_id in self.history.get(topic, {})

    def register(self, topic: str, handler: Callable[[Event], None]):
        self.topic_handlers.setdefault(topic, []).append(handler)
