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
    change_timestep: float

class ActiveSwimmer(SteppableBasePy, Element):
    def __init__(self, params: ActiveSwimmerParams, frequency=1):
        
        super().__init__(frequency)

        self.params = params
        self.angles: np.ndarray | None = None
        self.cell_force_magnitudes = {}

    def start(self):
        # draw random angles
        self.angles = np.random.random(size=len(list(self.params.filter()))) * 2 * np.pi

        # draw random motilities
        for compartments in self.params.filter():
                self.cell_force_magnitudes[compartments[0].id] = np.random.normal(self.params.force_magnitude[0], self.params.force_magnitude[1])

        with open('force_list.txt', 'w') as f:
            for value in self.cell_force_magnitudes:
                f.write("f{value}\n")

        # Set initial motility value
        self.params.motility = 200

    def step(self, msc):
        if self.angles is None:
            return

        for compartments, angle in zip(
            self.params.filter(),
            self.angles
        ):
        # generate force magnitude from a normal distribution
            if msc < self.params.change_timestep:
                force_magnitude_normal = self.params.motility
                # print(msc, force_magnitude_normal)
            else:
                force_magnitude_normal = self.cell_force_magnitudes[compartments[0].id]

            for cell in compartments:
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