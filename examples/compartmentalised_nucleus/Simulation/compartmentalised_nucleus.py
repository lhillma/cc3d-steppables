from cc3d import CompuCellSetup
from cc3dslib.nucleus import NucleusCompartmentCell, NucleusCompartmentCellParams
from cc3dslib import ActiveSwimmer, ActiveSwimmerParams

# from cc3dslib.analysis import COMTracker, DistanceTracker

import numpy as np

nuc_params = NucleusCompartmentCellParams(
    box=(0, 0, 400, 400), nucleus_size_ratio=0.3, lambda_nuc=0.5
)
CompuCellSetup.register_steppable(NucleusCompartmentCell(params=nuc_params))

active_params = ActiveSwimmerParams(
    cell_size=nuc_params.cell_size, d_theta=0.1, force_magnitude=1.0
)
CompuCellSetup.register_steppable(ActiveSwimmer(params=active_params))

# CompuCellSetup.register_steppable(COMTracker(filename="com.h5", frequency=1))
# CompuCellSetup.register_steppable(
#     DistanceTracker(filename="distances.h5", frequency=10)
# )


# CompuCellSetup.register_steppable(
#     steppable=cyt_nuc_interaction_long_short_timesSteppable(frequency=1)
# )


CompuCellSetup.run()
