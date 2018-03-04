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

import os
import sys
import fileinput
import string
import shutil
import subprocess
from datetime import datetime


print ''
print '-- FINE/TURBO SCRIPT FOR PROJECT BACKUP --'
print ''

path = os.getcwd()
project_file = 'none'
list_files = []
list_files = os.listdir(path)
for files in list_files:
	if files[-4:] == '.iec':
		project_file = files
		print ' > Project to backup: '+str(project_file[:-4])
		break

if project_file == 'none':
	print ' > No project file found in the current path. Script is ending.'
else:
	# request for archive
	compress_q = raw_input(' > Do you want to compress? (y/n) ')
	while compress_q != 'y' and compress_q != 'n':
		print ' >> Please answer y or n'
		compress_q = raw_input(' > Do you want to compress? (y/n) ')

	# how to compress
	archive_tmp = '0'
	delete = 'n' #no deleting
	if compress_q == 'y':
		archive1 = raw_input(' > Do you want to compress with .zip (1) or .tar.gz (2)? (1 or 2) ')
		while archive1 != '1' and archive1 != '2':
			print ' >> Please answer 1 or 2'
			archive1 = raw_input(' > Do you want to compress with .zip (1) or .tar.gz (2)? (1 or 2) ')
		if archive1 == '1':
			archive_tmp = '1' #will be .zip

		# do we delete backup folder
		delete = raw_input(' > Do you want to delete the backup folder after compression? (y/n) ')
		while delete != 'y' and delete != 'n':
			print ' >> Please answer y or n'
			delete = raw_input(' > Do you want to delete the backup folder after compression? (y/n) ')

	# Find time and date for the project name
	i = datetime.now()
	info = i.strftime('_%Y-%m-%d_%Hh-%Mm-%Ss')
	backup_file = project_file[:-4]+info

	# Find and copy the needed files
	#if os.path.exists(os.path.join(os.getcwd(),backup_file)):
		#os.makedirs(os.path.join(os.getcwd(),backup_file))
	for files in list_files:
		if files == "_mesh":
			mesh_dir = os.path.join(os.getcwd(),backup_file,files)
			print (mesh_dir)
			shutil.copytree(os.path.join(os.getcwd(),files),mesh_dir)

	shutil.copy(project_file,os.path.join(os.getcwd(),backup_file))

	os.chdir(os.path.join(os.getcwd(),backup_file,mesh_dir))
	list_files_mesh = os.listdir(os.path.join(os.getcwd(),files,backup_file,mesh_dir))
	for files in list_files_mesh:
		if not files.endswith(".trb") and not files.endswith(".geomTurbo") and not ((files.endswith(".geomTurbo.xmt_txt") or files.endswith(".geomTurbo.X_T"))):
			os.unlink(os.path.join(mesh_dir,files))

	os.chdir(os.path.expanduser('../..'))
	if archive_tmp == '0' and compress_q == 'y':
		os.system('tar cvfz '+backup_file+'.tar.gz '+ backup_file)
	elif archive_tmp == '1' and compress_q == 'y':
		command =  "zip -r %s %s/" % (backup_file,backup_file)
		#subprocess.call(command)
		os.system(command)
	if delete == 'y':
		os.system('rm -fr '+backup_file)



	print ''
	print ' > Backup is over'
	print ''
