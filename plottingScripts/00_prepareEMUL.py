#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 14:41:12 2020

@author: Jaakko Ahola, Finnish Meteorological Institute
@licence: MIT licence Copyright
"""
import time

from InputSimulation import InputSimulation

def prepareEMULData():

                
    rootFolderOfEmulatorSets = "/home/aholaj/mounttauskansiot/eclairmount"
    
    fileListLVL3Night = InputSimulation.getEmulatorFileList(rootFolderOfEmulatorSets, "case_emulator_DESIGN_v3.0.0_LES_ECLAIR_branch_ECLAIRv2.0.cray.fast_LVL3_night" )
    fileListLVL3Day = InputSimulation.getEmulatorFileList(rootFolderOfEmulatorSets, "case_emulator_DESIGN_v3.1.0_LES_ECLAIR_branch_ECLAIRv2.0.cray.fast_LVL3_day" )
    
    fileListLVL4Night = InputSimulation.getEmulatorFileList(rootFolderOfEmulatorSets, "case_emulator_DESIGN_v3.2_LES_ECLAIR_branch_ECLAIRv2.0.cray.fast_LVL4_night" )
    fileListLVL4Day = InputSimulation.getEmulatorFileList(rootFolderOfEmulatorSets, "case_emulator_DESIGN_v3.3_LES_ECLAIR_branch_ECLAIRv2.0.cray.fast_LVL4_day" )
    
    
    emulatorLVL3Day = InputSimulation(
            idCollection = "ids.yaml",
            folderCollection="folders.yaml",
            labelCollection="labels.yaml",
            )
    
    manuscriptSimulationData.saveDataFrameAsCSV(folder, "manuscriptSimulationData.csv")

def main():
    prepareEMULData()
   
if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print("Script completed in " + str(round((end - start),0)) + " seconds")       
if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print("Script completed in " + str(round((end - start),0)) + " seconds")
