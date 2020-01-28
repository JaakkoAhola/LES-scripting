#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 14:41:12 2020

@author: Jaakko Ahola, Finnish Meteorological Institute
@licence: MIT licence Copyright
"""
import time

from InputSimulation import InputSimulation
from Colorful import Colorful
def changeToStringList(array):
    return list(map(str, array))

def prepareEMULData():

                
    rootFolderOfEmulatorSets = "/home/aholaj/mounttauskansiot/eclairmount"
    
    folderList = {"LVL3Night" :"case_emulator_DESIGN_v3.0.0_LES_ECLAIR_branch_ECLAIRv2.0.cray.fast_LVL3_night",
                "LVL3Day"   :  "case_emulator_DESIGN_v3.1.0_LES_ECLAIR_branch_ECLAIRv2.0.cray.fast_LVL3_day" ,
                "LVL4Night" :  "case_emulator_DESIGN_v3.2_LES_ECLAIR_branch_ECLAIRv2.0.cray.fast_LVL4_night" ,
                "LVL4Day"   : "case_emulator_DESIGN_v3.3_LES_ECLAIR_branch_ECLAIRv2.0.cray.fast_LVL4_day" 
                }
      
    fileLists = {}
    idLists = {}
    labelLists = {}
    colorLists = {}
    
    for case in list(folderList):
        fileLists[case]  = InputSimulation.getEmulatorFileList(rootFolderOfEmulatorSets, folderList[case] )
        idLists[case]    = InputSimulation.getEmulatorIDlist(fileLists[case])
        labelLists[case] = idLists[case]
        colorLists[case] = Colorful.getIndyColorList( len(fileLists[case]))
    
    
    simulationData = {}
    for case in list(folderList):
        simulationData[case] = InputSimulation( idCollection= idLists[case], 
                                               folderCollection= fileLists[case],
                                               labelCollection = labelLists[case],
                                               colorSet= colorLists[case])
        
#    manuscriptSimulationData.saveDataFrameAsCSV(folder, "manuscriptSimulationData.csv")

def main():
    prepareEMULData()
   
if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print("Script completed in " + str(round((end - start),0)) + " seconds")       
