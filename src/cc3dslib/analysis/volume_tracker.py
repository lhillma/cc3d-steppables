
'''
from dataclasses import dataclass
from cc3d.cpp.CompuCell import CellG
from cc3dslib.filter import Filter

@dataclass
class VolumeTrackerParams:
    filter: Filter[CellG]

class VolumeTracker(SteppableBasePy, Element):
    def __init__(self, params: VolumeTrackerParams, frequency):
        super().__init__(frequency=frequency)
        self.params = params

    def start(self):
        print(list(self.params.filter()))

    def step(self, step):
        pass

    def finish(self):
        # this is called when the simulation ends
        pass

    def stop(self):
        # this is called when the user presses stop
        pass

    def build(self) -> list(ElementCC3D):
        return []

'''

