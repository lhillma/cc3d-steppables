from typing import Iterable
from cc3d.core.PySteppables import SteppableBasePy
from cc3d.cpp.CompuCell import CellG
from .filter import Filter


class CellTypeFilter(Filter):
    def __init__(self, *types):
        super().__init__(frequency=float("inf"))
        self.cell_types = types

    def __call__(self) -> Iterable[CellG]:
        """Return cells of the specified type(s).

        Wrapper around `cell_list_by_type`.
        """
        return self.cell_list_by_type(*self.cell_types)
