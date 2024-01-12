"""Steppable to track the displacement vector of cells between simulation steps."""

from pathlib import Path

import numpy as np
import h5py
from cc3d.core.PySteppables import SteppableBasePy


class DistanceTracker(SteppableBasePy):
    """ "Steppable to track the displacement vector of cells between simulation steps.

    This steppable requires the COM plugin to be enabled in the simulation xml file as
    follows:

    <Plugin Name="CenterOfMass" />
    """

    def __init__(
        self,
        filename: Path | str,
        dims: int = 2,
        chunk_size=1000,
        frequency=1,
    ):
        super().__init__(frequency)

        self.filename = filename
        self.dims = dims
        self.chunk_size = chunk_size

    def start(self):
        self.steps = 0
        self.file = h5py.File(self.filename, "w")

        assert (
            self.cell_list is not None
        ), "No cells in simulation. Please add DistanceTracker after cell creation steppables."

        n_particles = len(self.cell_list)
        self.h5_dset = self.file.create_dataset(
            "floats",
            (0, n_particles, self.dims),
            maxshape=(None, n_particles, self.dims),
        )
        self.distances = np.empty((self.chunk_size, n_particles, self.dims))
        self.prev_coms = np.empty((n_particles, 3))

        for i, cell in enumerate(self.cell_list):
            self.prev_coms[i, :] = [
                cell.xCOM,
                cell.yCOM,
                0 if self.dims == 2 else cell.zCOM,
            ]

    def step(self, _):
        assert self.cell_list, "No cells in simulation."

        if self.steps % self.chunk_size == 0:
            self.h5_dset.resize(self.h5_dset.shape[0] + self.chunk_size, axis=0)
            self.h5_dset[-self.chunk_size :, :, :] = self.distances

        for i, cell in enumerate(self.cell_list):
            current_com = [cell.xCOM, cell.yCOM, 0 if self.dims == 2 else cell.zCOM]
            previous_com = self.prev_coms[i, :]
            self.distances[
                self.steps % self.chunk_size, i, :
            ] = self.invariant_distance_vector(current_com, previous_com)[: self.dims]

            self.prev_coms[i, :] = current_com

        self.steps += 1

    def finish(self):
        self.h5_dset[-self.chunk_size :, :, :] = self.distances
        self.h5_dset.resize(self.steps, axis=0)
        self.file.close()

    def on_stop(self):
        self.finish()
