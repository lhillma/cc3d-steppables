from typing import Iterator
from cc3d.cpp.CompuCell import CellG
from cc3dslib import ActiveSwimmer, ActiveSwimmerParams
from cc3dslib.filter import (
    CompartmentFilter,
    RandomFractionFilter,
)
from cc3dslib.nucleus import NucleusCompartmentCell, NucleusCompartmentCellParams
from cc3dslib.simulation import ConfigBuilder, PottsParams


sim_params = PottsParams(dimensions=(100, 100, 1), steps=1_000_000)

# nucleus
nuc_params = NucleusCompartmentCellParams(
    box=(0, 0, *sim_params.dimensions[:2]),
    nucleus_size_ratio=0.4,
    lambda_nuc=2.0,
    lambda_cell=3.0,
)
nuc_params.J[("Cytoplasm", "Cytoplasm")] = 2.0
nuc_params.J_internal[("Cytoplasm", "Nucleus")] = 2.0
nuc_steppable = NucleusCompartmentCell(params=nuc_params)
nuc_cells = NucleusCompartmentCell(params=nuc_params)

# active force

# Select all cells in the simulation and group them by cluster ID
cell_filter = CompartmentFilter()


def unravel(data) -> Iterator[list[CellG]]:
    """
    Turn [[x, y, z], [a, b, c]] into [[x], [y], [z], [a], [b], [c]].

    This function is required to separate the cells in each compartment into
    individual cells to be processed by the active swimmer steppable."""
    for x in data:
        for y in x:
            yield [y]


active_params = ActiveSwimmerParams(
    filter=RandomFractionFilter(cell_filter, 0.25).transform(unravel),
    cell_size=nuc_params.cell_size,
    d_theta=0.1,
    force_magnitude=10.0,
)

(
    ConfigBuilder()
    .base()
    .potts(sim_params)
    .add(nuc_cells)
    .add(cell_filter)
    .add(ActiveSwimmer(params=active_params))
    .setup()
    .run()
)
