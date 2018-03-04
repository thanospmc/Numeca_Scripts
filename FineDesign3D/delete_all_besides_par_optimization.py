#!/usr/bin/python

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
# Script for deleting all files besides the ones with specific extensions 
#
# 2017/07/13 - Thanos Poulos
#
######################################################################


import os

# This script needs to be run in _opt directory of the Design3D computation directory

# USER INPUT: extensions of files to delete
extensions = [".par"]

# Names of the directories that contain the files we want to delete
# Be careful if _mesh is part of the full path of the directory
dir_names = ["_design"]

current_dir = os.getcwd()

# Do this process for each extension in every directory
for ext in extensions:
    for name in dir_names:
        print("[Info] Deleting all files in %s folders besides %s files") % (name, ext)
        # Go through all lower directories
        for folder, subfolder, files in os.walk(current_dir):
            for filename in files:
                full_path = os.path.join(folder, filename)
                if (not filename.endswith(ext)) and (name in full_path):
                    print("Deleting %s") % full_path
                    os.unlink(full_path)
            
            if (not os.listdir(folder)):
                print ("Deleting directory %s") % folder
                os.rmdir(folder)
        print("[Info] Finished deleting all files in %s folders besides %s files") % (name, ext)
