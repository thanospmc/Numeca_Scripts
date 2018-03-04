#!/usr/bin/env python
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


######################################################################
#
# Script for extracting the results from the _results directory in
# FINE/Design3D
#
# 2017/06/13 - Thanos Poulos
#
######################################################################


import os
import sys

#----------- USER INPUTS --------------------------------------------
# This script needs to be run in the Design3D computation directory

# USER INPUT: names of files
file_names = ["choke_mass_flow", "stall_efficiency", "stall_pressure_ratio", "static.fea_stress_max_vm"]

# If database use _flow_, if optimization, use _design_
dir_name = "_design_"


#---------- MAIN PROGRAM -------------------------------------------
# Get the working directory
current_dir = os.getcwd()

# Do this process for each quantity
for quantity in file_names:
    with open(quantity + "_global.dat", "w") as f:
        print("Processing files for quantity %s") %(quantity)
        # Go through all lower directories
        for folder, subfolder, files in os.walk(current_dir):
            for filename in files:
                # Open the quantity file and extract the quantity
                if os.path.splitext(filename)[0] == quantity:
                    infile = open(os.path.join(folder, filename), "r")
                    print("Processing %s") % os.path.join(folder, filename)
                    # Read information from filename
                    for line in infile:
                        words = line.split()
                        if words[0] == "VALUE":
                            value = words[1]
                    infile.close()
                    # Get the design number information
                    full_path = os.path.join(folder, filename).split(os.sep)
                    for item in full_path:
                        if dir_name in item:
                            design_nr = item.split("_")[2]
                            
                    try:
                        f.write("%s %s\n" %(design_nr, value))
                    except NameError:
                        print("Check the variabe dir_name. If this is a database, use _flow_ else use _design_")
                        print("The program will now exit")
                        sys.exit()
                    #if design_nr:
                    #    f.write("%s %s\n" %(design_nr, value))
                        
        print("Finished processing for quantity %s") %quantity
