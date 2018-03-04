#!/bin/python
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
# Date: December 2016

#-------------- Change Log ----------------#
# 2017-02-03: Fixed a problem related to the definition of all computations
# 2017-03-13: Changed the number of cores to multiples of 24
# 2017-03-13: Reversed change due to cluster delay
# 2017-04-03: Changed the number of cores to multiples of 24
# 2017-04-19: Modified SGE scripts to account for newer versions
# 2017-05-09: Fixed modifications for newer versions (FT 12.1, FO 7.1)
# 2017-05-09: Fixed the regular expression that tests for rc versions
# 2017-07-18: Fixed double precision by default using OpenMPI and Euranus
# 2017-08-03: Added "unset OMP_NUM_THREADS" to Hexpress/Hybrid submit function to account for bug on viz04
# 2017-08-04: Changed the Intel library path for FINE/Turbo 12.1 and FINE/Open 7.1
# 2017-08-04: Changed function names in order to be more descriptive
# 2017-08-04: Deleted function for FINE/Marine. The script from the Marine team is more complete
# 2017-08-07: Created new functions for cleaning up the code and for avoiding code duplication
# 2017-08-07: Changed Hexpress/Hybrid launch command to the one used in the FINE/Design3D template
# 2017-08-07: Updated to latest local IntelMPI version for FT 12.1 and FO 7.1
# 2017-08-08: Fixed a bug that made the script go into an infinite loop in case the input for the parallel partitioner is bad (FT)
# 2017-08-08: Adapted the regular expression to include patches (e.g. 112_2)

#------------- To Do -------------#
# TO DO: Dependency definition --> Probably too complex for a command line, maybe a GUI is needed
# TO DO: Keep track of versioning of OpenMPI and IntelMPI libraries and adapt as they change

"""
Create and submit computations using SGE for FINE/Turbo, FINE/Open, FINE/Marine and
Hexpress/Hybrid

"""

import os
import sys
import subprocess
import shutil
import re

#---------------------------------------------------------
#
#        FUNCTIONS
#
#---------------------------------------------------------

def is_float(value):
	"""
	Function is_float:
			-This function is used to find if a string contains a float
		Inputs:
			- value: string
		Output:
			- Boolean
	"""
	try:
		float(value)
		return True
	except ValueError:
		return False


def major_version(version):
	"""
	Function major_version:
		- This function is used to find out the major version as well as 
		   if it is an alpha, beta or rc
		Input:
			- version: the version comes in as a string
		Outputs:
			- version_float: It returns the major version as a float
	"""
	# Check if the version is alpha, beta or rc
	# by checking if the version can be changed to a float
	# Returns false if the version contains letters
	if is_float(version) == True:
		version_float = int(float(version)/10)
	else:
		try:
			# Check for alpha or beta versions via a regular expression
			# Format: NumberLetterNumber e.g. 121b10
			r = re.compile("([0-9]+)\w+([0-9]+)")
			m = re.match(r, version)
			version_float = int(float(m.group(1))/10)
		except AttributeError:
			# if it does not match the above definition, it must be an rc
			r = re.compile("([0-9]+)([a-zA-Z]+)") 	#format:NumberLetter. Patches (e.g. 11.2-2) are not caught
			m = re.match(r, version)
			version_float = int(float(m.group(1))/10)

	return version_float


