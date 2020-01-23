#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 14:41:12 2020

@author: Jaakko Ahola, Finnish Meteorological Institute
@licence: MIT licence Copyright
"""
import time

from InputSimulation import InputSimulation

def prepareIceManuscriptData():

                
    folder = "/home/aholaj/OneDrive/kuvatesti/"
    
    emulatorLVL3Day = InputSimulation(
            idCollection = "ids.yaml",
            folderCollection="folders.yaml",
            labelCollection="labels.yaml",
            )
    
    manuscriptSimulationData.saveDataFrameAsCSV(folder, "manuscriptSimulationData.csv")

def main():
    prepareIceManuscriptData()
   
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
