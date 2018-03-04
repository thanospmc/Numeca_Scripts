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

###############################################################################
#                           IBPA Creation Script                              #
#                               Developed by                                  #
#                              Thanos Poulos                                  #
#                               March 2015                                    #
#                                                                             #
#                              Description:                                   #
#     This script creates an IBPA line from a forced motion computation       #
#                                                                             #
###############################################################################                                   
#
############## LIBRARY SOURCING ###############################################
#
import os,sys
from math import pi
# The script needs to be run within FINE/Turbo as we need to import the python functions
import FT
#
############## AUXILIARY FUNCTIONS #############################################
#
#
# Transform an angle from degrees to radians
#
def from_deg_to_rad(ang_deg):
    #
    ang_rad = ang_deg*pi/180.0
    #
    return ang_rad
    #

#
#
# Transform an angle from radians to degrees
#
def from_rad_to_deg(ang_rad):
    #
    ang_deg = ang_rad*180.0/pi
    #
    return ang_deg
    #
    
#
# Calculate the Interphase Blade Angles from the Nodal Diameters 
#
def IBPA_from_ND(Nod_diam_nb,nb_blades):
    #
    forward_wave = []
    backward_wave = []
    for n in xrange(1,Nod_diam_nb):
        #
        # Forward travelling wave IBPA definition
        #
        forward_wave.append(2*pi*n/nb_blades)
        #
        # Backward travelling wave IBPA definition
        #
        backward_wave.append(2*pi*(nb_blades-n)/nb_blades)
        #
    #    
    # Create IBPA angles list
    #
    IBPA_angles = backward_wave + forward_wave
    #
    return IBPA_angles
    
#
############## END OF AUXILIARY FUNCTIONS ######################################
#
#    
#
############## INPUT DATA ######################################################
#
#
# Input the number of nodal diameters to be taken into account
#
ND = 10
print "Number of Nodal Diameters to be computed: %s" % ND
#
# Input project path (path needs to end with a / )
#
path = "/marketing/home/poulos/Cases/test_FSI/"
#
# Input project name (without the .iec extension)
#
project_name = "test_FSI"
#
# Is RBF the mesh deformation technique used?
#
RBF = True
if RBF: print "Mesh deformation is RBF"
#
############## END INPUT DATA ##################################################
#
#
############## MAIN BODY #######################################################
#
#
# Open FINE/Turbo project
#
FT.open_project(path + project_name + ".iec")
#
# ++++++ Save new project +++++++++++++++++++++++++++++++++++++++++++++++++++++
#
#FT.save_project_as("test_Py_FSI",0)
#
# ++++++ Get the number of blades (needs to be used for the IBPA defintion ++++
#
# Get the row object in order to find the number of blades on the row
# 0 signifies the first row, 1 the second etc
#
row_object = FT.get_row(0)
#
# Get the number of blades on the found row object
#
nb_blades = row_object.get_nb_blades()
print "The number of blades is %s" % nb_blades
#
# ++++++++++++++ Find forced motion computation +++++++++++++++++++++++++++++++
# 
#
# Get the number of computations
#
nb_computations = FT.get_nb_computations()
#
# Loop in computations to find the forced motion computation
#
for x in xrange(0,nb_computations):
    #
    # Set active computation in FINE/Turbo
    #
    FT.set_active_computations([x])
    #
    # Find if this computation uses the modal approach
    #
    is_elastic = FT.get_elastic_deformation_type()
    if (is_elastic == "Modal"):
        #
        # Write the computation index
        #
        FSI_computation_index = x
        #
        # If the computation is found, break the loop
        #
        break
        #
    #
#
# +++++++++++ User input of computation to be duplicated
#
#FSI_computation_name = "input_name" 
#
#
# +++++++++++ Find the structure which is vibrating +++++++++++++++++++++++++++
#
#
# Set the active computation in order to duplicate
#
FT.set_active_computations([FSI_computation_index])
#
# Get number of Boundary condition groups that are solid
#
nb_bc_groups = FT.get_nb_bc_groups("SOLID")
#
# Get the group ID that is going to be used in FSI
#
for i in xrange(0,nb_bc_groups):
    if FT.get_mechanical_coupled(i):
        #
        coupled_group_index = i
        #
        break
        #
#
# Get computation name
#
FSI_computation_name = FT.get_computation_name(FSI_computation_index)
#
#
# +++++++ Create new computations +++++++++++++++++++++++++++++++++++++++++++++
#
#
# Find IBPA angles
#
IBPAs = IBPA_from_ND(ND,nb_blades)
print "The interblade phase angles in radians are %s" % IBPAs
IBPAs_deg = [ from_rad_to_deg(elem) for elem in IBPAs ]
IBPAs_deg = [ round(elem, 0) for elem in IBPAs_deg ]
print "The interblade phase angles in degrees are", IBPAs_deg
#
# Loop for each interblade phase angle
#
for z in xrange(0,len(IBPAs)):
    #
    # Duplicate the FSI computation and rename
    #
    new_computation_name = FSI_computation_name + "_IBPA_%s" % IBPAs_deg[z]
    FT.new_computation(new_computation_name)
    #
    # Set the new interblade phase angle
    #    
    FT.set_generalized_displacement_NLH_IBPA(coupled_group_index,1,IBPAs[z])
    FT.save_selected_computations()
    #
    # +++++ Create symbolic links if RBF is used ++++++++++++++++++++++++++++++
    #
    if RBF == True:
        #
        # Change the expert parameter ISVMAT in order to avoid recomputing the matrix
        #
        FT.set_expert_parameter("ISVMAT",2)
        #
        # Path to the original deformation matrix
        #
        original_matrix_path = path + project_name + "_" + FSI_computation_name + "/" + FSI_computation_name + ".mat_0"
        print "Path is %s" % original_matrix_path
        #
        # Path to the new matrix
        #
        new_matrix_path = path + project_name + "_" + new_computation_name + "/" + new_computation_name + ".mat_0"
        print "Path is %s" % new_matrix_path
        os.symlink(original_matrix_path,new_matrix_path)
        #
    #
    # +++++ Add task manager and intelmpi options in the batch file +++++++++++
    #
#
# Save project
#
FT.save_project()
    
###############################################################################
#                                                                             #
#                         END SCRIPT                                          #
#                                                                             #
###############################################################################
