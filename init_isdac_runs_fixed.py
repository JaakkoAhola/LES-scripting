#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 13:29:01 2019

@author: aholaj
"""
import submit_uclales-salsa-methods as submitMet
import os
import getopt
import f90nml as nml
import json

from subprocess import call
from shutil import copy2

global debug


debug = False
override = True

# auxiliary variables
vmD = "/"
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
namelistF = "NAMELIST_fixedinc"
# binary name in binD directory
exeF = "les.mpi.IceDevel_Jaakko_Isdac.IceD.intel.fast"

# parameters used to determine output location
case_name = "isdac"
lvl = 5
dim = 3

# variables derived from input parameters
nmlbaseV = vmD.join([inputD, namelistF])
soundinV = vmD.join([inputD, soundinF])
exeV     = vmD.join([binD, exeF])

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
        outputD = vmD.join( [outputrootD, name] )

        ### modify namelist values
        model_nml = "model"
        nmlbaseDict[model_nml]['filprf'] = name
        nmlbaseDict[model_nml]['hfilin'] = name + ".rst"
        nmlbaseDict[model_nml]['timmax'] = hours*3600.

        salsa_nml = "salsa"
        nmlbaseDict[salsa_nml]["fixinc"] = iceConc*iceBase

        ###### radiation sounding
        try:
            radiationP = nmlbaseDict[model_nml]["radsounding"]
            radiationV = vmD.join([radiationinputD, radiationP])

            radiationD = os.path.dirname(radiationP)
            radoutputD =  vmD.join( [outputD, radiationD] )


            radB = True
        except KeyError:
            radB = False
            pass


        # print namelist
        print(json.dumps( nmlbaseDict, separators = (",", "=")) )

        # dir making
        makedirsL = ['mkdir','-p', outputD]

        if radB:
            makedirsL.append(radoutputD)

        if debug:
            print(makedirsL)
        else:
            call(makedirsL)


        # namelist file writing
        namelistNewV = vmD.join([outputD,"NAMELIST" ])
        try:
            nmlbaseDict.write( namelistNewV )
        except OSError:
            try:
                if os.path.isfile(namelistNewV) and override:
                    os.remove(namelistNewV)
                    nmlbaseDict.write( namelistNewV )
            except OSError:
                print("The creation of new namelist did not succeed")


        # copying files
        if debug:
            print(exeV, soundinV)
        else:
            copy2(exeV, outputD)
            copy2(soundinV, vmD.join([outputD,"sound_in"]))

        if radB:
            copy2( radiationV, vmD.join([outputD, radiationP]) )

        # create bash job script
        jobname = vmF.join( ["LES", str(iceConc), str(hours) + "h" ] )
        nproc   = 64
        nodeNPU= 28
        WT = walltime
        email="jaakko.ahola@fmi.fi"
        rundir = outputD
        exe = exeF

        createBashJobScript(jobname = jobname, nproc = nproc, nodeNPU = nodeNPU, WT = WT, email = email, rundir = rundir, exe = exe)
