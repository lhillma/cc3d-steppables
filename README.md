# CC3D Steppables

This project aims to be a repository of steppables to use for CompuCell3D
simulations. The steppables are written in Python and can be used in and
combined with any CC3D simulation.

## Pre-requisites

A working installation of CompuCell3D in a virtual Python environment is
required to use the steppables in this repository. The following assumes that
your virtual Python environment is named `cc3d` (change the commands
accordingly, if this is not the case for you).

## Getting started

Follow the [Installation](#installation) instructions to install the package in
your CompuCell3D Python virtual environment.

This repository contains an example CC3D simulation that uses the steppables
from the library. You can find the example in the `examples` directory. To run
the provided simulation with a cell containing a (stiff) nucleus suspect to a
random force, run the following commands from the root of the repository:

```bash
conda activate cc3d  # change the name to match your virtual Python environment
python -m cc3d.player5 -i examples/compartmentalised_nucelus/simulation.cc3d
```

For a more in-depth explanation of the example simulation, see the
[Usage](#usage) section down below.

## Installation

Clone the repository and install the package using pip:

```bash
git clone https://gitlab.tue.nl/20235660/cc3d-steppables.git
conda activate cc3d  # change the name to match your virtual Python environment
pip install cc3d-steppables
```

## Usage

To use the steppables in your own CC3D simulation, import the package and use
`CompuCellSetup.register_steppable` to register the steppable in your simulation.
Below you can see the Python part of a CC3D simulation that uses the
`NucleusCompartmentCell` steppable to simulate a cell comprised of a nucleus
suspended in cytoplasm:

```python
from cc3dslib.nucleus import NucleusCompartmentCell, NucleusCompartmentCellParams
from cc3dslib.simulation import ConfigBuilder, PottsParams

sim_params = PottsParams(dimensions=(400, 400, 1), steps=1_000_000)

nuc_params = NucleusCompartmentCellParams(
    box=(0, 0, 400, 400), nucleus_size_ratio=0.3, lambda_nuc=0.5
)

(
    ConfigBuilder()
    .base(n_processors=1, dbg_frequency=1000)
    .potts(sim_params)
    .add(NucleusCompartmentCell(params=nuc_params))
    .setup()
    .run()
)
```

You can use several steppables in a single simulation. For example, you can
modify the above simulation to add an active force to each compartment cell. In order
to to so, you need to use a filter in order to select the cells that should be
subject to the active force. In this case, we want to apply the active force to
all cells.

```python
from cc3dslib.nucleus import NucleusCompartmentCell, NucleusCompartmentCellParams
from cc3dslib import ActiveSwimmer, ActiveSwimmerParams

# cells with nucleus
nuc_params = NucleusCompartmentCellParams(
    box=(0, 0, 400, 400), nucleus_size_ratio=0.3, lambda_nuc=0.5
)
nuc_plugin = NucleusCompartmentCell(params=nuc_params)

# active force
cell_filter = CompartmentFilter()
active_params = ActiveSwimmerParams(
    filter=cell_filter, cell_size=nuc_params.cell_size, d_theta=0.1, force_magnitude=1.0
)
active_plugin = ActiveSwimmer(params=active_params)

(
    ConfigBuilder()
    .base(n_processors=1, dbg_frequency=1000)
    .potts(sim_params)
    .add(nuc_plugin)
    .add(cell_filter)
    .add(active_plugin)
    .setup()
    .run()
)
```

Below you can see a screenshot of the simulation resulting from the snippet
above:

![Simulation_screenshot](assets/nucleus_w_active_force_screenshot.png)

## Contributing
Contributions via merge requests are always welcome. If you encounter an issue
and don't have the time to fix it, please open an issue and describe the
problem. If you have a question, please open an issue and describe the problem.

### Pre-commit
The project uses [pre-commit](https://pre-commit.com/) to run some checks on any
changes prior to committing them. Please install pre-commit in your virtual
Python environment in order to automatically adhere to the coding style required
for this project. To do so, it should suffice to run the following two commands
from the root of the repository:

```bash
pip install --upgrade pre-commit
pre-commit install
```

## Authors and acknowledgment
Many of the steppables in this repository are based on the work of Quirine
Braat and P. M. C. Wielstra.

## License

TBA

## Project status
This project is in active development, so expect changes to the API and the
feature set.
