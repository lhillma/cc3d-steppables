from dataclasses import dataclass

from cc3d.core.PySteppables import SteppableBasePy
from cc3d.core.XMLUtils import ElementCC3D
from cc3d.cpp.CompuCell import CellG

from cc3dslib.filter import Filter
from cc3dslib.simulation import Element
@dataclass
class VolumeTrackerParams:
    filter: Filter[CellG]

class VolumeTracker(SteppableBasePy, Element):

    def __init__(self, params: VolumeTrackerParams, frequency:float):
        super().__init__(frequency=frequency)

        self.params = params

    def start(self):
        print(list(self.params.filter()))

    def step(self, _):
        pass
    #replacing _ by step gives you the timestep

    def finish(self):
        pass
    #this is called when the simulation ends

    def stop(self):
        pass
    #this is called when the user presses stop

    def build(self) -> list[ElementCC3D]:
        return[]
    #it returns what you put in list[]