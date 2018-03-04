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
# Script for extracting the statistical moments in
# FINE/Design3D from the .his file
#
# 2017/06/13 - Thanos Poulos
#
######################################################################


import os

# The script needs to be run in the computation folder
current_dir = os.getcwd()

# USER INPUT: Change this to the correct .his file
filename = "sample.his"
design_dir_name = "_design_"

names = []
try:
    with open(os.path.join(current_dir, filename), "r") as f:
        is_name_block = False
        is_design_block = False
        count = 0
        outfile = open("moments_global.dat", "w")
        for line in f:
            words = line.split()
            # Find the names of the Statistical Moments used in the computation
            if len(words) == 2:
                    if (str(words[0]) == "NI_BEGIN") and (str(words[1]) == "STATISTICS_NAMES"):
						is_name_block = True
						name  = ""
                    elif (str(words[0]) == "NI_END") and (str(words[1]) == "STATISTICS_NAMES"):
						names.append(name)
						is_name_block = False
						outfile.write("\n")
                    elif is_name_block == True:
                        if str(words[0]) == "STATISTICS":
                            name = str(words[1])
                            print("Name %s found") % name
                            outfile.write(name + " ")

            # Find the values for each design iteration
            if len(words) >= 2:
                    if (str(words[0]) == "NI_BEGIN") and (str(words[1]) == "DESIGN_SAMPLE"):
						is_design_block = True
						values  = []
                    elif (str(words[0]) == "NI_END") and (str(words[1]) == "DESIGN_SAMPLE"):
						is_design_block = False
                    elif is_design_block == True:
                        if "DESIGN_STATISTICS" in str(words[0]):
                            values = list(words[1:])
                        elif str(words[0]) == "SIMULATION_PATH":
                            if design_dir_name in str(words[1]):
                                for i in range(len(values)):
                                    outfile.write(values[i] + " ")
                                outfile.write("\n")
    outfile.close()
except IOError:
    print("[Error] The files does not exist")
    print("[Error] The program will exit")
