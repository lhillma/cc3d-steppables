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
        force_magnitudes: dict[int,float] | None=None,
        dims: int = 2,
        chunk_size=1000,
        frequency=1,
    ):
        super().__init__(frequency)

        self.filename = filename
        self.dims = dims
        self.chunk_size = chunk_size
        self.filter = filter
        self.force_magnitudes = force_magnitudes if force_magnitudes is not None else {}

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
        self.coms = np.empty((self.chunk_size, n_particles, self.dims))

        self.force_dset = self.file.create_dataset(
            "force_magnitudes",
            (0, n_particles),
            maxshape=(None, n_particles),
            dtype="f",
        )
        self.forces = np.empty((self.chunk_size, n_particles))
    def step(self, _):
        if self.steps % self.chunk_size == 0:
            self.com_dset.resize(self.com_dset.shape[0] + self.chunk_size, axis=0)
            self.force_dset.resize(self.force_dset.shape[0] + self.chunk_size, axis=0)

            self.com_dset[-self.chunk_size :, :, :] = self.coms
            self.force_dset[-self.chunk_size :, :] = self.forces

        for i, cells in enumerate(self.filter()):
            self.coms[self.steps % self.chunk_size, i, :] = 0, 0
            for cell in cells:
                self.coms[self.steps % self.chunk_size, i, :] += cell.xCOM, cell.yCOM
            self.coms[self.steps % self.chunk_size, i, :] /= len(cells)

        for i, cells in enumerate(self.filter()):
            for j, cell in enumerate(cells):
                if cell.id in self.force_magnitudes:
                    self.forces[self.steps % self.chunk_size, i] = self.force_magnitudes[cell.id]
                else:
                    self.forces[self.steps % self.chunk_size, i] = 0
        self.steps += 1

    def finish(self):
        self.com_dset[-self.chunk.size :, :, :] = self.coms
        self.com_dset.resize(self.steps, axis=0)

        self.force_dset[-self.chunk.size :, :] = self.forces
        self.force_dset.resize(self.steps, axis=0)

        self.file.close()

    def on_stop(self):
        self.finish()

    def build(self) -> list[ElementCC3D]:
        com_plugin = ElementCC3D("Plugin", {"Name": "CenterOfMass"})
        return [com_plugin]
