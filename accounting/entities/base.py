
from abc import abstractmethod, abstractproperty
from copy import deepcopy
from dataclasses import dataclass
from typing import Generic, Iterable, List, TypeVar
from uuid import UUID


@dataclass
class Entity:
    id: UUID
    version: int

    def __repr__(self) -> str:
        properties = ['='.join((k, repr(v))) for k, v in self.__dict__.items()
                      if k != 'id']
        properties.sort()
        return '{}(id={}{}{})'.format(self.__class__.__name__, self.id,
                                      ', ' if properties else '',
                                      ', '.join(properties))


A = TypeVar('A', bound=Entity)


# Mypy does not like generic types which are bound by abstract classes like
# data classes.
@dataclass
class Event(Generic[A]):  # type: ignore
    class VersionConflict(Exception):
        pass

    expected_version: int

    @abstractproperty
    def aggregate_id(self) -> UUID:
        pass

    def apply(self, aggregate: A) -> A:
        if self.expected_version != aggregate.version + 1:
            raise Event.VersionConflict

        new_aggregate = deepcopy(aggregate)
        self.apply_changes(new_aggregate)
        new_aggregate.version += 1
        return new_aggregate

    @abstractmethod
    def apply_changes(self, aggregate: A):
        pass

    def __repr__(self) -> str:
        properties = ['='.join((k, repr(v))) for k, v in self.__dict__.items()]
        properties.sort()
        return '{}({})'.format(self.__class__.__name__, ', '.join(properties))


class Factory:
    @classmethod
    @abstractmethod
    def nil(cls):
        pass

    @classmethod
    def replay(cls, events: List[Event[A]]) -> A:
        aggregate = cls.nil()

        for event in events:
            aggregate = event.apply(aggregate)

        return aggregate

    @classmethod
    def apply(cls, aggregate: A, events: List[Event[A]]) -> A:
        for event in events:
            aggregate = event.apply(aggregate)

        return aggregate


I = TypeVar('I')
E = TypeVar('E')


class Repository(Generic[I, E]):
    @abstractmethod
    def add(event: E) -> None:
        pass

    @abstractmethod
    def get(id: I) -> Iterable[E]:
        pass