def write_numeca_settings(path, name, index, version, package, cores, sge):
	"""
	Function that writes the NUMECA settings in the sge files

	inputs:
		- path: 			path to the computation directory
		- name: 			list with the names of the computations to run
		- index: 			current index for the name list
		- version: 			NUMECA software version
		- package: 			software type (FINE/Turbo, FINE/Open, etc)
		- cores:            Number of cores used for the job
		- sge:				file object to write

	outputs:
		- The function has no outputs
	"""
    
	sge.write("#!/bin/sh\n")
	sge.write("#$ -S /bin/sh\n")
	sge.write("#$ -notify\n")
	sge.write("#$ -q compute.q\n")
	sge.write("#$ -pe orte %s\n" %(cores))
	sge.write("#$ -l exclusive=1\n")
	sge.write("#$ -N %s_%s\n" %(package.upper(),index))
	if package == "hh":
		sge.write("#$ -o %s.std -j y\n" %(os.path.join(path,name[index])))
	else:
		sge.write("#$ -o %s.std -j y\n" %(os.path.join(path,name[index],name[index])))
	sge.write("\n")

	# Write Numeca settings
	sge.write("#########################################################################\n")
	sge.write("# NUMECA Settings                                                       #\n")
	sge.write("#########################################################################\n")
	sge.write("\n")
	sge.write("NI_VERSIONS_DIR=/home/SHARED/numeca_software\n")
	sge.write("export NI_VERSIONS_DIR\n\n")
	if package == "ft":
		sge.write("NUMECA_SOFT_VERSION=%s\n" %(version))
	elif package == "fo" or package == "hh":
		sge.write("NUMECA_SOFT_VERSION=open%s\n" %(version))
	sge.write("export NUMECA_SOFT_VERSION\n\n")
	sge.write("NUMECA_DIR=${NI_VERSIONS_DIR}/fine${NUMECA_SOFT_VERSION}\n")
	sge.write("export NUMECA_DIR\n\n")
	sge.write("NUMECA_BIN=${NUMECA_DIR}/LINUX\n")
	sge.write("export NUMECA_BIN\n\n")
	sge.write("PATH=/usr/bin:${PATH}:${NI_VERSIONS_DIR}/bin\n")
	sge.write("export PATH\n\n")
	sge.write("TMP_DIR=~/.numeca/tmp/\n")
	sge.write("export TMP_DIR\n\n")
	sge.write("export NUMECA_LICENSE_FILE=${NI_VERSIONS_DIR}/COMMON/license.dat\n")
	sge.write("\n")


def write_ld_library(sge, mpi_version, version_float, package):
	"""
	Function that writes the LD_LIBRARY_PATH information to the sge file

	inputs:
		- sge:                file object to write
		- mpi_version:        Type of the MPI library: OpenMPI or IntelMPI
		- version:            NUMECA software version
		- package:            software type (FINE/Turbo, FINE/Open, etc)
	outputs:
		No outputs
	"""
	sge.write("#########################################################################\n")
	sge.write("# PATH - LD_LIBRARY_PATH\n")
	sge.write("#########################################################################\n\n\n")
	
	if mpi_version == "impi":
        	if version_float >= 12:
			sge.write('pathlist="${I_MPI_ROOT}/bin64"\n')
		else:
			sge.write('pathlist="${I_MPI_ROOT}/bin"\n')
        else:
        	sge.write('pathlist="${MPIR_HOME}/bin ${NI_VERSIONS_DIR}/bin"\n')
	
	sge.write("for item in ${pathlist} ; do\n")
	sge.write('\tif [ -n "$PATH" ] ; then\n')
    sge.write("\t\tfound=`echo :${PATH}: | grep :${item}:`\n")
    sge.write('\t\tif [ "X$found" == "X" ] ; then\n')
    sge.write('\t\t\tPATH="${item}:${PATH}"\n')
    sge.write("\t\tfi\n")
    sge.write("\telse\n")
    sge.write("\t\tPATH=${item}\n")
    sge.write("\tfi\n")
	sge.write("done\n")
	sge.write("export PATH\n")
	
	if mpi_version == "impi":
        	if (package == "ft" and version_float >= 12) or (package == "fo" and version_float >= 7):
                sge.write('libpath="${I_MPI_ROOT}/lib64 ${NUMECA_BIN}/_lib_sicc15 ${NUMECA_BIN}/_lib_sx86_64 ${NUMECA_BIN}/_lib_sx86_64dtk ${NUMECA_BIN}/install/flex64"\n\n')
        	elif (package == "ft" and version_float < 12) or (package == "fo" and version_float < 7):
            	sge.write('libpath="${I_MPI_ROOT}/lib ${NUMECA_BIN}/_lib_sicc15 ${NUMECA_BIN}/_lib_sx86_64 ${NUMECA_BIN}/_lib_sx86_64dtk ${NUMECA_BIN}/install/flex64"\n\n')
    	else:
        	sge.write('libpath="${MPIR_HOME}/lib ${NUMECA_BIN}/_lib_sicc15 ${NUMECA_BIN}/_lib_sx86_64 ${NUMECA_BIN}/_lib_sx86_64dtk ${NUMECA_BIN}/install/flex64"\n\n')
	
	sge.write("for item in ${libpath} ; do\n")
    sge.write('\tif [ -n "$LD_LIBRARY_PATH" ] ; then\n')
    sge.write('\t\tfound=`echo :${LD_LIBRARY_PATH}: | grep :${item}:`\n')
    sge.write('\t\tif [ "X$found" == "X" ] ; then\n')
    sge.write('\t\t\tLD_LIBRARY_PATH="${item}:${LD_LIBRARY_PATH}"\n')
    sge.write("\t\tfi\n")
    sge.write("\telse\n")
    sge.write("\t\tLD_LIBRARY_PATH=${item}\n")
    sge.write("\tfi\n")
	sge.write("done\n")
	sge.write("export LD_LIBRARY_PATH\n")
	sge.write("\n")


