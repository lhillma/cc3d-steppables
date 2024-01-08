from typing import Iterable, TypeVar, Generic

import numpy as np

from .filter import Filter


T = TypeVar("T", covariant=True)


class RandomFractionFilter(Filter[T], Generic[T]):
    """Randomly select a given fraction of the elements a filter returns"""

    def __init__(self, filter: Filter[T], fraction: float):
        self.filter = filter
        self.fraction = fraction
        self.indices: np.ndarray | None = None

    def __call__(self) -> Iterable[T]:
        data = np.array(list(self.filter()))
        if self.indices is None:
            self._assign_indices(data)

        return data[self.indices]

    def _assign_indices(self, data: np.ndarray) -> None:
        size = len(data)
        self.indices = np.random.choice(size, int(size * self.fraction), replace=False)
