from dataclasses import dataclass

from cc3d.core.PySteppables import SteppableBasePy
from cc3d.core.XMLUtils import ElementCC3D
from cc3d.cpp.CompuCell import CellG

from cc3dslib.filter import Filter
from cc3dslib.simulation import Element

import numpy as np


@dataclass
class VolumeTrackerParams:
    filter: Filter[CellG]


class VolumeTracker(SteppableBasePy, Element):
    def __init__(self, params: VolumeTrackerParams, frequency: int = 1):
        super().__init__(frequency)
        self.params = params

    def start(self):
        """This method will be called at the beginning of the simulation"""
        print("VolumeTracker: start")

    def step(self, mcs):
        """This method will be called at each MCS"""
        print(f"VolumeTracker: step {mcs}")

    def finish(self):
        """This method will be called at the end of the simulation"""
        print("VolumeTracker: finish")

    def on_stop(self):
        """This method will be called when the user stops the simulation"""
        print("VolumeTracker: on_stop")

    def build(self) -> list[ElementCC3D]:
        """This method returns the XML elements for the component"""
        return []


# class VolumeTracker(SteppableBasePy, Element):
#
#     def __init__(self, params: VolumeTrackerParams, frequency: float):
#         super().__init__(frequency=frequency)
#
#         self.params = params
#
#     def start(self):
#         print("Hello from start!")
#         print(list(self.params.filter()))
#
#         self.cell_volumes = []
#
#     def step(self, _):
#         print("Hello from step!")
#         volumes = []
#         for cell in self.params.filter():
#             volumes.append(cell.volume)
#
#         self.cell_volumes.append(np.array(volumes))
#
#     def finish(self):
#         # this is called when the simulation ends
#         print("Hello from finish!")
#
#         # save the data
#         np.savetxt("cell_volumes.txt", np.array(self.cell_volumes))
#
#         pass
#
#     def on_stop(self):
#         # this is called when the user presses stop
#         print("Hello from stop!")
#         self.finish()
#         pass
#
#     def build(self) -> list[ElementCC3D]:
#         volume_tracker = ElementCC3D("Plugin", {"Name": "VolumeTracker"})
#
#         # this translates to
#         # <Plugin Name="VolumeTracker" />
#
#         return [volume_tracker]
