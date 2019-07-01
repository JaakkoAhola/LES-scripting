#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 13:08:29 2019

@author: aholaj
"""

def createBashJobScript(jobname = "LES", nproc = 1, nodeNPU = 24, WT = "24:00:00", email = "jaakko.ahola@fmi.fi", rundir = "/lustre/tmp/aholaj/UCLALES-SALSA/bashjob", exe = "les.seq"):

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