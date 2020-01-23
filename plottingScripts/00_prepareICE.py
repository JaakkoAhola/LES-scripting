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

    colorDict ={
                "ICE0": "#3cb44b",
                "ICE1": "#f58231",
                "ICE2": "#f032e6",
                "ICE3": "#469990",
                "ICE4": "#4363d8",
                "ICE5": "#800000",
                "ICE6": "#000075",
                "Prognostic": "#e6194B",
                "BIN": "#000000",
                "BULK": "#a9a9a9"}
                
    folder = "/home/aholaj/OneDrive/kuvatesti/"
    
    manuscriptSimulationData = InputSimulation(
            idCollection = "ids.yaml",
            folderCollection="folders.yaml",
            labelCollection="labels.yaml",
            colorSet =  colorDict,
            folder = folder)
    
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
