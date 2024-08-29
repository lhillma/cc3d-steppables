"""Steppable for active swimmer cells in the Simulation."""

from dataclasses import dataclass
from cc3d.cpp.CompuCell import CellG
from cc3dslib.filter import Filter
from cc3dslib.simulation import Element
from cc3dslib.active_swimmer import ActiveSwimmerParams

from cc3d.core.PySteppables import SteppableBasePy
from cc3d.core.XMLUtils import ElementCC3D

import numpy as np


class CompartmentSwimmer(SteppableBasePy, Element):
    def __init__(self, params: ActiveSwimmerParams, k: float = 0.1, frequency=1):
        super().__init__(frequency)

        self.params = params
        self.angles: np.ndarray | None = None
        self.coms: np.ndarray | None = None
        self.last_coms: np.ndarray | None = None
        self.max_compartment_size = 0

        self.box_size = None
        self.k = k

    def start(self):
        n_cells = len(list(self.params.filter()))
        self.angles = np.random.random(size=n_cells) * 2 * np.pi

        self.max_compartment_size = 0
        for cells in self.params.filter():
            self.max_compartment_size = max(self.max_compartment_size, len(cells))

        self.coms = np.zeros((n_cells, 3))
        self.last_coms = np.zeros((n_cells, self.max_compartment_size, 3))
        for i, cells in enumerate(self.params.filter()):
            # cells = [c for c in cells_raw if c.type == 1]
            self.last_coms[i, : len(cells), :] = np.array(
                [self._get_com(cell) for cell in cells]
            )

        box_coords = self.get_box_coordinates()[1]
        self.box_size = np.array([box_coords.x, box_coords.y, box_coords.z])

    def step(self, mcs: int):
        self._update_coms()
        self._update_forces(mcs)
        self._update_angles()

    def _update_forces(self, mcs):
        if self.angles is None or self.coms is None:
            return

        force_magnitude = (
            self.params.force_magnitude
            if mcs > self.params.initial_steps
            else self.params.initial_magnitude
        )

        for cidx, (compartments, angle) in enumerate(
            zip(
                self.params.filter(),
                self.angles,
            )
        ):
            for cell in compartments:
                if cell.type == 2 and cell.volume > 0:
                    compartment_com = self.coms[cidx]
                    cell_com = self._get_com(cell)

                    # spring force (Hooke's law)
                    k = self.k * force_magnitude  #  * cell.targetVolume
                    force = k * self._unwrapped_distance(compartment_com, cell_com)

                    # force component along X axis
                    cell.lambdaVecX = force[0]
                    # force component along Y axis
                    cell.lambdaVecY = force[1]
                else:
                    # force component along X axis
                    cell.lambdaVecX = force_magnitude * np.cos(angle)
                    # force component along Y axis
                    cell.lambdaVecY = force_magnitude * np.sin(angle)

    def _update_angles(self):
        if self.angles is None:
            return

        self.angles += (np.random.normal(size=self.angles.shape)) * np.sqrt(
            2 * self.params.d_theta
        )

    def _update_coms(self):
        assert self.coms is not None and self.last_coms is not None
        for i, cells in enumerate(self.params.filter()):
            # cells = [c for c in cells_raw if c.type == 1]
            new_coms = np.array([self._get_com(cell) for cell in cells])
            cell_volumes = np.array([cell.volume for cell in cells])
            old_coms = self.last_coms[i, : len(cells), :]

            unwrapped_coms = old_coms + self._unwrapped_distance(old_coms, new_coms)

            self.coms[i, :] = np.average(unwrapped_coms, weights=cell_volumes, axis=0)
            self.last_coms[i, :, :] = unwrapped_coms

    def _get_com(self, cell: CellG) -> np.ndarray:
        """
        Get the center of mass of a cell as numpy array.

        Parameters
        ----------
        cell : CellG
            The cell to get the center of mass of.

        Returns
        -------
        np.ndarray
            The center of mass of the cell
        """
        return np.array([cell.xCOM, cell.yCOM, 0])

    def _unwrapped_distance(self, old_coms, new_coms) -> np.ndarray:
        """
        Compute the unwrapped distance between two center of mass positions.

        Compute the distance between two center of mass positions while taking into
        account the periodic boundary conditions of the simulation.

        Parameters
        ----------
        old_coms : np.ndarray
            The old center of mass positions.
        new_coms : np.ndarray
            The new center of mass positions.

        Returns
        -------
        np.ndarray
            The unwrapped center of mass positions.
        """
        assert self.box_size is not None

        diff = np.empty_like(old_coms)
        for j in range(len(diff)):
            diff[j] = new_coms[j] - old_coms[j]
            diff -= np.rint(diff / self.box_size * 2) * self.box_size / 2
        return diff

        # new_coms = old_coms + diff
        # return new_coms

    def finish(self):
        pass

    def build(self) -> list[ElementCC3D]:
        root_node = ElementCC3D("Plugin", {"Name": "ExternalPotential"})
        root_node.ElementCC3D("Algorithm", {}, "PixelBased")
        return [root_node]
