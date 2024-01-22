from typing import Protocol

from cc3d.core.XMLUtils import ElementCC3D


class Element(Protocol):
    def build(self) -> list[ElementCC3D]:
        ...
