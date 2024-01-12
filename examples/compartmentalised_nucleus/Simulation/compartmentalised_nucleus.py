from cc3d import CompuCellSetup
from cc3dslib.nucleus import NucleusCompartmentCell, NucleusCompartmentCellParams
from cc3dslib.filter import CompartmentFilter
from cc3dslib import ActiveSwimmer, ActiveSwimmerParams

# nucleus
nuc_params = NucleusCompartmentCellParams(
    box=(0, 0, 400, 400), nucleus_size_ratio=0.3, lambda_nuc=0.5
)
CompuCellSetup.register_steppable(NucleusCompartmentCell(params=nuc_params))

# active force
cell_filter = CompartmentFilter()
CompuCellSetup.register_steppable(cell_filter)
active_params = ActiveSwimmerParams(
    filter=cell_filter, cell_size=nuc_params.cell_size, d_theta=0.1, force_magnitude=1.0
)
CompuCellSetup.register_steppable(ActiveSwimmer(params=active_params))

CompuCellSetup.run()
