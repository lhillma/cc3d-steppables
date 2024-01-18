from cc3d.cpp.CompuCell import CellG
from .filter import Filter


class CellFilter(Filter[CellG]):
    def __init__(self):
        super().__init__(frequency=float("inf"))

    def __call__(self) -> list[CellG]:
        assert self.cell_list is not None
        return list(self.cell_list)
