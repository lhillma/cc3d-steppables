from typing import Iterator
from cc3d.core.PySteppables import SteppableBasePy

from cc3dslib.active_swimmer import CellG
from .filter import Filter


class CompartmentFilter(SteppableBasePy, Filter[list[CellG]]):
    """A filter iterating over the cells in a cluster/ compartment.

    This filter is used to select all cells in the simulation and group them by
    cluster ID. This is for example useful in conjunction with the `NucleusCompartment`
    """

    def __init__(self):
        super().__init__(frequency=float("inf"))

    def __call__(self) -> Iterator[list[CellG]]:
        assert self.clusters is not None
        for compartment in self.clusters:
            yield list(compartment)
