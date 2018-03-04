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


'''
Script to import a computation using selective open by using block names

Author: Thanos Poulos
'''

import os
import subprocess
import sys

#------------------ INPUT DATA ------------------------------------------------

# Path to the mesh file
# This needs to be pointing to an .igg file
igg_path = "DemoCase8.igg"

# List containing the block names that you want to import
block_names = ["row_2_flux_1_Main_Blade_downStream",
               "row_2_flux_1_Main_Blade_outlet",
               "row_2_flux_1_Main_Blade_upStream",
               "row_2_flux_1_Main_Blade_inlet",
               "row_2_flux_1_Main_Blade_skin",
               "row_2_flux_1_Main_Blade_up",
               "row_2_flux_1_Main_Blade_down",
               "row_2_flux_1_Main_Blade_shroudgap1",
               "row_2_flux_1_Main_Blade_shroudgap2"]

# If you just want to open the project and not do anything else, leave this empty
# If it is not empty, it should point to a CFView macro which will copy 
# and will only change the FileOpenProjectSelection command
macro = ''

### There is additional user input needed on line 259
# The command variable needs to be changed

#------------------ END INPUT DATA --------------------------------------------

# Functions
#----------

def igg_get_block_names(project_path, delete_python_script):
    '''
    Function that gets the block names from igg_get_block_names
    
    Creates a temporary dat file that contains the names of the blocks
    in the correct order (one name per line). It also creates a python
    script. There is a prompt to delete the file or not in the end. 
    
    Input: Full absolute project path pointing to an IGG file
    
    Output: Temporary dat file containing block names
    '''
    # Get current directory
    cdir = os.getcwd()
    # temp variables
    temporary_file = "outfile = " + "'" + cdir + "/" + "blf.dat" + "'"
    path = "path = " + "'" + project_path + "'"
    
    # Create IGG python script
    print(">>> Creating IGG python script <<<")
    with open("igg_script.py", 'w') as iggpy:
        iggpy.write("script_version(2.2)\n")
        iggpy.write("import os\n")
        iggpy.write(path)
        iggpy.write("\n")
        iggpy.write(temporary_file)
        iggpy.write("\n")
        iggpy.write("open_igg_project(path)\n")
        iggpy.write("block_list = []\n")
        iggpy.write("nb = num_of_blocks()\n")
        iggpy.write("print('>>> There are %s blocks in %s <<')%(nb,os.path.basename(path))\n")
        iggpy.write("print('>>> Creating block name list <<<')\n")
        iggpy.write("i = 1\n")
        iggpy.write("with open(outfile, 'w') as temp:\n")
        iggpy.write("\twhile i<=nb:\n")
        iggpy.write("\t\ttemp.write(block(i).get_name())\n")
        iggpy.write("\t\ttemp.write('\\n')\n")
        iggpy.write("\t\ti += 1\n")
        iggpy.write("print('>>> The block name list has been written in blf.dat <<<')\n")
        iggpy.write("print('>>> Closing IGG session <<<')")
        
    print(">>> IGG python script created ")
    
    print(">>> Running IGG puthon script ")
    
    subprocess.call(["igg111", "-batch", "-script", "igg_script.py"])
    
    print(">>> IGG python script finished successfully ")
    
    if delete_python_script == "y":
        os.remove("igg_script.py")
        print(">>> The IGG python script has been deleted ")


def get_block_indices_from_names(input_list,delete_block_names_file):
    '''
    Function that reads the file with the block names and puts them into a list.
    The indices are accessed through the list.
    
    The file name needs to be blf.dat (of course this is not optimal and it can
    be changed in the future
    
    Also,it creates the command to pass to the run_cfview function
    FileOpenProjectSelection
    
    Input: input list with the require block names
    
    Output: string with the block indices to be used in the command
    '''
    
    with open("blf.dat", 'r') as f:
        block_list = f.read().splitlines()
    
    index_list = []
    for item in input_list:
        index_list.append(block_list.index(item)+1)
    
    # sort the list
    index_list.sort()
    
    # Create a string from the index list to be inpu in the command
    indices = ' '.join(str(x) for x in index_list)
    
    # Add single quotes to conform to CFView format
    indices = "'" + indices + "'"
    
    print(">>> The block indices have been extracted from the block names ")
    
    # Clean the auxiliary block name file if needed
    if delete_block_names_file == "y":
        os.remove("blf.dat")
        print(">>> The auxiliary block name file has been deleted ")
    
    return indices


