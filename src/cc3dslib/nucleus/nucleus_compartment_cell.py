from typing import Literal
from dataclasses import dataclass, field

import numpy as np

from cc3d.core.PySteppables import SteppableBasePy
from cc3d.core.XMLUtils import ElementCC3D
from cc3d.cpp import CompuCell

from cc3dslib.simulation import Element


class NucleusCompartmentCell(SteppableBasePy, Element):
    """Steppable to set up compartmentalized cells with a nucleus and cytoplasm.

    Usage of this steppable requires the simulation to have two cell types
    defined, one for the nucleus and one for the cytoplasm. This steppable sets up the
    most basic Hamiltonian for a cell containing a nucleus. This includes the cell
    types "Cytoplasm" with ID 1 and "Nucleus" with ID 2. Default contact energies for
    the contact plugin are set in `NucleusCompartmentCellParams`. Finally, a volume
    constraint is set on both the nucleus and the cytoplasm. The target volume is set
    automatically upon setup. The Lagrange multiplier can be set for the nucleus and
    cytoplasm individually in the `NucleusCompartmentCellParams` class.
    """

    # missing type hints
    NUCLEUS: int
    CYTOPLASM: int
    DUMMY: int
    cell_field: CompuCell.cellfield

    def __init__(
        self,
        params: "NucleusCompartmentCellParams",
    ):
        """Initialize steppable."""
        # Since this steppable is only an initializer, it should only run once, thus
        # it is set to run at a frequency of infinity.
        super().__init__(frequency=float("inf"))

        self.params = params
        self._cluster_ids: np.ndarray = np.array([])

    def start(self):
        """Create a cell with a nucleus and cytoplasm."""
        self._assign_cells_to_grid()
        self._assign_cell_custer_ids()
        self._assign_volume_terms()

    def _assign_cells_to_grid(self):
        """Create new cells in a regular grid with the nucleus in the centre."""
        start_x, start_y, end_x, end_y = self.params.box

        cell_size = self.params.diameter
        nuc_size = int(cell_size * self.params.nucleus_size_ratio)
        nuc_start = int((cell_size - nuc_size) / 2)
        nuc_end = nuc_start + nuc_size

        self.cell_field[:, :, 0] = self.new_cell(self.DUMMY)

        for x in np.arange(start_x, end_x, cell_size).astype(np.float64):
            for y in np.arange(start_y, end_y, cell_size).astype(np.float64):
                self.cell_field[
                    x : x + cell_size, y : y + self.params.diameter, 0
                ] = self.new_cell(self.CYTOPLASM)

                self.cell_field[
                    x + nuc_start : x + nuc_end, y + nuc_start : y + nuc_end, 0
                ] = self.new_cell(self.NUCLEUS)

    def _assign_cell_custer_ids(self):
        """Assign the same cluster ID to the nucleus and cytoplasm of each cell."""
        cluster_ids: list[int] = []
        for cyto_cell, nuc_cell in zip(
            self.cell_list_by_type(self.CYTOPLASM), self.cell_list_by_type(self.NUCLEUS)
        ):
            cluster_id = cyto_cell.clusterId
            self.reassign_cluster_id(nuc_cell, cluster_id)
            cluster_ids.append(cluster_id)

        self._cluster_ids = np.array(cluster_ids)

    def _assign_volume_terms(self):
        """Assign the volume terms for each cell according to the cell size."""
        cell_vol = self.params.diameter**2
        nuc_vol = self.params.nucleus_size_ratio**2 * cell_vol
        cyto_vol = cell_vol - nuc_vol

        for cell in self.cell_list_by_type(self.NUCLEUS):
            cell.targetVolume = nuc_vol
            cell.lambdaVolume = self.params.nuc_lambda_volume

        for cell in self.cell_list_by_type(self.CYTOPLASM):
            cell.targetVolume = cyto_vol
            cell.lambdaVolume = self.params.cyto_lambda_volume

        n_cells = len(self.cell_list_by_type(self.CYTOPLASM))
        box_coords = self.get_box_coordinates()[1]
        box_size = box_coords.x * box_coords.y
        for cell in self.cell_list_by_type(self.DUMMY):
            cell.targetVolume = box_size - n_cells * cell_vol
            cell.lambdaVolume = self.params.cyto_lambda_volume

    def step(self, _):
        pass

    def finish(self):
        pass

    @property
    def cluster_ids(self) -> np.ndarray:
        """Return the cluster IDs of the cells created by this steppable."""
        return self._cluster_ids

    @property
    def n_clusters(self) -> int:
        """Return the number of clusters created by this steppable."""
        start_x, start_y, end_x, end_y = self.params.box
        cell_size = self.params.diameter

        return int((end_x - start_x) / cell_size) * int((end_y - start_y) / cell_size)

    def build(self) -> list[ElementCC3D]:
        """Return the XML element for this steppable."""
        cell_type = ElementCC3D("Plugin", {"Name": "CellType"})
        cell_type.ElementCC3D("CellType", {"TypeId": "0", "TypeName": "Medium"})
        cell_type.ElementCC3D("CellType", {"TypeId": "1", "TypeName": "Cytoplasm"})
        cell_type.ElementCC3D("CellType", {"TypeId": "2", "TypeName": "Nucleus"})
        cell_type.ElementCC3D("CellType", {"TypeId": "3", "TypeName": "Dummy"})

        contact_plugin = ElementCC3D("Plugin", {"Name": "Contact"})

        for (type1, type2), j in self.params.contact_energy.items():
            contact_plugin.ElementCC3D(
                "Energy", {"Type1": type1, "Type2": type2}, str(j)
            )

        contact_plugin.ElementCC3D(
            "NeighborOrder", {}, str(self.params.neighbour_order_contact)
        )

        contact_internal_plugin = ElementCC3D("Plugin", {"Name": "ContactInternal"})

        for (type1, type2), j in self.params.contact_internal.items():
            contact_internal_plugin.ElementCC3D(
                "Energy", {"Type1": type1, "Type2": type2}, str(j)
            )

        contact_internal_plugin.ElementCC3D(
            "NeighborOrder", {}, str(self.params.neighbour_order_internal)
        )

        neighbour_plugin = ElementCC3D("Plugin", {"Name": "NeighborTracker"})

        volume_plugin = ElementCC3D("Plugin", {"Name": "Volume"})
        volume_plugin.ElementCC3D(
            "NeighborOrder", {}, str(self.params.neighbour_order_volume)
        )

        # connectivity_plugin = ElementCC3D("Plugin", {"Name": "Connectivity"})
        # connectivity_plugin.ElementCC3D("Penalty", {}, "100000")

        return [
            cell_type,
            contact_plugin,
            contact_internal_plugin,
            neighbour_plugin,
            volume_plugin,
            # connectivity_plugin,
        ]


