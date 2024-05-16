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
    force_magnitude: Tuple[float, float]
    d_theta: float

class ActiveSwimmer(SteppableBasePy, Element):
    def __init__(self, params: ActiveSwimmerParams, frequency=1):
        
        super().__init__(frequency)

        self.params = params
        self.angles: np.ndarray | None = None

    def start(self):
        self.angles = np.random.random(size=len(list(self.params.filter()))) * 2 * np.pi

    def step(self, _):
        if self.angles is None:
            return

        for compartments, angle in zip(
            self.params.filter(),
            self.angles
        ):
            for cell in compartments:
                #generate force magnitude from a normal distribution
                force_magnitude_normal = np.random.normal(self.params.force_magnitude[0], self.params.force_magnitude[1])
                # force component along X axis
                cell.lambdaVecX = force_magnitude_normal * np.cos(angle)
                # force component along Y axis
                cell.lambdaVecY = force_magnitude_normal * np.sin(angle)

        self.angles += (
            np.random.random(size=self.angles.shape) - 0.5
        ) * self.params.d_theta

    def finish(self):
        pass
    def build(self) -> list[ElementCC3D]:
        root_node = ElementCC3D("Plugin", {"Name": "ExternalPotential"})
        root_node.ElementCC3D("Algorithm", {}, "CenterOfMassBased")
        return [root_node]
