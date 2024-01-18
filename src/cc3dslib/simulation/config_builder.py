import cc3d
from cc3d.core.PySteppables import SteppableBasePy
from cc3d.core.XMLUtils import ElementCC3D

from .element import Element

from dataclasses import dataclass, field


@dataclass
class PottsParams:
    dimensions: tuple[int, int, int] = field(default=(100, 100, 1))
    steps: int = field(default=1000)
    temperature: float = field(default=1.0)
    neighborOrder: int = field(default=2)
    boundary_x: str = field(default="Periodic")
    boundary_y: str = field(default="Periodic")
    boundary_z: str | None = field(default=None)


class ConfigBuilder:
    def __init__(self):
        self.root_element = ElementCC3D(
            "CompuCell3D", {"Revision": "0", "Version": cc3d.__version__}
        )
        self.elements: list[Element] = []

    def base(self, n_processors: int = 1, dbg_frequency: int = 4000) -> "ConfigBuilder":
        metadata = self.root_element.ElementCC3D("Metadata")
        metadata.ElementCC3D("NumberOfProcessors", {}, str(n_processors))
        metadata.ElementCC3D("DebugOutputFrequency", {}, str(dbg_frequency))
        return self

    def potts(self, params: PottsParams) -> "ConfigBuilder":
        potts = self.root_element.ElementCC3D("Potts")
        potts.ElementCC3D(
            "Dimensions", {x: params.dimensions[i] for i, x in enumerate("xyz")}
        )
        potts.ElementCC3D("Steps", {}, str(params.steps))
        potts.ElementCC3D("Temperature", {}, str(params.temperature))
        potts.ElementCC3D("NeighborOrder", {}, str(params.neighborOrder))
        potts.ElementCC3D("Boundary_x", {}, params.boundary_x)
        potts.ElementCC3D("Boundary_y", {}, params.boundary_y)
        if params.boundary_z is not None:
            potts.ElementCC3D("Boundary_z", {}, params.boundary_z)
        return self

    def add(self, element: Element) -> "ConfigBuilder":
        self.elements.append(element)
        for e in element.build():
            self.root_element.add_child(e)
        return self

    def build(self) -> ElementCC3D:
        return self.root_element

    def setup(self) -> "Simulation":
        from cc3d import CompuCellSetup

        CompuCellSetup.setSimulationXMLDescription(self.build())

        for element in filter(lambda x: isinstance(x, SteppableBasePy), self.elements):
            CompuCellSetup.register_steppable(element)

        return Simulation()


class Simulation:
    def run(self) -> None:
        """Wrapper to run the simulation by calling

        `cc3d.core.CompuCellSetup.run`.
        """
        from cc3d import CompuCellSetup

        CompuCellSetup.run()
