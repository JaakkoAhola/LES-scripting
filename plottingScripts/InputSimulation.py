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
