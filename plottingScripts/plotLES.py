#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 10:50:04 2020

@author: Jaakko Ahola, Finnish Meteorological Institute
@licence: MIT licence Copyright
"""
import numpy
import pandas
import time


from Simulation import Simulation
from Figure import Figure
from Plot import Plot
from FileSystem import FileSystem

class inputSimulation:
    
    
    def createSimulationColorCollection( labelCollection, colorCollection, dtype = "|S7" ):
        
        simulationColorCollection = numpy.zeros( numpy.shape( labelCollection ), dtype=dtype )
        
        for ind, label in enumerate(labelCollection):
            simulationColorCollection[ind] = colorCollection[label]
        
        return simulationColorCollection
    
    def getSimulationDataFrame(folderCollectionYAMLFile, labelCollectionYAMLFile, idCollectionYAMLFile, colorCollection):
        folderCollection = FileSystem.readYAML( folderCollectionYAMLFile )
        labelCollection = FileSystem.readYAML( labelCollectionYAMLFile)
        idCollection = FileSystem.readYAML( idCollectionYAMLFile )
        
        simulationColorCollection = inputSimulation.createSimulationColorCollection( labelCollection, colorCollection)
    
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
        
def main(
        simulationDataFrameCSVFile = None,
        folderCollectionYAMLFile = None,
        labelCollectionYAMLFile = None,
        idCollectionYAMLFile = None,
        colorCollection = None):
    
    if simulationDataFrameCSVFile is None:
        simulationDataFrame = inputSimulation.getSimulationDataFrame(folderCollectionYAMLFile,
                                                                     labelCollectionYAMLFile,
                                                                     idCollectionYAMLFile,
                                                                     colorCollection)
    else:
        simulationDataFrame = pandas.read_csv(simulationDataFrameCSVFile)
    
    
    # simulation data as dictionary
    simulationCollection = inputSimulation.getSimulationCollection( simulationDataFrame )
        
    
    #inter = Simulation("/home/aholaj/case_isdac_LVL5_3D_iceD_inter_48h", "Prognostic", "red")
    
    fig1 = Figure("/home/aholaj/OneDrive/kuvatesti","Prognostic")
    
    cloudTicks = Plot.getTicks(0, 1000, 250)

    logaritmicLevels = Plot.getLogaritmicTicks(-17,-9, includeFives = True)
    
    ax, im = Plot.getTimeseriesOfProfile(fig1.getAxes(),
                                simulationCollection["Prognostic_48h"],
                                "P_cDUa",
                                title = "",
                                yticks = cloudTicks,
                                timeEndH= 33.05, levels = logaritmicLevels,
                                useColorBar = False, showXaxisLabels=False, 
                                showXLabel = False
                                )
    
    fig1.save()
    
    
if __name__ == "__main__":
    start = time.time()
    
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
    
    main(
            folderCollectionYAMLFile="/home/aholaj/OneDrive/kuvatesti/folders.yaml",
            labelCollectionYAMLFile="/home/aholaj/OneDrive/kuvatesti/labels.yaml",
            idCollectionYAMLFile = "/home/aholaj/OneDrive/kuvatesti/ids.yaml",
            colorCollection =  colorCollection)
    
    end = time.time()
    print("Script completed in " + str(round((end - start),0)) + " seconds")
