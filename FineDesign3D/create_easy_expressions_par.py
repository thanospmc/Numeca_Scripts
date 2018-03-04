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
##############################################################################



__version__ = '0.1'  
__author__ = 'Thanos Poulos'
__license__ = 'MIT'


######################################################################
#
# Script creating very simple expressions on a par file
#
# 2017/06/21 - Thanos Poulos
#
######################################################################


import os

# The scrip must be launched at the directory of the par file that needs changing
current_dir = os.getcwd()

#---------- User defined parameters -------------------------------
# Par file name that needs changing. The extension has to be included
file_name = "sample.par"

# No support for spaces in the name
new_file = file_name.split(".")[0] + "_new." + file_name.split(".")[1]

# Dictionary with the new parameters as keys and the list of existing parameters to change
# The lists should contain either the full names of the parameters or the partial name
expressions_dict = {
    "THICKNESS" : ["HALF_THICKNESS"],
    "GAP_UNCERTAINTY" : ["SHROUD_GAP_WIDTH"],
    "OPERATIONAL_MULTI" : []
    }

# Ranges of the new uncertain parameters to set
unc_par_range = ["1","0.5", "1.5"]


#--------- Main Program --------------------------------------------
# open new file
print("Starting Process")

n = open(new_file, "w")

with open(file_name, "r") as f:
    # Parsing the .par file -- Format in the bottom
    # File format used from version 11.2 or newer
    is_param_block = False
    is_required_param = False
    is_user_param = False
    count = 0
    for line in f:
        words = line.split()
        if (len(words) == 2):
            if (str(words[0]) == "NI_BEGIN") and (str(words[1]) == "USER_PARAMETERS"):
                is_user_param = True
                n.write(line)
            elif (str(words[0]) == "NI_END") and (str(words[1]) == "USER_PARAMETERS"):
                is_user_param = False
                n.write(line)
            elif is_user_param:
                if (str(words[0]) == "NUMBER_OF_PARAMETERS"):
                    num_param = int(words[1])
                    num_param += len(expressions_dict)
                    line_new = words[0] + "\t" + "+" + str(num_param) + "\n"
                    n.write(line_new)
                else:
                    if count < len(expressions_dict):
                        for key in expressions_dict:
                            n.write("NI_BEGIN\t PARAMETER\n")
                            n.write("NAME\t" + key + "\n")
                            n.write("LIMIT_MIN\t -1000000000\n")
                            n.write("LIMIT_MAX\t 1000000000\n")
                            n.write("VALUE\t" + unc_par_range[0] + "\n")
                            n.write("VALUE_MIN\t" + unc_par_range[1] + "\n")
                            n.write("VALUE_MAX\t" + unc_par_range[2] + "\n")
                            n.write("VALUE_REF\t 1\n")
                            n.write("NB_LEVELS\t +2\n")
                            n.write("QUANTITY_TYPE\t VALUE\n")
                            n.write("UNCERTAIN\t FALSE\n")
                            n.write("NI_END\t PARAMETER\n")
                            count += 1
                        else:
                            n.write(line)
                        is_user_param = False
            else:
                if (str(words[0]) == "NI_BEGIN") and (str(words[1]) == "PARAMETER"):
                    is_param_block = True
                    name  = ""
                    value = ""
                    quantity_type = "EXPRESSION"
                    n.write(line)
                elif (str(words[0]) == "NI_END") and (str(words[1]) == "PARAMETER"):
                    is_param_block = False
                    is_required_param = False
                    n.write(line)
                elif is_param_block == True:
                    if str(words[0]) == "NAME":
                        name = str(words[1])
                        for key in expressions_dict:
                            for dict_value in expressions_dict[key]:
                                if dict_value in name:
                                    is_required_param = True
                                    key_name = key
                        line_new = words[0] + "\t" + name + "\n"
                        n.write(line_new)
                    elif str(words[0]) == "VALUE":
                        if is_required_param:
                            value = str(words[1])
                            line_new = words[0] + "\t" + value + "\n"
                            n.write(line_new)
                        else:
                            n.write(line)
                    elif str(words[0]) == "QUANTITY_TYPE":
                        if is_required_param:
                            line_new = words[0] + "\t" + quantity_type + "\n"
                            n.write(line_new)
                        else:
                            n.write(line)
                    elif str(words[0]) == "UNCERTAIN":
                        n.write(line)
                        if is_required_param:
                            # write the new line
                            # Example:
                            #EXPRESSION                     "0.0003*GAP_UNCERTAINTY"
                            line_new = 'EXPRESSION\t "' + value + '*' + key_name + '"\n' 
                            n.write(line_new)
                    else:
                        n.write(line)
                else:
                    n.write(line)
        else:
            n.write(line)
                
n.close()

print("Process finished")

'''
NI_BEGIN	PARAMETER
         NAME                           GAP_UNCERTAINTY
         PARAMETRIC_TYPE                DOUBLE
         LIMIT_MIN                      -1000000000
         LIMIT_MAX                      1000000000
         VALUE                          1
         VALUE_MIN                      1
         VALUE_MAX                      1
         VALUE_REF                      1
         NB_LEVELS                      +2
         QUANTITY_TYPE                  VALUE
         UNCERTAIN                      FALSE
      NI_END	PARAMETER
'''
'''
NI_BEGIN	PARAMETER
            NAME                           SHROUD_GAP_WIDTH
            PARAMETRIC_TYPE                DOUBLE
            LIMIT_MIN                      0
            LIMIT_MAX                      1000000000
            VALUE                          0.0003
            VALUE_MIN                      0.0003
            VALUE_MAX                      0.0003
            VALUE_REF                      0.0002
            NB_LEVELS                      +2
            QUANTITY_TYPE                  EXPRESSION
            UNCERTAIN                      FALSE
            EXPRESSION                     "0.0003*GAP_UNCERTAINTY"
         NI_END	PARAMETER
'''