def write_mpi_settings(mpi_version, version_float, package, sge):
	"""
	Function that writes the MPI settings in the sge files

	inputs:
		- mpi_version: 		Type of the MPI library: OpenMPI or IntelMPI
		- version: 			NUMECA software version
		- package:          software type (FINE/Turbo, FINE/Open, etc)
		- sge:				file object to write

	outputs:
		- The function has no outputs
	"""
	
	# Write MPI library settings
	if mpi_version == "impi":
		# Write IntelMPI settings
		sge.write("#########################################################################\n")
		sge.write("# INTELMPI Library Settings                                             #\n")
		sge.write("#########################################################################\n")
		sge.write("\n")
	
		# Add this if the version is older than 12.1
		if (package == "ft" and version_float < 12) or (package == "fo" and version_float < 7):
			sge.write("I_MPI_ROOT=$NUMECA_BIN/_mpi/_impi5.0.3/intel64\n")
			sge.write("export I_MPI_ROOT\n\n")
			sge.write("source $I_MPI_ROOT/bin/mpivars.sh\n")
		else:
			sge.write("I_MPI_ROOT=/XF/Mpi/Intelmpi/2017.3-196/Installed/impi/2017.3.196\n")
			sge.write("export I_MPI_ROOT\n\n")
			sge.write("source $I_MPI_ROOT/bin64/mpivars.sh\n")

		sge.write("# IntelMPI allows support for different interconnects\n")
		sge.write("# tcp = standard ethernet\n")
		sge.write("# ofa = Infiniband\n")
		sge.write("# I_MPI_FABRICS=tcp\n\n")
		sge.write("I_MPI_FABRICS=ofa\n")
		sge.write("export I_MPI_FABRICS\n\n")
		sge.write("export I_MPI_MPIRUN_CLEANUP=1\n\n")
		
		if package == "ft":
            	sge.write("BIN=$NUMECA_DIR/LINUX/euranus/euranusTurbodpx86_64_impi_icc\n\n")
        	else:
            	sge.write("BIN=$NUMECA_DIR/LINUX/hexa/hexstreamdpx86_64_impi_icc\n\n")
	else:
		# Write OpenMPI settings
		sge.write("#########################################################################\n")
		sge.write("# OPENMPI Library Settings                                              #\n")
		sge.write("#########################################################################\n")
		sge.write("\n")
		
		# Check if the version is 12.1 or newer
		if (package == "ft" and version_float >= 12) or (package == "fo" and version_float >= 7):
			sge.write("MPIR_HOME=/XF/Mpi/Openmpi/1.10.4.gcc-4.8.5/Installed/\n")
		else:
			sge.write("MPIR_HOME=/XF/Mpi/Openmpi/1.6.5/Installed/\n")
        
		sge.write("export MPIR_HOME\n\n")
		sge.write("export OPAL_PREFIX=$MPIR_HOME\n")
		sge.write("ompi_options=\n")
		
		if version_float >= 12 and package == "ft":
			sge.write("BIN=${NUMECA_BIN}/euranus/euranusTurbodpx86_64_ompi_icc\n\n")
		elif version_float < 12 and package == "ft":
			sge.write("BIN=${NUMECA_BIN}/euranus/euranusTurbodpx86_64_ompi\n\n")
        	elif package == "fo":
            	sge.write("BIN=${NUMECA_BIN}/hexa/hexstreamdpx86_64_ompi\n\n")
        	elif package == "hh":
            	sge.write("export BIN=${NUMECA_BIN}/hexpress/hexpresshybridx86_64\n\n")
            	sge.write("unset OMP_NUM_THREADS\n")


