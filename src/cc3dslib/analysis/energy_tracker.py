from pathlib import Path
from cc3d.core.PySteppables import SteppableBasePy
from cc3d.core.XMLUtils import ElementCC3D

from cc3dslib.simulation.element import Element

import numpy as np


class EnergyTracker(SteppableBasePy, Element):
    def __init__(self, frequency=1):
        super().__init__(frequency)
        self.num_flips: int = 0
        self.energy_names: list[str] = []
        self.energy_changes: list[np.ndarray] = []
        self.accepted_energy_changes: list[np.ndarray] = []
        self.flip_results: list[float] = []

    def step(self, mcs: int):
        calcs = self.get_energy_calculations()

        if mcs == 0:
            self.energy_names = calcs.function_names

        self.energy_changes.append(np.array(calcs.energy_changes).mean(axis=0))
        if np.array(calcs.flip_results).any():
            self.accepted_energy_changes.append(
                np.array(calcs.energy_changes)[np.array(calcs.flip_results)].mean(
                    axis=0
                )
            )
        else:
            self.accepted_energy_changes.append(np.zeros(len(self.energy_names)))
        self.flip_results.append(np.array(calcs.flip_results).mean())

    def calc_acceptance_rates(self) -> np.ndarray:
        return np.array(self.flip_results)

    def save(self, filename: str | Path) -> None:
        np.savez(
            filename,
            energy_names=self.energy_names,
            energy_changes=np.array(self.energy_changes),
            accepted_energy_changes=np.array(self.accepted_energy_changes),
            flip_results=np.array(self.flip_results),
        )

    def build(self) -> list[ElementCC3D]:
        return []
