"""Steppable for active swimmer cells in the Simulation."""
from dataclasses import dataclass
from cc3d.cpp.CompuCell import CellG
from cc3dslib.filter import Filter
from cc3dslib.simulation import Element

from cc3d.core.PySteppables import SteppableBasePy
from cc3d.core.XMLUtils import ElementCC3D

import numpy as np


@dataclass
class ActiveSwimmerParams:
    filter: Filter[list[CellG]]
    d_theta: float = 0.1
    force_magnitude: float = 0.8
    initial_magnitude: float = 0.0
    initial_steps: int = 0


class ActiveSwimmer(SteppableBasePy, Element):
    def __init__(self, params: ActiveSwimmerParams, frequency=1):
        super().__init__(frequency)

        self.params = params
        self.angles: np.ndarray | None = None

    def start(self):
        self.angles = np.random.random(size=len(list(self.params.filter()))) * 2 * np.pi

    def step(self, mcs: int):
        if self.angles is None:
            return

        force = (
            self.params.force_magnitude
            if mcs >= self.params.initial_steps
            else self.params.initial_magnitude
        )

        for compartments, angle in zip(
            self.params.filter(),
            self.angles,
        ):
            for cell in compartments:
                # force component along X axis
                cell.lambdaVecX = force * np.cos(angle)
                # force component along Y axis
                cell.lambdaVecY = force * np.sin(angle)

        self.angles += (
            np.random.random(size=self.angles.shape) - 0.5
        ) * self.params.d_theta

    def finish(self):
        pass

    def build(self) -> list[ElementCC3D]:
        root_node = ElementCC3D("Plugin", {"Name": "ExternalPotential"})
        root_node.ElementCC3D("Algorithm", {}, "CenterOfMassBased")
        return [root_node]
