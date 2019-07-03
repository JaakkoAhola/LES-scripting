#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 13:08:29 2019

@author: aholaj
"""
import os
import json
from subprocess import call
from shutil import copy2
global vmD, model_nml
import f90nml as nml
vmD = "/"
model_nml = "model"

def radiationSounding(nmlbaseDict, radiationinputD, outputD):
    # input:
    #
    # nmlbaseDict: dictionary variable that is the namelist
    # radiationinputD: input root directory of radiation sounding file
    # outputD: output directory
    #
    # output:
    # radiationP: relative path of radiation sounding in outputfolder = same as value in namelist
    # radiationV: absolute path of radiation sounding file
    # radiationD: subfolder of radiation souding file
    # radoutputD: absolute path of radiation soudinng file in output folder
    # radB: if radiation sounding is used
    # 
    # 
    
    
    try:
        radiationP = nmlbaseDict[model_nml]["radsounding"]
        radiationV = vmD.join([radiationinputD, radiationP])
        
        radiationD = os.path.dirname(radiationP)
        radoutputD = vmD.join( [outputD, radiationD] )
        
        radB = True
        
    except KeyError:
        radiationP = ""
        radiationV = ""
        
        radiationD = ""        
        radoutputD = ""
        
        radB = False
        
        pass

    return radiationP, radiationV, radiationD, radoutputD, radB

def makeDirectories(outputD, radB = False, radoutputD = "datafiles" ):
    makedirsL = ['mkdir','-p', outputD]

    if radB:
        makedirsL.append(radoutputD)
        
    call(makedirsL)

def writeNamelist(nmlbaseDict, outputD, override = True, printtaa=True):
    # input:
    #
    # nmlbaseDict: dictionary variable that is the namelist
    # outputD: output directory
    # override: if file exists, override and write over it
    # printtaa: if you want to print the namelist dictionary variable

    if printtaa:
        print(json.dumps( nmlbaseDict, separators = (",", "=")) )

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
            
def writePatchNamelist(nmlbaseDict, nmlPatch, outputD, override = True):
    # input:
    #
    # nmlbaseDict: dictionary variable that is the namelisti
    # nmlPatch: patch to the namelist
    # outputD: output directory   

        namelistNewV = vmD.join([outputD,"NAMELIST" ])
        if os.path.isfile(namelistNewV) and override:
            nml.patch( nmlbaseDict, nmlPatch, namelistNewV )

def copyFiles(exeV, soundinV, outputD, radB=False, radiationV = "", radiationP=""):
    # input:
    #
    # exeV: absolute path of executable in inputfolder
    # soundinV: absolute path of sounding in inputfolder
    # outputD: output directory
    # radB: if radiation sounding is needed
    # radiationV: absolute path of radiation sounding in inputfolder
    # radiationP: relative path of radiation sounding in outputfolder = same as value in namelist
    
    copy2(exeV, outputD)
    copy2(soundinV, vmD.join([outputD,"sound_in"]))

    if radB:
        copy2( radiationV, vmD.join([outputD, radiationP]) )

def createPBSJobScript(jobname = "LES", nproc = 1, nodeNPU = 28, WT = "24:00:00", email = "jaakko.ahola@fmi.fi", rundir = "/lustre/tmp/aholaj/UCLALES-SALSA/bashjob", exe = "les.seq"):

    lines = []

    lines.append("#!/bin/sh")
    lines.append("#PBS -N {0}".format( jobname ))
    lines.append("#PBS -l mppwidth={0}".format( nproc ))
    lines.append("#PBS -l mppnppn={0}".format( nodeNPU ))
    lines.append("#PBS -l walltime={0}".format( WT ))
    lines.append("#PBS -j oe")
    lines.append("#PBS -M {0}".format( email ))
    lines.append("#PBS -m ae")
    lines.append("#PBS -o {0}".format( rundir ))
    lines.append("")
    lines.append("#export I_MPI_PLATFORM=auto")
    lines.append("#export MPICH_ALLTOALLV_THROTTLE=2")
    lines.append("")
    lines.append("export MPICH_ENV_DISPLAY=1")
    lines.append("")
    lines.append("# Exit on error")
    lines.append("set -e")
    lines.append("")
    lines.append("cd {0}".format( rundir ))
    lines.append("")
    lines.append("aprun -n {0} ./{1} | tee {2}/{3}.log".format( nproc, exe, rundir, jobname ))
    lines.append("exit")

    with open( rundir + "/" + "runles.sh", "w") as writer:
        for ll in lines:
            writer.write(ll)
            writer.write("\n")