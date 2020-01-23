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
        idCollection = None, #either list or YAML file
        folderCollection = None, #either list or YAML file
        labelCollection = None, #either list or YAML file
        colorSet = None, #either list or YAML file or dictionary with "label" : "color" format
        folder = None):
        
        self.idCollection     = InputSimulation.__setupCollection(self, folder, idCollection)
        self.folderCollection = InputSimulation.__setupCollection(self,folder, folderCollection)
        self.labelCollection  = InputSimulation.__setupCollection(self,folder, labelCollection)
        self.colorCollection  = InputSimulation.__setupCollection(self,folder, colorSet)
        
        self.simulationDataFrame = InputSimulation.initSimulationDataFrame(self)
        
    def __setupCollection(self, folder, collectionVar):
        
        if isinstance(collectionVar, str):
            if folder is not None:
                absoluteFileOfPath = FileSystem.getAbsoluteFilename(folder,collectionVar)
            else:
                absoluteFileOfPath = collectionVar
                
            collection = FileSystem.readYAML( absoluteFileOfPath )
            
        elif isinstance(collectionVar, list):
            collection = collectionVar
        elif isinstance(collectionVar, dict):
            collection = InputSimulation.__createSimulationColorCollection( self.labelCollection, collectionVar)
        else:
            collection = None
        
        return collection
    
    def __createSimulationColorCollection( labelCollection, colorCollection, dtype = "|S7" ):
        
        simulationColorCollection = numpy.zeros( numpy.shape( labelCollection ), dtype=dtype )
        
        for ind, label in enumerate(labelCollection):
            simulationColorCollection[ind] = colorCollection[label]
        
        return list(simulationColorCollection)
    
    def getIdCollection(self):
        return self.idCollection
    def getFolderCollection(self):
        return self.folderCollection
    def getLabelCollection(self):
        return self.labelCollection
    def getColorCollection(self):
        return self.colorCollection
    def getSimulationDataFrame(self):
        return self.simulationDataFrame
    
    def setIdCollection(self, idCollection):
        self.idCollection = idCollection
    def setFolderCollection(self, folderCollection):
        self.folderCollection = folderCollection
    def setLabelCollection(self, labelCollection):
        self.labelCollection = labelCollection
    def setColorCollection(self, colorCollection):
        self.colorCollection = colorCollection
    def setSimulationDataFrame(self, simulationDataFrame):
        self.simulationDataFrame = simulationDataFrame
    
    def initSimulationDataFrame(self):
        checkType, checkLength = InputSimulation.checkObj(self)
        
        if checkType and checkLength:
        
            self.simulationDataFrame = pandas.DataFrame( data = numpy.asarray([
                                                                    self.idCollection,
                                                                    self.labelCollection,
                                                                    self.colorCollection,
                                                                    self.folderCollection ]).T,
                                      index = self.idCollection,
                                      columns = ["ID", "LABEL", "COLOR", "FOLDER"] )
        else:
            self.simulationDataFrame = None
        
        return self.simulationDataFrame
    
    def getSimulationCollection(simulationDataFrame):
        simulationCollection = {}
        for i in range(numpy.size(simulationDataFrame["ID"])):
            simulationCollection[ simulationDataFrame.iloc[i]["ID"] ] = Simulation( simulationDataFrame.iloc[i]["FOLDER"],
                                                                                    simulationDataFrame.iloc[i]["LABEL"],
                                                                                    simulationDataFrame.iloc[i]["COLOR"])
        return simulationCollection
    
    
    def checkObj(self):
        checkType, checkLength = InputSimulation.checkLists([self.idCollection, self.folderCollection, self.labelCollection, self.colorCollection])
        
        if not checkType:
            print("Object variable types are not lists")
        elif not checkLength:
            print("Object list lengths are incorrect")
            
        return checkType, checkLength
    
    def checkLists(arrayOfLists):
        checkType = True
        checkLength = True
        for k in arrayOfLists:
            checkType = (checkType and isinstance(k, list))
        
        for i in range(1,len(arrayOfLists)):
            checkLength = checkLength and (len(arrayOfLists[i-1]) == len(arrayOfLists[i]) )
        
        return checkType, checkLength
    
    def saveDataFrameAsCSV(self, folder, file = None):
        if self.simulationDataFrame is None:
            raise Exception("simulationDataFrame is not set. Set proper object variables and run initSimulationDataFrame()")
        if file is None:
            absFile = folder
        else:
            absFile = pathlib.Path(folder) / file
        self.simulationDataFrame.to_csv(absFile)
        
        return absFile
