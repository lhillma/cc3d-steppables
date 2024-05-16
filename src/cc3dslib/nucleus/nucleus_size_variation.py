from typing import Literal
from dataclasses import dataclass, field

import numpy as np

from cc3d.core.PySteppables import SteppableBasePy
from cc3d.core.XMLUtils import ElementCC3D
from cc3d.cpp import CompuCell

from cc3dslib.simulation import Element


def vary_nucleus_sizes()