def write_computation_settings(path, name, index, mpi_version, version_float, package, sge, mem=None, parpar=None):
	"""
	Function that writes the computation settings in the sge files

	inputs:
		- path:               project path
		- name:               Computations to run names
		- index:	      Index for the current computation
		- mem:                Memory definition list for FINE/Turbo
		- parpar:             Use of parallel partitioner for FINE/Turbo
		- mpi_version:        Type of the MPI library: OpenMPI or IntelMPI
		- version:            NUMECA software version
		- package:            software type (FINE/Turbo, FINE/Open, etc)
		- sge:                file object to write

	outputs:
		- The function has no outputs

	"""
	
	# Write computation settings
    sge.write("#########################################################################\n")
	sge.write("# Computation Settings & Start                                          #\n")
	sge.write("#########################################################################\n")
	sge.write("\n")
	if package == "hh":
        # Old command, could be useful to keep it here
		#sge.write('COMMAND="${MPIR_HOME}/bin/mpirun  --display-map --display-allocation ${ompi_options} -np ${NB_PROCS} ${BIN} < %s"\n' %(os.path.join(path,name[index])))
		sge.write("CONF_FILE=%s\n" %(os.path.join(path,name[index])))
		sge.write("$BIN ${CONF_FILE} -numproc ${NSLOTS} -print")
		sge.write("\n")
		sge.write("$COMMAND")
		sge.close()
    	else:
        	sge.write("RUNFILE=%s.run\n" %(os.path.join(path,name[index],name[index])))
        	sge.write("\n")
        	sge.write("STEERINGFILE=%s.steering\n" %(os.path.join(path,name[index],name[index])))
        	sge.write("\n")

        	# Check if the parallel partitioner should be used and if the automatic memory estimation will be used
        	if package == "ft":
			sge.write("NB_BALANCE=`expr $NSLOTS - 1`\n")
                	sge.write("\n")
            		if mem[0] == "1":
                		if parpar == "1":
                            sge.write("fine${NUMECA_SOFT_VERSION} -print -batch -partition -computation $RUNFILE -nproc $NB_BALANCE -nbint %s -nbreal %s\n" %(mem[1],mem[2]))
                		else:
                            sge.write("fine${NUMECA_SOFT_VERSION} -print -batch -parallel -computation $RUNFILE -nproc $NB_BALANCE -nbint %s -nbreal %s\n" %(mem[1],mem[2]))
            		else:
                		if parpar == "1":
              				sge.write("fine${NUMECA_SOFT_VERSION} -print -batch -partition -computation $RUNFILE -nproc $NB_BALANCE\n")
                		else:
               				sge.write("fine${NUMECA_SOFT_VERSION} -print -batch -parallel -computation $RUNFILE -nproc $NB_BALANCE\n")
            		sge.write("\n")
        
        	# Different commands are needed for OpemMPI and IntelMPI
        	if mpi_version == "ompi":
                sge.write("${MPIR_HOME}/bin/mpirun -np $NSLOTS $BIN $RUNFILE -steering $STEERINGFILE -print\n")
        	else:
            	if (package == "ft" and version_float >= 12) or (package == "fo" and version_float >= 7):
                	sge.write("${I_MPI_ROOT}/bin64/mpirun -np $NSLOTS $BIN $RUNFILE -steering $STEERINGFILE -print\n")
            	else:
                	sge.write("${I_MPI_ROOT}/bin/mpirun -np $NSLOTS $BIN $RUNFILE -steering $STEERINGFILE -print\n")


