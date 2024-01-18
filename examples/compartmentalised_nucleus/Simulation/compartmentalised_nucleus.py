from cc3dslib.nucleus import NucleusCompartmentCell, NucleusCompartmentCellParams
from cc3dslib.filter import CompartmentFilter
from cc3dslib import ActiveSwimmer, ActiveSwimmerParams
from cc3dslib.simulation import ConfigBuilder, PottsParams


sim_params = PottsParams(dimensions=(100, 100, 1), steps=1_000_000)

# nucleus
nuc_params = NucleusCompartmentCellParams(
    box=(0, 0, *sim_params.dimensions[:2]),
    nucleus_size_ratio=0.4,
    lambda_nuc=2,
    lambda_cell=3,
)
nuc_params.J[("Cytoplasm", "Cytoplasm")] = 2.0
nuc_params.J_internal[("Cytoplasm", "Nucleus")] = 2.0
nuc_steppable = NucleusCompartmentCell(params=nuc_params)

# active force
cell_filter = CompartmentFilter()
active_params = ActiveSwimmerParams(
    filter=cell_filter,
    cell_size=nuc_params.cell_size,
    d_theta=0.1,
    force_magnitude=10.0,
)
active_steppable = ActiveSwimmer(params=active_params)


(
    ConfigBuilder()
    .base(n_processors=1, dbg_frequency=1000)
    .potts(sim_params)
    .add(nuc_steppable)
    .add(cell_filter)
    .add(active_steppable)
    .setup()
    .run()
)