CellType = Literal["Medium", "Cytoplasm", "Nucleus", "Dummy"]


def _default_j() -> dict[tuple[CellType, CellType], float]:
    return {
        ("Medium", "Medium"): 0.0,
        ("Medium", "Cytoplasm"): 40.0,
        ("Medium", "Nucleus"): 3.0,
        ("Medium", "Dummy"): 3.0,
        ("Cytoplasm", "Cytoplasm"): 3.0,
        ("Cytoplasm", "Nucleus"): 1000.0,
        ("Cytoplasm", "Dummy"): 3.0,
        ("Nucleus", "Nucleus"): 1000.0,
        ("Nucleus", "Dummy"): 1000.0,
        ("Dummy", "Dummy"): 0.0,
    }


def _default_j_internal() -> dict[tuple[CellType, CellType], float]:
    return {
        ("Cytoplasm", "Cytoplasm"): 0.0,
        ("Cytoplasm", "Nucleus"): 2.0,
        ("Nucleus", "Nucleus"): 0.0,
    }


@dataclass
class NucleusCompartmentCellParams:
    """Parameters for NucleusCompartmentCell:

    Attributes:
        - box (tuple[int, int, int, int]): The size of the box that is supposed to be
          filled with a confluent layer of compartmentalised nucleus cells
        - diameter (int): Diameter of the cytoplasm in pixels
        - nucleus_size_ratio (float): Ratio of the nucleus size (must be between 0 and
          1). The nucleus diamter is thus `nucleus_size_ratio * diameter`
        - cyto_lambda_volume (float): Lagrange multiplier of the cytoplasm volume
          constraint
        - nuc_lambda_volume (float): Lagrance multiplier of the nucleus volume
          constraint
        - contact_energy (dict): Dictionary of contact energies between cell types.
        - contact_internal (dict): Dictionary of contact energies between cell nucleus
          and cytoplasm

    """

    box: tuple[int, int, int, int]
    diameter: int = 20
    nucleus_size_ratio: float = 0.2
    cyto_lambda_volume: float = 0.1
    nuc_lambda_volume: float = 1.0
    contact_energy: dict[tuple[CellType, CellType], float] = field(
        default_factory=_default_j,
    )
    contact_internal: dict[tuple[CellType, CellType], float] = field(
        default_factory=_default_j_internal,
    )
    neighbour_order_contact: int = 20
    neighbour_order_internal: int = 20
    neighbour_order_volume: int = 20