def submit_job(name, index, script_path):
	"""
	Function that writes the submission settings in the sge files

	inputs:
		- name:               Computations to run names (list)
		- script_path:        Path to the created SGE scripts (string)

	outputs:
		- The function has no outputs
	""" 
	print ("Launching computation: %s" %(name[index]))

    # Check python version and launch the appropriate command
    if sys.version_info[:2] <= (2, 7):
       	command_line = "qsub " + os.path.join(script_path, "launch_%s.sge" %(name[index]))
       	os.system(command_line)
    else:
       	subprocess.call(["qsub",os.path.join(script_path, "launch_%s.sge" %(name[index]))])


def launch_fine_turbo(path, name, mpi_version, version, cores, mem, parpar, package, submit):
	'''
	 Function launch_fine_turbo:
			- This function is used for FINE/Turbo
			- Creates a script path
			- Creates an sge file for each computation
			  checking for the MPI library requested
			- Submits the sge file
	'''

	script_path = os.path.join(path,"SGE_Scripts")

	if not os.path.exists(script_path):
        print (">: Creating path for SGE scripts...")
        os.makedirs(script_path)
	else:
		print (">: Path for SGE scripts exists")
		print (">: Creating SGE script(s)...")

	os.chdir(script_path)

	# Define the major version used
	version_float = major_version(version)

	# Create an SGE script for each computation to launch
	for i in range(len(name)):
		with open(os.path.join(script_path, "launch_%s.sge" %(name[i])), 'w') as sge:
            write_numeca_settings(path, name, i, version, package, cores, sge)
			write_mpi_settings(mpi_version, version_float, package, sge)
			write_ld_library(sge, mpi_version, version_float, package)
            write_computation_settings(path, name, i, mpi_version, version_float, package, sge, mem, parpar)
        if submit:
            submit_job(name, i, script_path)


def launch_fine_open(path, name, mpi_version, version, cores, package, submit):
	'''
		 Function launch_fine_open:
			- This function is used for FINE/Open
			- Creates a script path
			- Creates an sge file for each computation
			  checking for the MPI library requested
			- Runs the sge file

	'''

	script_path = os.path.join(path,"SGE_Scripts")

	if not os.path.exists(script_path):
		print (">: Creating path for SGE scripts...")
		os.makedirs(script_path)
	else:
		print (">: Path for SGE scripts exists")
		print (">: Creating SGE script(s)...")

	os.chdir(script_path)
	
	# Define the major version used
	version_float = major_version(version)

	# Create an SGE file for each computation to be launched
	for i in range(len(name)):
        	with open(os.path.join(script_path, "launch_%s.sge" %(name[i])), 'w') as sge:
                write_numeca_settings(path, name, i, version, package, cores, sge)
            	write_mpi_settings(mpi_version, version_float, package, sge)
                write_ld_library(sge, mpi_version, version_float, package)
                write_computation_settings(path, name, i, mpi_version, version_float, package, sge)
        
        	if submit:
                submit_job(name, i, script_path)


