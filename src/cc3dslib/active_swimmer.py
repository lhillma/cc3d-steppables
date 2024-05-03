"""Steppable for active swimmer cells in the Simulation."""
from dataclasses import dataclass
from cc3d.cpp.CompuCell import CellG
from cc3dslib.filter import Filter
from cc3dslib.simulation import Element
from cc3d.core.PySteppables import SteppableBasePy
from cc3d.core.XMLUtils import ElementCC3D

import numpy as np

from typing import List
from typing import Tuple

#import random
#from collections import defaultdict




@dataclass
class ActiveSwimmerParams:
    filter: Filter[List[CellG]]
    force_magnitudes: dict[int, float]
    force: Tuple[float, float]
    d_theta: float

class ActiveSwimmer(SteppableBasePy, Element):
    def __init__(self, params: ActiveSwimmerParams, frequency=1):

        super().__init__(frequency)

        self.params = params
        self.angles: np.ndarray | None = None
        self.cell_force_magnitudes = self.params.force_magnitudes

    def start(self):
        self.angles = np.random.random(size=len(list(self.params.filter()))) * 2 * np.pi
        self.cell_force_magnitudes = {}
        for compartments in self.params.filter():
            for cell in compartments:
                self.cell_force_magnitudes[cell.id] = np.random.normal(self.params.force[0], self.params.force[1])

    def step(self, _):
        if self.angles is None:
            return

        for compartments, angle in zip(
            self.params.filter(),
            self.angles
        ):
            for cell in compartments:
                #generate force magnitude from a normal distribution
                force_magnitude_normal = self.cell_force_magnitudes[cell.id]
                # force component along X axis
                cell.lambdaVecX = force_magnitude_normal * np.cos(angle)
                # force component along Y axis
                cell.lambdaVecY = force_magnitude_normal * np.sin(angle)
                # force magnitude
                #cell.lambdaVecMag = np.sqrt(cell.lambdaVecX**2 + cell.lambdaVecY**2)

        self.angles += (
            np.random.random(size=self.angles.shape) - 0.5
        ) * self.params.d_theta

    def finish(self):
        pass
    def build(self) -> list[ElementCC3D]:
        root_node = ElementCC3D("Plugin", {"Name": "ExternalPotential"})
        root_node.ElementCC3D("Algorithm", {}, "CenterOfMassBased")
        return [root_node]
