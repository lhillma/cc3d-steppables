from cc3dslib.nucleus import NucleusCompartmentCell, NucleusCompartmentCellParams
from cc3dslib.filter import CompartmentFilter
from cc3dslib import ActiveSwimmer, ActiveSwimmerParams
from cc3dslib.analysis import COMTracker
from cc3dslib.simulation import ConfigBuilder, PottsParams


sim_params = PottsParams(dimensions=(100, 100, 1), steps=1_000_000)

# nucleus
nuc_params = NucleusCompartmentCellParams(
    box=(0, 0, *sim_params.dimensions[:2]),
    nucleus_size_ratio=0.3,
    nuc_lambda_volume=0.5,
)
nuc_plugin = NucleusCompartmentCell(params=nuc_params)

# active force
cell_filter = CompartmentFilter()
active_params = ActiveSwimmerParams(
    filter=cell_filter,
    d_theta=0.1,
    force_magnitude=1.0,
)
active_plugin = ActiveSwimmer(params=active_params)

com_tracker = COMTracker("com.h5", cell_filter, dims=2, chunk_size=1000, frequency=100)

(
    ConfigBuilder()
    .base()
    .potts(sim_params)
    .add(nuc_plugin)
    .add(cell_filter)
    .add(active_plugin)
    .add(com_tracker)
    .setup()
    .run()
)
