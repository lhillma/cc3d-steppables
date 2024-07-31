"""Steppable to track the center of mass of cells in a simulation."""

from pathlib import Path

import numpy as np
import h5py
from cc3d.core.PySteppables import SteppableBasePy
from cc3d.cpp.CompuCell import CellG
from cc3d.core.XMLUtils import ElementCC3D

from cc3dslib.filter import Filter
from cc3dslib.simulation import Element


class COMTracker(SteppableBasePy, Element):
    """
    Steppable to track the center of mass of cells between simulation steps.
    """

    def __init__(
        self,
        filename: Path | str,
        filter: Filter[list[CellG]],
        dims: int = 2,
        chunk_size=1000,
        frequency=1,
        wrap_box: None | tuple[float, float] | tuple[float, float, float] = None,
    ):
        super().__init__(frequency)

        self.filename = filename
        self.dims = dims
        self.chunk_size = chunk_size
        self.filter = filter
        if wrap_box is not None:
            self.wrap_box = np.array(wrap_box)
            if len(self.wrap_box) == 2:
                self.wrap_box = np.append(wrap_box, 0)
            if len(self.wrap_box) != 3:
                raise ValueError("wrap_box must be a 2 or 3 element tuple.")
        else:
            self.wrap_box = None

        self.box_size = None

    def start(self):
        self.steps = 0
        self.file = h5py.File(self.filename, "w")

        n_particles = len(list(self.filter()))
        self.com_dset = self.file.create_dataset(
            "com",
            (0, n_particles, self.dims),
            maxshape=(None, n_particles, self.dims),
            dtype="f",
        )

        self.max_compartment_size = 0
        for cells in self.filter():
            self.max_compartment_size = max(self.max_compartment_size, len(cells))

        self.coms = np.empty((self.chunk_size, n_particles, 3))
        self.last_coms = np.zeros((n_particles, self.max_compartment_size, 3))
        for i, cells in enumerate(self.filter()):
            self.last_coms[i, : len(cells), :] = np.array(
                [self._get_com(cell) for cell in cells]
            )

        box_coords = self.get_box_coordinates()[1]
        self.box_size = np.array([box_coords.x, box_coords.y, box_coords.z])

    def step(self, _):
        for i, cells in enumerate(self.filter()):
            new_coms = np.array([self._get_com(cell) for cell in cells])
            cell_volumes = np.array([cell.volume for cell in cells])
            old_coms = self.last_coms[i, : len(cells), :]

            if cell_volumes.sum() == 0:
                unwrapped_coms = np.zeros_like(new_coms)
                cell_volumes = np.ones_like(cell_volumes)
            else:
                unwrapped_coms = old_coms + self._unwrapped_distance(old_coms, new_coms)

            self.coms[self.steps % self.chunk_size, i, :] = np.average(
                unwrapped_coms, weights=cell_volumes, axis=0
            )
            self.last_coms[i, :, :] = unwrapped_coms

        self.steps += 1
        if self.steps % self.chunk_size == 0:
            self._append_coms_to_h5()

    def finish(self):
        self._append_coms_to_h5()
        self.com_dset.resize(self.steps, axis=0)
        self.file.close()

    def on_stop(self):
        self.finish()

    def build(self) -> list[ElementCC3D]:
        com_plugin = ElementCC3D("Plugin", {"Name": "CenterOfMass"})
        return [com_plugin]

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
        return np.array(
            [
                cell.xCOM,
                cell.yCOM,
                0 if self.dims == 2 else cell.zCOM,
            ]
        )

    def _append_coms_to_h5(self) -> None:
        """
        Append the center of mass positions to the HDF5 dataset.
        """
        self.com_dset.resize(self.com_dset.shape[0] + self.chunk_size, axis=0)
        if self.wrap_box is None:
            self.com_dset[-self.chunk_size :, :, :] = self.coms[:, :, : self.dims]
            return

        self.com_dset[-self.chunk_size :, :, :] = (
            self.coms[:, :, : self.dims] % self.wrap_box[None, None, : self.dims]
        )

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