def launch_hexpress_hybrid(path, name, version, cores, package, submit, mpi_version=None):
	'''
		 Function launch_hexpress_hybrid:
			- This function is used for Hexpress/Hybrid
			- Creates a script path
			- Creates an sge file for each computation
			  checking for the MPI library requested
			- Runs the sge file

	'''

	script_path = os.path.join(path,"SGE_Scripts")

	if not os.path.exists(script_path):
		print (">: Creating path for SGE scripts...")
		os.makedirs(script_path)
	else:
		print (">: Path for SGE scripts exists")
		print (">: Creating SGE script(s)...")

	os.chdir(script_path)
	
	# Define the major version used
	version_float = major_version(version)

	# Create an SGE file for each computation to be launched
	for i in range(len(name)):
        	with open(os.path.join(script_path, "launch_%s.sge" %(name[i])), 'w') as sge:
            	write_numeca_settings(path, name, i, version, package, cores, sge)
            	write_ld_library(sge, mpi_version, version_float, package)
            	write_mpi_settings(mpi_version, version, package, sge)
            	write_computation_settings(path, name, i, mpi_version, version, package, sge)
            
        	if submit:
            		submit_job(name, i, script_path)


#---------------------------------------------------------
#
#        USER INPUTS
#
#---------------------------------------------------------
print ('')
print ('-- NUMECA SCRIPT FOR JOB SUBMISSION --')
print ('')

# Software definition
print (">: This script is available for the following options")
print ("\t ft: FINE/Turbo")
print ("\t fo: FINE/Open")
print ("\t hh: Hexpress/Hybrid")
software = raw_input(">>> Enter the software package you would like to use (ft, fo or hh): ")
while (software != "ft") and (software != "fo") and (software != "hh"):
	print (">: Incorrect argument used for the Software")
	software = raw_input(">>> Enter the software package you would like to use (ft, fo or hh): ")

# Project path definition
computation_path = raw_input(">>> Enter the directory path where the computations are [default: current directory]: ")
if computation_path == "":
	computation_path = os.getcwd()
	print(">: The project path is %s" %computation_path)
if not(os.path.isdir(computation_path)):
	print(">: The directory %s does not exist" %computation_path)
	print ("!!! The program will exit")
	raise SystemExit

# Computation definition
print (">>> Enter the computations that you would like to run separated with space [default: all computations in the project directory]: ")
print (">: For FINE/Turbo, FINE/Open and FINE/Marine, enter the computation name")
print (">: For Hexpress/Hybrid, enter the full name of the .conf file")
computation_names = raw_input()

if software == "hh":
	if computation_names == "":
		computation_name_list = [f for f in os.listdir(computation_path) if f.endswith('.conf')]
	else:
		computation_name_list = computation_names.split()
		if not(all(f.endswith('.conf') for f in computation_name_list)):
			print (">: For Hexpress/Hybrid, the computation has to be the .conf file")
			print ("!!! The program will exit")
			raise SystemExit
else:
    	extension = ".run"
	
	all_computations = [subdir for subdir in os.walk(computation_path).next()[1] if any(subfile.endswith(extension) for subfile in os.listdir(os.path.join(computation_path,subdir)))]
	
	if computation_names == "":
		computation_name_list = all_computations
	else:
		computation_name_list = computation_names.split()
		if any(f not in all_computations for f in computation_name_list):
			print (">: At least one computation does not exist in the project")
			print ("!!! The program will exit")
			raise SystemExit
if len(computation_name_list) == 0:
	print (">: No computation file in the project directory")
	print ("!!! The program will exit")
	raise SystemExit

print(">: The following computations will be run: ")
for comp in computation_name_list:
	print(comp)


# Version definition
version  = raw_input(">>> Version (enter only the numbers of the version, not open or marine): ")
while version == "":
	print (">: There was no version entered")
	version  = raw_input(">>> Version (enter only the numbers of the version, not open or marine): ")

# Number of cores definition
if software == "hh":
	nCores = 24
else:
	nCores = raw_input(">>> Number of cores (multiple of 24): ")
	while int(nCores)%24 != 0:
		print (">: Number of cores is not a multiple of 24")
		nCores = raw_input(">>> Number of cores (multiple of 24): ")

