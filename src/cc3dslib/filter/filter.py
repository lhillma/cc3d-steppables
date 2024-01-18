from abc import ABC, abstractmethod
from typing import Iterable, Generic, TypeVar, Callable


from cc3d.core.XMLUtils import ElementCC3D

from cc3dslib.simulation.element import Element


T = TypeVar("T", covariant=True)
TO = TypeVar("TO", covariant=True)


class Filter(ABC, Element, Generic[T]):
    """A filter is a callable that returns an iterable.

    Filters can be used to select a subset of cells from a simulation.
    """

    @abstractmethod
    def __call__(self) -> Iterable[T]:
        """Return an iterable of cells."""

    def transform(
        self, transform: Callable[[Iterable[T]], Iterable[TO]]
    ) -> "Filter[TO]":
        return TransformFilter(self, transform)

    def apply(self, transform: Callable[[T], TO]) -> "Filter[TO]":
        return ApplyFilter(self, transform)

    def build(self) -> list[ElementCC3D]:
        return []


TI = TypeVar("TI", covariant=True)


class TransformFilter(Filter[TO], Generic[TO]):
    """A filter that transforms the iterable returned by another filter."""

    def __init__(
        self, filter: Filter[TI], transform: Callable[[Iterable[TI]], Iterable[TO]]
    ):
        self.filter = filter
        self._transform_fn = transform

    def __call__(self) -> Iterable[TO]:
        return self._transform_fn(self.filter())


class ApplyFilter(Filter[TO], Generic[TO]):
    """A filter that applies a transformation to each element returned by another filter."""

    def __init__(self, filter: Filter[TI], transform: Callable[[TI], TO]):
        self.filter = filter
        self._transform_fn = transform

    def __call__(self) -> Iterable[TO]:
        return map(self._transform_fn, self.filter())
