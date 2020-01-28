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
      
    fileLists = {
                "LVL3Night" : InputSimulation.getEmulatorFileList(rootFolderOfEmulatorSets, folderList["LVL3Night"] ),
                "LVL3Day"   : InputSimulation.getEmulatorFileList(rootFolderOfEmulatorSets, folderList["LVL3Day"] ),
                "LVL4Night" : InputSimulation.getEmulatorFileList(rootFolderOfEmulatorSets, folderList["LVL4Night"] ),
                "LVL4Day"   : InputSimulation.getEmulatorFileList(rootFolderOfEmulatorSets, folderList["LVL4Day"] )
                }
    
    idLists = {
                "LVL3Night" : InputSimulation.getEmulatorIDlist(fileLists["LVL3Night"] ),
                "LVL3Day"   : InputSimulation.getEmulatorIDlist(fileLists["LVL3Day"] ),
                "LVL4Night" : InputSimulation.getEmulatorIDlist(fileLists["LVL4Night"] ),
                "LVL4Day"   : InputSimulation.getEmulatorIDlist(fileLists["LVL4Day"] )
            }
    
    labelLists = idLists
    
    colorLists = {
                "LVL3Night" : Colorful.getIndyColorList( len(fileLists["LVL3Night"]) ),
                "LVL3Day"   : Colorful.getIndyColorList( len(fileLists["LVL3Day"]) ),
                "LVL4Night" : Colorful.getIndyColorList( len(fileLists["LVL4Night"]) ),
                "LVL4Day"   : Colorful.getIndyColorList( len(fileLists["LVL4Day"]) )
            }
    
        

        
    simulationData = {
                "LVL3Night" : InputSimulation( idCollection= idLists["LVL3Night"], 
                                               folderCollection= fileLists["LVL3Night"],
                                               labelCollection = labelLists["LVL3Night"],
                                               colorSet= colorLists["LVL3Night"]),
                "LVL3Day"   : InputSimulation( idCollection= idLists["LVL3Day"], 
                                               folderCollection= fileLists["LVL3Day"],
                                               labelCollection = labelLists["LVL3Day"],
                                               colorSet= colorLists["LVL3Day"]),
                "LVL4Night" : InputSimulation( idCollection= idLists["LVL4Night"], 
                                               folderCollection= fileLists["LVL4Night"],
                                               labelCollection = labelLists["LVL4Night"],
                                               colorSet= colorLists["LVL4Night"]),
                "LVL4Day"   : InputSimulation( idCollection= idLists["LVL4Day"], 
                                               folderCollection= fileLists["LVL4Day"],
                                               labelCollection = labelLists["LVL4Day"],
                                               colorSet= colorLists["LVL4Day"])
            }   

#    emulatorLVL3Day = InputSimulation(
#            idCollection = "ids.yaml",
#            folderCollection="folders.yaml",
#            labelCollection="labels.yaml",
#            )
    
#    manuscriptSimulationData.saveDataFrameAsCSV(folder, "manuscriptSimulationData.csv")

def main():
    prepareEMULData()
   
if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print("Script completed in " + str(round((end - start),0)) + " seconds")       
