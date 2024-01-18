from dataclasses import dataclass

from cc3d.core.PySteppables import SteppableBasePy
from cc3d.core.XMLUtils import ElementCC3D

from cc3dslib.simulation import Element
from cc3dslib.filter import Filter


@dataclass
class VolumeConstraintParams:
    """Parameters for the volume constraint steppable."""

    volume: float
    lambda_volume: float
    filter: Filter


class VolumeConstraint(SteppableBasePy, Element):
    def __init__(self, params: VolumeConstraintParams):
        super().__init__(frequency=float("inf"))
        self.filter = filter
        self.params = params

    def start(self):
        """Set up the volume constraint."""
        for cell in self.params.filter():
            cell.targetVolume = self.params.volume
            cell.lambdaVolume = self.params.lambda_volume

    def build(self) -> list[ElementCC3D]:
        """Build the XML elements for this steppable."""
        volume_plugin = ElementCC3D("Plugin", {"Name": "Volume"})
        return [volume_plugin]
