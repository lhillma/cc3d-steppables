from dataclasses import dataclass

import numpy as np

from cc3d.core.PySteppables import SteppableBasePy
from cc3d.cpp import CompuCell


@dataclass
class NucleusCompartmentCellParams:
    """Parameters for NucleusCompartmentCell."""

    box: tuple[int, int, int, int]
    cell_size: int = 20
    nucleus_size_ratio: float = 0.2
    lambda_cell: float = 0.1
    lambda_nuc: float = 1.0


class NucleusCompartmentCell(SteppableBasePy):
    """Steppable to set up compartmentalized cells with a nucleus and cytoplasm.

    Usage of this steppable requires the simulation to have two cell types
    defined, one for the nucleus and one for the cytoplasm. The cell types
    should be defined in the simulation's .xml file as follows:

    <Plugin Name="CellType">
        <CellType TypeId="0" TypeName="nucleus"/>
        <CellType TypeId="1" TypeName="cytoplasm"/>
    </Plugin>
    """

    # missing type hints
    NUCLEUS: int
    CYTOPLASM: int
    cell_field: CompuCell.cellfield

    def __init__(
        self,
        params: NucleusCompartmentCellParams,
    ):
        """Initialize steppable."""
        # Since this steppable is only an initializer, it should only run once, thus
        # it is set to run at a frequency of infinity.
        super().__init__(frequency=float("inf"))

        self.params = params

    def start(self):
        """Create a cell with a nucleus and cytoplasm."""
        self._assign_cells_to_grid()
        self._assign_cell_custer_ids()
        self._assign_volume_terms()

    def _assign_cells_to_grid(self):
        """Create new cells in a regular grid with the nucleus in the centre."""
        start_x, start_y, end_x, end_y = self.params.box

        cell_size = self.params.cell_size
        nuc_size = int(cell_size * self.params.nucleus_size_ratio)
        nuc_start = int((cell_size - nuc_size) / 2)
        nuc_end = nuc_start + nuc_size

        for x in np.arange(start_x, end_x, cell_size).astype(np.float64):
            for y in np.arange(start_y, end_y, cell_size).astype(np.float64):
                self.cell_field[
                    x : x + cell_size, y : y + self.params.cell_size, 0
                ] = self.new_cell(self.CYTOPLASM)

                self.cell_field[
                    x + nuc_start : x + nuc_end, y + nuc_start : y + nuc_end, 0
                ] = self.new_cell(self.NUCLEUS)

    def _assign_cell_custer_ids(self):
        """Assign the same cluster ID to the nucleus and cytoplasm of each cell."""
        for cyto_cell, nuc_cell in zip(
            self.cell_list_by_type(self.CYTOPLASM), self.cell_list_by_type(self.NUCLEUS)
        ):
            cluster_id = cyto_cell.clusterId
            self.reassign_cluster_id(nuc_cell, cluster_id)

    def _assign_volume_terms(self):
        """Assign the volume terms for each cell according to the cell size."""
        cell_vol = self.params.cell_size**2
        nuc_vol = self.params.nucleus_size_ratio**2 * cell_vol
        cyto_vol = cell_vol - nuc_vol

        for cell in self.cell_list_by_type(self.NUCLEUS):
            cell.targetVolume = nuc_vol
            cell.lambdaVolume = self.params.lambda_nuc

        for cell in self.cell_list_by_type(self.CYTOPLASM):
            cell.targetVolume = cyto_vol
            cell.lambdaVolume = self.params.lambda_cell

    def step(self, _):
        pass

    def finish(self):
        pass
