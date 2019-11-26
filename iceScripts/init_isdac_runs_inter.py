#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 13:29:01 2019

@author: aholaj
"""
import os
import sys
sys.path.insert(0, os.path.join(os.environ["SCRIPT"], "submitScripts"))
import submit_uclales_salsa_methods as submitMet


import getopt
import f90nml as nml

global debug, vmF


debug = False
override = True

# auxiliary variables
vmF  = "_"


###################################
###                             ###
### input parameters CHANGEABLE ###
###                             ###
###################################

# directories
inputD           = os.environ["ISDAC"]
outputrootD      = os.environ["LUSTRE"]
binD             = os.environ["BIN"]

radiationinputD = binD

#filenames in inputD directory
soundinF  = "sound_in3.5"
namelistF = "NAMELIST_inter"
# binary name in binD directory
exeF = "les.mpi.IceDevel_Jaakko_Isdac_Puhti.IceV1.0.puhtiintel.fast"

# parameters used to determine output location
case_name = "isdac"
lvl = 5
dim = 3

# supercomputer parameters
nproc = 64 # number of processors
### command line arguments
argv = sys.argv[1:]
try:
    opts, args = getopt.getopt(argv,"h:",[ \
                                          "inputD=",\
                                          "outputrootD=",\
                                          "binD=",\
                                          "radiationinputD=",\
                                          "soundinF=",\
                                          "namelistF=",\
                                          "exeF=",\
                                          "case_name=",\
                                          "lvl=",\
                                          "dim=",\
                                          "nproc="])
except getopt.GetoptError:
   print('ERROR, usage: .py -i <inputfile> -o <outputfile>')
   sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print('.py -i <inputfile> -o <outputfile>')
        sys.exit()
    elif opt in ("--inputD"):
        inputD = arg
    elif opt in ("--outputrootD"):
        outputrootD = arg
    elif opt in ("--binD"):
        binD = arg
    elif opt in ("--radiationinputD"):
        radiationinputD = arg
    elif opt in ("--soundinF"):
        soundinF = arg
    elif opt in ("--namelistF"):
        namelistF = arg
    elif opt in ("--exeF"):
        exeF = arg
    elif opt in ("--case_name"):
        case_name = arg
    elif opt in ("--lvl"):
        lvl = arg
    elif opt in ("--dim"):
        dim = arg
    elif opt in ("--nproc"):
        nproc = arg

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
    timeList = [8]
else:
    timeList = [8,48]


for hours in timeList:

    if hours == 24:
        walltime = "36:00:00"
    else:
        walltime = "24:00:00"
    print(" ")
    print(" ")

    postfix = vmF.join( ["iceD", "inter", str(hours) + "h" ] ) # AS INPUT

    # derived
    name = vmF.join( [ prefix, postfix ] )
    outputD = os.path.join( outputrootD, name )

    ### modify namelist values
    model_nml = "model"
    nmlbaseDict[model_nml]['filprf'] = name
    nmlbaseDict[model_nml]['hfilin'] = name + ".rst"
    nmlbaseDict[model_nml]['timmax'] = hours*3600.

    salsa_nml = "salsa"


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
    submitMet.createSBATCHJobScript( jobname = vmF.join( ["LES", "i", str(hours) + "h" ] ), nproc = nproc, WT = walltime, rundir = outputD, exe = exeF)
    #######################################################################
