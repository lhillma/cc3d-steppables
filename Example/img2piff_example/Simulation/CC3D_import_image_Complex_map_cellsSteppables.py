from cc3d.core.PySteppables import *

import CC3D_import_image_Complex_map_cells_Parameters as p   # the parameters file for this project

class CC3D_import_image_Complex_map_cellsSteppables(SteppableBasePy):
    def __init__(self, frequency=1):
        SteppableBasePy.__init__(self, frequency)
        self.create_scalar_field_py("BMP_image")
        
    def start(self):
        self.unkownPixelText = ""
    
    def step(self,mcs):
        if mcs == 1:
            #### This requires the Python Image library. For python 3.7 in CC3D
            #### In a command window, set defualt into the directory:
            ####     C:\CompuCell3D-py3-64bit\python36\Scripts
            #### Then install the impage library using PIP:
            ####     pip.exe install Image

            from PIL import Image
        
            #############################################################################
            img = Image.open(p.img_path)  # these are defined in the paramters file

            print(img)
            ############################################################################
        
        
            print("\n\t\tInput Path:",p.inPath)            
            print("\t\tInput File:",p.inImage)            
            print("\t\t+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            if (img.size[0]>self.dim.x) or (img.size[1]>self.dim.y):
                print("ERROR-- image size:",img.size," is greater then the CC3D model size:",self.dim.x,self.dim.y,"  ...aborting")
                self.stop_simulation()
            else:
                print("\t\t OK IMAGE-- image size:",img.size," CC3D model size should be:",self.dim.x,self.dim.y)
            print("\t\t+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

            # CC3D draws with the origin (0,0) in upper left, invert the data so the image matches CC3D
            self.img=img.transpose(Image.FLIP_TOP_BOTTOM)
            
            # map the pixels in the image to a user field
            field = self.field.BMP_image
            self.img.format = p.inImage[-3:].upper()
            color_count = {}  # dictionary to store counts of the colors
            # loop over all the pixels in the image and count how often the r,g,b occurs and put
            # a value into the CC3D field for display
            for x,y,z in self.every_pixel():
                if x<self.img.size[0] and y<self.img.size[1]:  # only lattice points that are also within the image
                    if self.img.format == 'PNG':
                        (r, g, b, a) = self.img.getpixel((x, y))  # the rgb for this pixel in the image
                    else:
                        (r, g, b) = self.img.getpixel((x, y))  # the rgb for this pixel in the image

                    gr=(r+g+b)/(255.*3)  # just map the r+g+b into 0-1
                    field[x,y,z] = gr
                    # count the colors
                    pc=str(r)+" "+str(g)+" "+str(b)
                    if (r,g,b) not in color_count:
                        color_count[(r,g,b)]=1
                    else:
                        color_count[(r,g,b)]+=1
                else:
                    field[x,y,z] = 0
            
            # list the color map defined in the parameters file
            print("\n\t\tThe input color map: Type ID, ranges:")
            #print(p.cmap)
            for i in range(len(p.cmap)):
                print("\t\t\t Entry",i,":")
                for k in p.cmap[i]:
                    print("\t\t\t\t ",k,p.cmap[i][k])

            # list how often each color occurs in the image 
            print("\n\t\tHow often each color occured iin input image:")
            for k in color_count: 
                print("\t\t\t ",k,color_count[k])

                
        # try to convert the image into individual cells based on the colors in the image
        if mcs == 2:
            # first, visit every pixel and assign to a new cell of type based on color
            # every pixel will be a cell by itself
            # use numpy arrays to store the data since that will be faster than doing the manipulation
            # directly in CC3D.
            print("\n\t\t converting image to cells, step 2, this may take a while")
            # array to hold cell types
            self.CellType=[[0 for j in range(0,self.dim.y)] for i in range(0,self.dim.x)]
            for x, y, z in self.every_pixel():
                if self.img.format == 'PNG':
                    (r, g, b, a) = self.img.getpixel((x, y))  # the rgb for this pixel in the image
                else:
                    (r, g, b) = self.img.getpixel((x,y))  # the red, green, blue values for this pixel in the image
                self.CellType[x][y] =-1

                for i in range(len(p.cmap)):
                    if r >= p.cmap[i]['rMin'] and r <= p.cmap[i]['rMax']  and \
                       g >= p.cmap[i]['gMin'] and g <= p.cmap[i]['gMax']  and \
                       b >= p.cmap[i]['bMin'] and b <= p.cmap[i]['bMax']:
                           self.CellType[x][y]=p.cmap[i]['CC3Did']
       
                # this pixel didn't match anything
                if self.CellType[x][y] == -1:
                    msg = "Unkown color at pixel -- pixX,pixY: "+str(x)+" "+str(y) \
                                +" -- r,g,b: "+str(r)+" " +str(g)+" "+str(b)+" -- assigned as medium\n"
                    self.unkownPixelText += msg
                    print(msg)
                    self.CellType[x][y] = 0

        if mcs == 3:                    
            # Every pixel is now a seperate cell in the array, collapse neighboring pixels of the
            # same cell type into the same cell. Only compare to the pixels right and up.
            # Note that the models dimensions are (self.dim.x,self.dim.y,self.dim.z)
            # This is not gauranteed to collapse all the pixels in a single scan 
            # through  the pixels, so keep doing it until no more changes are made
            print("\t\t converting image to cells, step 3, this may take a longer while (changes needs to count down to zero)")
            
            # make an array to hold the created CellIDs, same dimensions as the CC3D  
            self.CellID=[[0 for j in range(0,self.dim.y)] for i in range(0,self.dim.x)]
            iii=1 # start at 1 since zero will be used for CC3D Medium
            for x in range(0,self.dim.x):
                for y in range(0,self.dim.y):
                    if self.CellType[x][y] != 0:
                        self.CellID[x][y] = iii  # each pixel is a "cell" and has a unique ID to start
                        iii += 1
                    else:
                        self.CellID[x][y] = 0  # medium
                   
            changes = 1
            print("\t\t\t changes: ",end="")
            while changes != 0:
                changes = 0
                for x in range(0,self.dim.x-1):
                    for y in range(0,self.dim.y-1):
                        ctype1 = self.CellType[x][y]
                        if ctype1 != 0:  # Medium cell type
                            cid1 = self.CellID[x][y]
                            for (dx,dy) in ((0,1),(1,0)):  # look one pixel right, then one pixel up
                                ctype2 = self.CellType[x+dx][y+dy]
                                if ctype2 != 0:
                                    cid2 = self.CellID[x+dx][y+dy]
                                    if ctype1 == ctype2 and cid1 != cid2:
                                        changes += 1
                                        if cid1 <= cid2:
                                            self.CellID[x+dx][y+dy] = cid1
                                        else:
                                            self.CellID[x][y] = cid2                                   
                print(" ",changes,end="",flush=True)
                #print("\t\t\t changes: ",changes)
            print("\n\t\t\t done")

               
            # collect all pixels for each cell 
            print("\t\t collecting pixels into cells, this needs to count up to",self.dim.x)
            self.pixList={} # dictionary to hold all the pixels in each cell, key is cellID, value is x,y,x,y,x,y,...
            ct={};  cell_count=0  # also count unique cell ids
            for x in range(0,self.dim.x):
                if x % 100 == 0 :
                    print("\t\t   x:",x)
                for y in range(0,self.dim.y):
                    if str(self.CellID[x][y]) in self.pixList:
                        self.pixList[str(self.CellID[x][y])] += [x,y]
                    else:
                        self.pixList[str(self.CellID[x][y])]  = [x,y]  
                        cell_count += 1
            print("\t\t\t done")

        if mcs == 4:
            # actually move stuff into CC3D
            print("\n\t\t creating cells from the pixel lists, step 4")
            # create CC3D cells from the pixel lists
            print("\t\t creating cells from the pixel lists")
            cellCount = 1
            for cellID in self.pixList: 
                theTypeID=self.CellType[self.pixList[cellID][0]][self.pixList[cellID][1]] 
                #print("cellID,theTypeID:",cellID,theTypeID)
                if theTypeID == 0:
                    cell = self.new_cell(self.cell_type.Medium)  # these actualy create the CC3D cells
                elif theTypeID == 1:
                    cell = self.new_cell(self.cell_type.cellborder)  # these actualy create the CC3D cells
                elif theTypeID == 2: 
                    cell = self.new_cell(self.cell_type.cell)

                for i in range(0,len(self.pixList[cellID]),2):   
                    x=self.pixList[cellID][i]
                    y=self.pixList[cellID][i+1]
                    self.cell_field[x,y,0] = cell  # this actual adds the pixels to this cell
                cellCount += 1
            print("\t\t done\n")
            
        if mcs == 5:
            # Convert the cell outlines to parts of the cells, look right then up
            print("\t\t convert the cell outlines to parts of the cells, step 5, this may take a while, but not too long")
            # visit all pixels, if border then add to a neighboring cell
            changes=1
            while changes > 0:
                changes = 0
                for x, y, z in self.every_pixel():
                    cell = self.cell_field[x,y,z]
                    if cell:  # make sure it isn't medium
                        if self.CellType[x][y] == 5:  # the black lines in the test image; cell and region borders
                            for (dx,dy) in ((1,0),(0,1)):  # look right then up
                                if 0 <= x+dx < self.dim.x and 0 <= y+dy < self.dim.y:   # make sure pixel is in range
                                    if self.CellType[x+dx][y+dy] != 5:  # the neighbor cant be a line pixel
                                        cell2 = self.cell_field[x+dx,y+dy,z]
                                        if cell2: # this cell is not medium
                                            self.cell_field[x,y,z] = cell2
                                            self.CellType[x][y] = -1  # mark that this pixel has been done
                                            changes += 1
                                            break
                print("\t\t\t changes:",changes)
            print("\t\t done\n")
            
        if mcs == 6:
            # save as a piff file, format:
            # [cell number] [cell type name] [xLow] [xHigh] [yLow] [yHigh] [zLow] [zHigh]
            print("\n\t\t save as a piff, step 6,")
            # need a map from cell type numbers to the names, the numbers and names 
            # are from the celltype plugin in the main oython script
            typeDict = self.cell_type.get_data()
            self.typeName={}
            for name in typeDict:
                self.typeName[typeDict[name]]=name
            print("\t\t Cell Types:",self.typeName)
            
            fn = p.inPath+p.inImage+".piff"
            outFile = open(fn,'w')
            print("\t\t writing to file:",fn)
            # Besides writing to the piff file, the code below also compresses the data somewhat;
            # all pixels for a particular cell within a given colume (y value) are collapsed into 
            # a single line in the piff.
            # In addtion, the cell.id are remaped starting at 1 (the code above typcially give cell.id
            # in the ten to hundreds)
            cellID = {0:0} # dictionary with key being the cell.id and the value being the new id
            nextID = 1
            for x in range(self.dim.x):
                lastCellID = -1
                y1=0;
                for y in range(self.dim.y):
                    cell=self.cell_field[x,y,0]
                    if cell.id not in cellID:
                        cellID[cell.id]=nextID
                        nextID += 1
                    cell_id=cellID[cell.id]
                    
                    #print("\t newY: ",self.typeName[cell.type],cell.id,"   ",str(x),str(y))
                    if cell.id == lastCellID or y == 0:
                        outLine = str(cell_id)+" "+self.typeName[cell.type]+" " \
                                 +str(x) +" "+str(x) +" "+str(y1)+" "+str(y)+" "+str(0) +" "+str(0) +"\n" 
                    else:
                        outFile.write(outLine)
                        #print("\t\t outLine:",outLine)
                        y1=y
                        outLine = str(cell_id)+" "+self.typeName[cell.type]+" " \
                                 +str(x) +" "+str(x) +" "+str(y1)+" "+str(y)+" "+str(0) +" "+str(0) +"\n" 

                    lastCellID = cell.id
                        
                outFile.write(outLine)
                #rint("\t finalY:",outLine)        
            outFile.close()
            print("\t\t done writing pif file\n")
            
            print("\n\t\t cellID dictionary:\n\t\t ",cellID)

        if mcs == 7:
            # count the number of cells of each type
            print("\n\t\t summary statistices, step 7,")
            cell_type_counts  = {}
            cell_type_minsize = {}
            cell_type_maxsize = {}
            totalPix = 0
            for cell in self.cell_list:
                totalPix += cell.volume 
                if cell.type in cell_type_counts:
                    cell_type_counts[cell.type] += 1
                    cell_type_minsize[cell.type] = min(cell.volume,cell_type_minsize[cell.type])
                    cell_type_maxsize[cell.type] = max(cell.volume,cell_type_maxsize[cell.type])
                else:
                    cell_type_counts[cell.type] = 1    
                    cell_type_minsize[cell.type] = cell.volume
                    cell_type_maxsize[cell.type] = cell.volume
            
            print("\t\t Total non-medium pixels:",totalPix)
            if self.cell_type.Medium in cell_type_counts:
                print("\t\t Total medium pixels:",cell_type_counts[self.cell_type.Medium],"\n")
            else:
                print("\t\t Total medium pixels: 0\n")
            print("\t\t celltype id, name, count of cells, minVol, maxVol:")
            for akey in sorted(cell_type_counts):
                print("\t\t",akey,self.typeName[akey],cell_type_counts[akey],cell_type_minsize[akey],cell_type_maxsize[akey])
            if self.unkownPixelText:
                print("\n\t\t Unkown pixel color info:\n\t\t\t",self.unkownPixelText)
            else:
                print("\n\t\t Unkown pixel color info:\n\t\t\t no unkown pixel colors")
            print("\n\n")
  