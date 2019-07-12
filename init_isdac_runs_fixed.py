#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 13:29:01 2019

@author: aholaj
"""
import submit_uclales_salsa_methods as submitMet
import PythonMethods as pm

import sys
import os
import getopt
import f90nml as nml
import json

global debug, vmF




# auxiliary variables
vmF  = "_"

############################################
###                                      ###
### input parameters read from json file ###
###                                      ###
############################################

#default value for json file (can be given as command line argument
jsonfile ="fixed_runs.json" # CHANGE THIS DEBUGKEBAB BEFORE COMMIT

# read command line arguments
try:
    opts, args = getopt.getopt(sys.argv,"h:",[ \
                                          "jsonfile="])
except getopt.GetoptError:
   print('ERROR, usage: .py --i=<input json file>')
   sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print('.py -i <inputfile> -o <outputfile>')
        sys.exit()
    elif opt in ("--jsonfile"):
        jsonfile = arg

# read json file
with open ("fixed_runs.json") as jsonfilu:
    jsondata = json.load(jsonfilu)

debug = pm.stringToBoolean( jsondata["debug"] )
override = pm.stringToBoolean( jsondata["override"] )

###########################
# read inputset from json #
###########################
jsonSet = "inputset"
####################


##############################
# read directories from json #
##############################
jsonSubSet = "directories"
##########################

useEnvVarBool = pm.stringToBoolean( jsondata[  jsonSet  ][ jsonSubSet  ][ "useEnvVarBool" ] ) # if directory parameters are given as environment variables

inputD          = jsondata[  jsonSet  ][  jsonSubSet  ][ "inputD" ]
outputrootD     = jsondata[  jsonSet  ][  jsonSubSet  ][ "outputrootD" ]
binD            = jsondata[  jsonSet  ][  jsonSubSet  ][ "binD" ]
radiationinputD = jsondata[  jsonSet  ][  jsonSubSet  ][ "radiationinputD" ]

if useEnvVarBool:
    inputD          = os.environ[ inputD ]
    outputrootD     = os.environ[ outputrootD ]
    binD            = os.environ[ binD ]
    radiationinputD = os.environ[ radiationinputD ]

########################
# read files from json #
########################
jsonSubSet = "files"
####################

#filenames in inputD directory
soundinF  = jsondata[  jsonSet  ][  jsonSubSet  ][ "soundinf" ]
namelistF = jsondata[  jsonSet  ][  jsonSubSet  ][ "namelistF" ]
# binary name in binD directory
exeF = jsondata[  jsonSet  ][  jsonSubSet  ][ "exeF" ]

###################################
# read outputparameters from json #
###################################
jsonSubSet = "outputparameters"
###############################

case_name = jsondata[  jsonSet  ][  jsonSubSet  ][ "case_name" ]
lvl = jsondata[  jsonSet  ][  jsonSubSet  ][ "lvl" ]
dim = jsondata[  jsonSet  ][  jsonSubSet  ][ "dim" ]

###########################################
# read supercomputer parameters from json #
###########################################
jsonSubSet = "supercomputerparameters"
###############################
#
nproc = jsondata[  jsonSet  ][  jsonSubSet  ][ "nproc" ] # number of processors



######################################
######################################
######################################


# variables derived from input parameters
nmlbaseV = os.path.join( inputD, namelistF )
soundinV = os.path.join( inputD, soundinF )
exeV     = os.path.join( binD, exeF )

prefix   = vmF.join(["case", case_name, "LVL" + str(lvl), str(dim) + "D"])

# read namelist as dictionary
nmlbaseDict = nml.read(nmlbaseV)


if debug:
    iceList  = [0]
    timeList = [8]
else:
    iceList  = [0,1,2,3,4,5,6]
    timeList = [8,24]

for iceConc in iceList:
    for hours in timeList: #[28800., 86400.]:

        if iceConc in [0,5,6] and hours == 24:
            continue

        if hours == 24:
            walltime = "36:00:00"
        else:
            walltime = "24:00:00"
        print(" ")
        print(" ")

        iceBase = 769.
        postfix = vmF.join( ["iceD", str(iceConc), str(hours) + "h" ] ) # AS INPUT

        # derived
        name = vmF.join( [ prefix, postfix ] )
        outputD = os.path.join( outputrootD, name )

        ### modify namelist values
        model_nml = "model"
        nmlbaseDict[model_nml]['filprf'] = name
        nmlbaseDict[model_nml]['hfilin'] = name + ".rst"
        nmlbaseDict[model_nml]['timmax'] = hours*3600.

        salsa_nml = "salsa"
        nmlbaseDict[salsa_nml]["fixinc"] = iceConc*iceBase

        #######################################################################
        ###### radiation sounding
        radiationP, radiationV, radiationD, radoutputD, radB = submitMet.radiationSounding( nmlbaseDict, radiationinputD, outputD )

        # dir making
        submitMet.makeDirectories( outputD = outputD, radB = radB, radoutputD=radoutputD )

        # namelist file writing
        submitMet.writeNamelist( nmlbaseDict, outputD )

        # copying files
        submitMet.copyFiles(exeV, soundinV, outputD )

        # create bash job script
        submitMet.createPBSJobScript( jobname = vmF.join( ["LES", str(iceConc), str(hours) + "h" ] ), nproc = nproc, WT = walltime, rundir = outputD, exe = exeF)
        #######################################################################