def run_cfview(command, macro, delete_cfview_file):
    '''
    Function that runs CFView
    
    A CFView python file is used as input. If there is no python file, a variable
    should be defined as an empty string. If the python file exists, it will be read,
    written along with the selective open command and run in batch in CFView.
    
    The macro path should be absolute, but it can be the file name if in the same
    directory.
    
    If the variable macro is empty, only the selective open command will be opened
    in CFView in normal mode.
    
    The selective open command can be changed.
    
    Input: CFView macro path
    
    Output: None
    '''
    
    print(">>> Creating the CFView macro ")
    
    if macro:
        if not os.path.isfile(macro):
            print("*** Error: The CFView macro does not exist ***")
            print("*** The program will now exit ***")
            sys.exit()
        
        with open(macro, 'r') as infile, open("cfview_script.py", "w") as outfile:
            # Read and write the first line (CFViewBackward(912))
            outfile.write(infile.readline())
            outfile.write("\n")
            outfile.write(command)
            outfile.write("\n")
            
            # Read and write the rest of the file
            for line in infile:
                # Check if the FileOpenProjectSelection already exists
                if line.startswith("FileOpenProjectSelection"):
                    continue
                
                outfile.write(line)
        
        
        print(">>> CFView macro created successfully ")
        print(">>> Running CFView macro ")
        
        # Run the CFView process
        subprocess.call(["cfview111", "-macro", "cfview_script.py", "-batch", "-print"])
    
    else:
        with open("cfview_script.py", "w") as outfile:
            # Read and write the first line (CFViewBackward(912))
            outfile.write("CFViewBackward(912)")
            outfile.write("\n")
            outfile.write(command)
            outfile.write("\n")
            
        print(">>> CFView macro created successfully ")
        print(">>> Running CFView macro ")
        
        # Run the CFView process
        subprocess.call(["cfview111", "-macro", "cfview_script.py", "-print"])
    
    # Clean the CFView macro if needed
    if delete_cfview_file == "y":
        os.remove("cfview_script.py")
        print(">>> The auxiliary CFView macro has been deleted ")


            
# Main Program
#--------------

# Check to see if the input exists
while not os.path.isfile(igg_path):
    print("*** Error: The mesh file does not exist ***")
    igg_path = raw_input("<> Please input the mesh file (.igg) full path: ")

# Check to keep auxiliary python file
delete_python_script = raw_input("<> Do you want the auxiliary IGG python script to be deleted at the end? [y,n]: ")

# Check to keep auxiliary block name file
delete_block_names_file = raw_input("<> Do you want the auxiliary block name file to be deleted at the end? [y,n]: ")

# Check to keep auxiliary CFView macro
delete_cfview_file = raw_input("<> Do you want the auxiliary CFView macro to be deleted at the end? [y,n]: ")

# Call the IGG script
igg_get_block_names(igg_path,delete_python_script)

# Call the index search function
indices = get_block_indices_from_names(block_names, delete_block_names_file)

################## USER INPUT ###############################
# Change the FileOpenProjectSelection command here
command = "FileOpenProjectSelection('DemoCase_8_000_FMMP.run' ,'blocklist',%s ,%s ,'loadqnt')" % (len(block_names), indices)

################## END USER INPUT ###########################

# Call the CFView function
run_cfview(command, macro, delete_cfview_file)

print(">>> The script has been successfully run ")
