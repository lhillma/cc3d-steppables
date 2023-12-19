"""Steppable to track the center of mass of cells in a simulation."""

from pathlib import Path

import numpy as np
import h5py
from cc3d.core.PySteppables import SteppableBasePy


class COMTracker(SteppableBasePy):
    """
    Steppable to track the center of mass of cells between simulation steps.

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
        ), "No cells in simulation. Please add COMTracker after cell creation steppables."

        n_particles = len(self.cell_list)
        self.com_dset = self.file.create_dataset(
            "com",
            (0, n_particles, self.dims),
            maxshape=(None, n_particles, self.dims),
            dtype="f",
        )
        self.coms = np.empty((self.chunk_size, n_particles, self.dims))

    def step(self, _):
        assert self.cell_list, "No cells in simulation."

        if self.steps % self.chunk_size == 0:
            self.com_dset.resize(self.com_dset.shape[0] + self.chunk_size, axis=0)
            self.com_dset[-self.chunk_size :, :, :] = self.coms

        for i, cell in enumerate(self.cell_list):
            self.coms[self.steps % self.chunk_size, i, :] = cell.xCOM, cell.yCOM

        self.steps += 1

    def finish(self):
        self.com_dset[-self.chunk_size :, :, :] = self.coms
        self.com_dset.resize(self.steps, axis=0)
        self.file.close()

    def on_stop(self):
        self.finish()
