def configure_simulation():

    from cc3d.core.XMLUtils import ElementCC3D

    import CC3D_import_image_Complex_map_cells_Parameters as p
    
    CompuCell3DElmnt=ElementCC3D("CompuCell3D",{"Revision":"20200731","Version":"4.2.3"})
    
    MetadataElmnt=CompuCell3DElmnt.ElementCC3D("Metadata")
    # Basic properties simulation
    MetadataElmnt.ElementCC3D("NumberOfProcessors",{},"1")
    MetadataElmnt.ElementCC3D("DebugOutputFrequency",{},"10")
    # MetadataElmnt.ElementCC3D("NonParallelModule",{"Name":"Potts"})
    
    PottsElmnt=CompuCell3DElmnt.ElementCC3D("Potts")
    # Basic properties of CPM (GGH) algorithm
    global model_x_width, model_x_width
    PottsElmnt.ElementCC3D("Dimensions",{"x":p.xDim,"y":p.yDim,"z":"1"})
    PottsElmnt.ElementCC3D("Steps",{},"8")
    PottsElmnt.ElementCC3D("Temperature",{},"10.0")
    PottsElmnt.ElementCC3D("NeighborOrder",{},"1")
    
    PluginElmnt=CompuCell3DElmnt.ElementCC3D("Plugin",{"Name":"CellType"})
    # Listing all cell types in the simulation
    PluginElmnt.ElementCC3D("CellType",{"TypeId":"0","TypeName":"Medium"})
    PluginElmnt.ElementCC3D("CellType",{"TypeId":"1","TypeName":"cellborder","Freeze":"1"})
    PluginElmnt.ElementCC3D("CellType",{"TypeId":"2","TypeName":"cell","Freeze":"1"})
    PluginElmnt.ElementCC3D("CellType",{"TypeId":"3","TypeName":"wall","Freeze":"1"})
    PluginElmnt.ElementCC3D("CellType",{"TypeId":"4","TypeName":"source","Freeze":"1"})
    PluginElmnt.ElementCC3D("CellType",{"TypeId":"5","TypeName":"blood","Freeze":"1"})

    
    # the below is required even though the cells are never used, it forces CC3D to setup some of the data structures
    SteppableElmnt=CompuCell3DElmnt.ElementCC3D("Steppable",{"Type":"UniformInitializer"})
    # Initial layout of cells in the form of rectangular slab
    RegionElmnt=SteppableElmnt.ElementCC3D("Region")
    RegionElmnt.ElementCC3D("BoxMin",{"x":"0", "y":"0", "z":"0"})
    RegionElmnt.ElementCC3D("BoxMax",{"x":40,"y":40,"z":"1"})
    RegionElmnt.ElementCC3D("Gap",{},0)
    RegionElmnt.ElementCC3D("Width",{},20)  
    RegionElmnt.ElementCC3D("Types",{},"wall")

    CompuCellSetup.setSimulationXMLDescription(CompuCell3DElmnt)
            
from cc3d import CompuCellSetup

configure_simulation()            

from CC3D_import_image_Complex_map_cellsSteppables import CC3D_import_image_Complex_map_cellsSteppables
CompuCellSetup.register_steppable(steppable=CC3D_import_image_Complex_map_cellsSteppables(frequency=1))

CompuCellSetup.run()
