
from abc import abstractmethod, abstractproperty
from typing import Generic, Iterable, TypeVar
from uuid import UUID

A = TypeVar('A')


class Event(Generic[A]):
    @abstractproperty
    def aggregate_id(self) -> UUID:
        pass

    @abstractmethod
    def apply(aggregate: A) -> A:
        pass

    def __repr__(self) -> str:
        properties = ['='.join((k, repr(v))) for k, v in self.__dict__.items()]
        properties.sort()
        return '{}({})'.format(self.__class__.__name__, ', '.join(properties))


class Entity:
    def __repr__(self) -> str:
        properties = ['='.join((k, repr(v))) for k, v in self.__dict__.items()
                      if k != 'id']
        properties.sort()
        return '{}(id={}{}{})'.format(self.__class__.__name__, self.id,
                                      ', ' if properties else '',
                                      ', '.join(properties))


I = TypeVar('I')
E = TypeVar('E')


class Repository(Generic[I, E]):
    @abstractmethod
    def add(event: E) -> None:
        pass

    @abstractmethod
    def get(id: I) -> Iterable[E]:
        pass
