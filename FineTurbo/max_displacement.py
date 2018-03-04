# Copyright (c) 2018 Thanos Poulos
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

__version__ = '0.1'  
__author__ = 'Thanos Poulos'
__license__ = 'MIT'

# Author: Thanos Poulos
# Date: October 2016
"""
Calculate the maximum displacement given the mode shape file
and the generalized displacement

"""

# Import packages
#---------------
import sys
import os
import numpy as np


# User Input
#-------------

# Absolute path the the structure file
structure_file_path = "modes.dat"


# Generalized displacement list that should contain a value for each mode shape
# If there are fewer values than mode shapes in the file, the remaining will be
# to zero. If it has more, then the script will stop with an error.
#
# Here the maximum displacement has to be input, not the time profile or the harmonic
# components. For these cases, the maximum has to be found and input here
generalized_disp_list = [0.0005, 0.0004]




# Functions
#----------
def read_structure_file(file_path):
    """
    Takes as an input the structure file in FINE format and creates
    a dictionary with the header line information and an array of the
    mode shapes

    Input:
    - file_path: Path to the structure file including extension

    Output:
    - global_info_dict: Dictionary with the global information of the structure file
    - mode_shapes: mode shape array
    """

    print("<<< Reading structure file for %s >>>") %(os.path.basename(file_path))

    # Get the global information of the structure file
    f = open(file_path,"r")

    # Skip the first line since it is a commentl line
    line = f.readline()

    # Get number of dimensions for the file
    ndim = int(f.readline().split()[4])

    # Get number of modes in the file
    nmodes = int(f.readline().split()[4])

    # Get the number of nodes of the structure mesh
    nnodes = int(f.readline().split()[4])

    # Get initial deformation
    ini_def = int(f.readline().split()[3])

    # Print the global information
    print("<<< Global Information Read Successfully for %s >>>") %(os.path.basename(file_path))
    print("The number of dimensions is %s") %ndim
    print("The number of modes is %s") %nmodes
    print("The number of nodes is %s") %nnodes
    if ini_def == 0:
        print("There is initial deformation present")
    else:
        print("There is no initial deformation present")

    # Put global information in a dictionary
    global_info_dict = {
        'ndim'   : ndim,
        'nmodes' : nmodes,
        'nnodes' : nnodes,
        'ini_def': ini_def
    }


    # Skip two more lines
    line = f.readline()
    line = f.readline()

    # Create the eigenfrequencies list
    eig_freq_list = []

    # Read the list from file
    '''
    line = f.readline()
    while "Mode shapes" not in line:
        if line:
            eig_freq_list.append(float(line))
            print eig_freq_list
        line = f.readline()
    '''

    for i in range(nmodes):
        eig_freq_list.append(float(f.readline()))

    # skip another  lines
    line = f.readline()
    line = f.readline()

    # Read the mode shapes in two arrays: Coordinates and Mode Shapes
    print("<<< Reading mode shapes >>>")
    mode_shapes = []
    line = f.readline()
    while line:
        # Create a array for the mode shapes
        mode_shapes.append(map(float, line.split()))
        line = f.readline()

    mode_shapes_array = np.array(mode_shapes)
    print("<<< Mode shapes have been read successfully >>>")
    f.close()
    return global_info_dict,mode_shapes_array


# Main Program
#--------------

# Check to see if the file exists
if not os.path.isfile(structure_file_path):
    print("****ERROR: File %s does not exist") %(os.path.basename(structure_file_path))
    print("The program will now exit")
    sys.exit()

# Read the structure file information
global_info, array_from_file = read_structure_file(structure_file_path)


# Split the array into coordinates and mode shapes depending on the initial
# deformation
if global_info["ini_def"] == 0:
    coord, mode_shapes = np.hsplit(array_from_file, [global_info["ndim"]])
else:
    coord, mode_shapes = np.hsplit(array_from_file, [global_info["ndim"]*2]) # since we have the coordinates and the initial deformation


# Check to see if the generalized displacement list has the same number of modes
# as the structure file.
if global_info["nmodes"] != len(generalized_disp_list):
    print("WARNING: Then number of modes shapes in the structure file is not equal to the number of generalized displacements given")
    print("WARNING: Zeros will be added in order to fill up the generalized displacement vector\n")
    generalized_disp_list =  generalized_disp_list + [0]*(mode_shapes.shape[1]/global_info["ndim"] - len(generalized_disp_list))

# Create array from generalized displacement list
generalized_disp_array = np.array(generalized_disp_list)

# Create the displacement matrix
# Initialize the array
disp = np.zeros((mode_shapes.shape[0],global_info["ndim"]))

# Loop to create it
c = 0
for gen in generalized_disp_list:
    # Update the displacement array with the product of the generalized
    # displacement for each mode shape
    disp += gen*mode_shapes[:,c:c+global_info["ndim"]]
    c += global_info["ndim"]


# Initialize cylindrical displacement and displacement magnitude arrays
disp_cyl = np.zeros((mode_shapes.shape[0],global_info["ndim"]))
disp_magn = np.zeros((mode_shapes.shape[0]))

# Create the displacement matrix in cylindrical coordinates as well
# Check if it is a 3D case. Effect on the magnitude and the cylindrical
# coordinates
if global_info["ndim"] == 3:
    for i in range(len(disp.shape)):
        disp_cyl[i,0] = np.sqrt(disp[i,0]**2 + disp[i,1]**2)
        disp_cyl[i,1] = np.arctan2(disp[i,1], disp[i,0])
        disp_cyl[i,2] = disp[i,2]
        disp_magn[i] = np.sqrt(disp[i,0]**2 + disp[i,1]**2 + disp[i,2]**2)
else:
    for i in range(len(disp.shape)):
        disp_cyl[i,0] = np.sqrt(disp[i,0]**2 + disp[i,1]**2)
        disp_cyl[i,1] = np.arctan2(disp[i,1], disp[i,0])
        disp_magn[i] = np.sqrt(disp[i,0]**2 + disp[i,1]**2)

#Find the maximum displacement by axis
xmax = np.amax(disp[:,0])
ymax = np.amax(disp[:,1])
# Check if it is a 3D case
if global_info["ndim"] == 3:
    zmax = np.amax(disp[:,2])
rmax = np.amax(disp_cyl[:,0])
thetamax = np.amax(disp_cyl[:,1])
magnmax = np.amax(disp_magn)

print("The maximum displacement along the x axis is: %s")%xmax
print("The maximum displacement along the y axis is: %s")%ymax
# Check if it is a 3D case
if global_info["ndim"] == 3:
    print("The maximum displacement along the z axis is: %s")%zmax
print("The maximum displacement along the radial direction is: %s")%rmax
print("The maximum displacement along the circumferential direction is: %s")%thetamax
print("The maximum of the magnitude of the displacement is: %s")%magnmax
