from dataclasses import dataclass

from cc3d.core.PySteppables import SteppableBasePy
from cc3d.core.XMLUtils import ElementCC3D

from cc3dslib.simulation import Element
from cc3dslib.filter import Filter


@dataclass
class SurfaceConstraintParams:
    """Parameters for the volume constraint steppable."""

    surface: float
    lambda_surface: float
    filter: Filter


class SurfaceConstraint(SteppableBasePy, Element):
    def __init__(self, params: SurfaceConstraintParams):
        super().__init__(frequency=float("inf"))
        self.filter = filter
        self.params = params

    def start(self):
        """Set up the volume constraint."""
        for cell in self.params.filter():
            cell.targetSurface = self.params.surface
            cell.lambdaSurface = self.params.lambda_surface

    def build(self) -> list[ElementCC3D]:
        """Build the XML elements for this steppable."""
        volume_plugin = ElementCC3D("Plugin", {"Name": "Surface"})
        return [volume_plugin]
