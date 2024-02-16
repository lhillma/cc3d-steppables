'''
Parameters to import an image and convert to a cell field in CC3D.
Made by J Sluka Sept. 2020, edited by Yi He Zhu 2023
Developed for CC3D version 4.x and Python 3.x

Parameters needed:
    1. file name and path to a suitable image (jpg, jpeg, bmp, png)
        a. need image x and y dimensions
    2. color map that maps colors in image to cell types
        a. by default white is considered to be CC3D Medium
        b. by default black is considered to be the boundary between two cells (or cell and Medium)
        
 Note that this project creates (besides the standard cell field display) a "field" called BMP_image
 to display the input image. This display uses the standard CC3D color map so the colors displayed wont
 match the input image colors.
 '''

import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
################ the input image
inPath="C:/Users/yihez/Desktop/Yogi-de-Pogi/University/Graduation-BME/code/BME-thesis/simulations/img2piff_example/Simulation/"
inImage="setup_filled.png"   # this image is 512x570 pixel
img_path = Path(inPath, inImage)
image = plt.imread(img_path)
xDim = np.shape(image)[1]  # image x width
yDim = np.shape(image)[0]  # image y width
### Colors: 
###       green = 2 hepatocyte (liver parenchymal cell)
###       red = 3 source (cells that are held in place and divide giving hep's)
###       white = 1 wall, bounding box, no cells, nothin, no spin copies, frozen
###       cyan = 4 blood in sinusoids (liver capillary blood vessels) lumen
###       black = 5 cell borders

# The color and cell type number map, as a list of dictionaries.
# Note that the cell type names used in the pif file are derived from the CC3D id's below and the cell names
# in the main CC3D python script.
# for each cell type, represented by a particular color, create a line in the table below. Specify the minimum and maximum 
# values (e.g., rMin and rMax for the red color channel) for each cell type. The min and max values can be the same.
# Recommend to use the first line as black for cell borders and the second for white for Medium (cell type 0).
cmap=[]
cmap.append({'rMin':250, 'rMax':255,   'gMin':250, 'gMax':255,   'bMin':250, 'bMax':255, 'CC3Did':0})  # white, medium=0 (cell wall=1 in the demo)
cmap.append({'rMin':  0, 'rMax':  5,   'gMin':  0, 'gMax':  5,   'bMin':  0, 'bMax':  5, 'CC3Did':0})  # black, cellborder
cmap.append({'rMin':250, 'rMax':255,   'gMin':  0, 'gMax':  5,   'bMin':  0, 'bMax':  5, 'CC3Did':2})  # red, cell

