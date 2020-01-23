#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 12:28:17 2020

@author: Jaakko Ahola, Finnish Meteorological Institute
@licence: MIT licence Copyright
"""
import numpy
import pandas
import pathlib
import time

from FileSystem import FileSystem
from Simulation import Simulation

class InputSimulation:
    
    def __init__(self,
        folderCollectionYAMLFile,
        labelCollectionYAMLFile,
        idCollectionYAMLFile,
        colorCollection, folder = None):
        
        if folder is not None:
            self.folder = pathlib.Path(folder)
            
            folderCollectionYAMLFile = self.folder / folderCollectionYAMLFile
            labelCollectionYAMLFile  = self.folder / labelCollectionYAMLFile
            idCollectionYAMLFile     = self.folder / idCollectionYAMLFile
            
        
        self.simulationDataFrame = InputSimulation.getSimulationDataFrame(folderCollectionYAMLFile,
                                                                     labelCollectionYAMLFile,
                                                                     idCollectionYAMLFile,
                                                                     colorCollection)
    
    
    def createSimulationColorCollection( labelCollection, colorCollection, dtype = "|S7" ):
        
        simulationColorCollection = numpy.zeros( numpy.shape( labelCollection ), dtype=dtype )
        
        for ind, label in enumerate(labelCollection):
            simulationColorCollection[ind] = colorCollection[label]
        
        return simulationColorCollection
    
    def getSimulationDataFrame(folderCollectionYAMLFile, labelCollectionYAMLFile, idCollectionYAMLFile, colorCollection):
        folderCollection = FileSystem.readYAML( folderCollectionYAMLFile )
        labelCollection = FileSystem.readYAML( labelCollectionYAMLFile)
        idCollection = FileSystem.readYAML( idCollectionYAMLFile )
        
        simulationColorCollection = InputSimulation.createSimulationColorCollection( labelCollection, colorCollection)
    
        simulationDataFrame = pandas.DataFrame(data = numpy.asarray([idCollection,labelCollection,simulationColorCollection, folderCollection, ]).T,
                                      index = idCollection,
                                      columns = ["ID", "LABEL", "COLOR", "FOLDER"])
        return simulationDataFrame
    
    def getSimulationCollection(simulationDataFrame):
        simulationCollection = {}
        for i in range(numpy.size(simulationDataFrame["ID"])):
            simulationCollection[ simulationDataFrame.iloc[i]["ID"] ] = Simulation( simulationDataFrame.iloc[i]["FOLDER"],
                                                                                    simulationDataFrame.iloc[i]["LABEL"],
                                                                                    simulationDataFrame.iloc[i]["COLOR"])
        return simulationCollection
    
    def saveDataFrameAsCSV(self, folder, file = None):
        if file is None:
            absFile = folder
        else:
            absFile = pathlib.Path(folder) / file
        self.simulationDataFrame.to_csv(absFile)
        
        return absFile
    
def main():
    if False:
        colorCollection ={
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
                folderCollectionYAMLFile="folders.yaml",
                labelCollectionYAMLFile="labels.yaml",
                idCollectionYAMLFile = "ids.yaml",
                colorCollection =  colorCollection,
                folder = folder)
        
        manuscriptSimulationData.saveDataFrameAsCSV(folder, "manuscriptSimulationData.csv")
   
if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print("Script completed in " + str(round((end - start),0)) + " seconds")    