# MPI definition
if software != "hh":
	mpi = raw_input(">>> Enter the mpi type you want to use (ompi for OpenMPI or impi for IntelMPI): ")
	while mpi != "impi" and mpi != "ompi":
		print (">: Incorrect argument used for the MPI Library")
		mpi = raw_input(">>> Enter the mpi type you want to use (ompi for OpenMPI or impi for IntelMPI):")



# Memory estimation and parallel partitioner - only for FINE/Turbo
if software == "ft":
	memFT = []
	memFT.append(raw_input(">>> Do you want to set the memory requirements? (1 for yes, 0 for no): "))
	while memFT[0] != "0" and memFT[0] != "1":
		print (">: You have to enter 0 for no or 1 for yes: ")
		memFT.append(raw_input(">>> Do you want to set the memory requirements? (1 for yes, 0 for no): "))

	if memFT[0] == "1":
		memFT.append(raw_input(">>> Enter the number of ints: "))
		memFT.append(raw_input(">>> Enter the number of reals: "))

	parpar =  raw_input(">>> Do you want to use the parallel partitioner (1 for yes, 0 for no): ")
	while parpar != "0" and parpar != "1":
		print (">: You have to enter 0 for no or 1 for yes: ")
		parpar = raw_input(">>> Do you want to use the parallel partitioner (1 for yes, 0 for no): ")

#Ask  the user if they want to delete the SGE scripts
#delete = raw_input(">>> Do you want to delete the SGE scripts at the end? (y/n): ")

# Ask the user if they would like to submit the jobs
if raw_input(">>> Would you like to submit the SGE scripts [default: SGE scripts will be submitted] (y/n): ") == "n":
    	submit = False
else:
    	submit = True

#---------------------------------------------------------
#
#        MAIN PROGRAM
#
#---------------------------------------------------------

print (">: SGE files will be created for the following computations:")

if software == "ft" or software == "fo":
	for i in computation_name_list:
		check_filename = os.path.join(computation_path,i,i) + ".run"
		if os.path.isfile(check_filename):
			print ("\t%s" %(i))
		else:
			print (">: The computation %s does not exist" %(i))
			print (">: Skipping computation %s" %(i))
else:
	for i in computation_name_list:
		check_filename = os.path.join(computation_path,i)
		if os.path.isfile(check_filename):
			print ("\t%s" %(i))
		else:
			print (">: The computation %s does not exist" %(i))
			print (">: Skipping computation %s" %(i))

print (">: The number of computations to be launched is: %s" %(len(computation_name_list)))

if software == "ft":
	print (">: The software to be used is FINE/Turbo")
elif software == "fo":
	print (">: The software to be used is FINE/Open")
elif software == "hh":
	print (">: The software to be used is Hexpress/Hybrid")

print (">: The version is %s" %version)

if software != "hh":
	if mpi == "impi":
		print (">: The MPI Library is IntelMPI")
	elif mpi == "ompi":
		print (">: The MPI Library is OpenMPI")

print (">: The number of cores is: %s" %nCores)

if software == "ft":
    launch_fine_turbo(computation_path, computation_name_list, mpi, version, nCores, memFT, parpar, software, submit)
elif software == "fo":
    launch_fine_open(computation_path, computation_name_list, mpi, version, nCores, software, submit)
elif software == "hh":
	launch_hexpress_hybrid(computation_path, computation_name_list, version, nCores, software, submit)

# Delete all SGE scripts
# if delete == "y":
# 	print (">: The SGE scripts will be deleted")
#	shutil.rmtree(script_path)

if submit:
	print(">: All computations have been launched successfully")
else:
	print(">: The SGE files have been saved successfully")

print ('')
print ('-- NUMECA SCRIPT FOR JOB SUBMISSION USING SGE ENDED SUCCESSFULLY--')
print ('')
