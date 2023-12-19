"""Steppable for active swimmer cells in the Simulation."""
from dataclasses import dataclass

from cc3d.core.PySteppables import SteppableBasePy

import numpy as np


@dataclass
class ActiveSwimmerParams:
    d_theta: float = 0.1
    force_magnitude: float = 0.8
    cell_size: float = 1


class ActiveSwimmer(SteppableBasePy):
    def __init__(self, params: ActiveSwimmerParams, frequency=1):
        super().__init__(frequency)

        self.params = params
        self.angles: np.ndarray | None = None

    def start(self):
        self.angles = np.random.random(size=len(self.clusters)) * 2 * np.pi

    def step(self, _):
        if self.angles is None:
            return

        assert self.clusters is not None

        for compartments, angle in zip(
            self.clusters,
            self.angles,
        ):
            for cell in compartments:
                # force component along X axis
                cell.lambdaVecX = (
                    self.params.force_magnitude
                    * np.cos(angle)
                    * cell.targetVolume
                    / self.params.cell_size**2
                )
                # force component along Y axis
                cell.lambdaVecY = (
                    self.params.force_magnitude
                    * np.sin(angle)
                    * cell.targetVolume
                    / self.params.cell_size**2
                )

        self.angles += (
            np.random.random(size=self.angles.shape) - 0.5
        ) * self.params.d_theta

    def finish(self):
        pass
