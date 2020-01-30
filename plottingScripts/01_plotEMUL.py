#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 15:46:01 2020

@author: Jaakko Ahola, Finnish Meteorological Institute
@licence: MIT licence Copyright
"""
import matplotlib
import numpy
import pandas
import seaborn
import time

from Colorful import Colorful
from InputSimulation import InputSimulation
from Figure import Figure
from Plot import Plot
from PlotTweak import PlotTweak


def main():
    
    caseCollection = ["LVL3Night",
                "LVL3Day",
                "LVL4Night",
                "LVL4Day"]
    
    annotationValues = ["(a) LVL3 Night",
            "(b) LVL3 Day",
            "(c) LVL4 Night",
            "(d) LVL4 Day"]
    
    annotationCollection = dict(zip(caseCollection, annotationValues))
    
    designsDataFrames = { "LVL3Night" : ,
                "LVL3Day",
                "LVL4Night", 
                "LVL4Day" : pandas.read_csv("/home/aholaj/mounttauskansiot/eclairmount/case_emulator_DESIGN_v3.3_LES_ECLAIR_branch_ECLAIRv2.0.cray.fast_LVL4_day/design.csv")
            }
    
    csvFolder = "/home/aholaj/OneDrive/000_WORK/000_ARTIKKELIT/001_Manuscript_LES_emulator/data/"
    
    simulationCollection ={}
    
    for case in caseCollection:
        simulationCollection[case] = InputSimulation.getSimulationCollection( 
                                                        pandas.read_csv( csvFolder + case + ".csv") )
    
    #figure folder
    figurefolder = "/home/aholaj/OneDrive/000_WORK/000_ARTIKKELIT/001_Manuscript_LES_emulator/figures"
    cloudTopOutliers = {}
    lwpOutliers = {}
    # load ts-datasets and change their time coordinates to hours
    keisseja = 10000  # TODO REMOVE THIS
    for case in caseCollection:
        for emul in list(simulationCollection[case])[:keisseja]:
            print(emul)
            
            simulationCollection[case][emul].getTSDataset()
            #simulationCollection[case][emul].getPSDataset()
            simulationCollection[case][emul].setTimeCoordToHours()
    
    
    LWPFigureFlag = True
    CloudFracFigureFlag = True
    if LWPFigureFlag:
        print(" ")
        print("lwp")
        # create figure object
        fig2 = Figure(figurefolder,"lwp", ncols=2, nrows=2, sharex=True, sharey = True)
        # plot timeseries with unit conversion
        maks = 0
        mini = 0
        for ind, case in enumerate(caseCollection):
            for emul in list(simulationCollection[case])[:keisseja]:
                dataset = simulationCollection[case][emul].getTSDataset()
                muuttuja = dataset["lwp_bar"]
                
                alku = muuttuja.sel(time =1.5, method = "nearest").values
                loppu = muuttuja.isel(time = -1).values
                conversion = 1000.
                colorParam = loppu/alku
                if colorParam > 1.2:
                    color = Colorful.getDistinctColorList("red")
                    zorderParam = 10
                    print('"' +  case + '"' + " : " + '"' + emul + '"' + ",")
                    lwpOutliers[case] = emul
                elif colorParam < 0.8:
                    color = Colorful.getDistinctColorList("blue")
                    zorderParam = 9
                else:
                    color = "white"
                    zorderParam  = 6
                
                if colorParam < 0.1:
                    print('"' +  case + '"' + " : " + '"' + emul + '"' + ",")
                    lwpOutliers[case] = emul  
                        
                        
                maks = max(colorParam, maks)
                mini = min(colorParam, mini)
                
                fig2.getAxes(True)[ind].plot( alku*conversion,  loppu*conversion,
                                                 marker = "o",
                                                 markerfacecolor = color,
                                                 markeredgecolor = "black",
                                                 markeredgewidth=0.2,
                                                 markersize = 6,
                                                 alpha = 0.5,
                                                 zorder=zorderParam
                                                 )
        print("minimi", mini, "maksimi",maks)
            
        xmax = 1000
        ymax = 1000
        
        for ind, case in enumerate(caseCollection):
            PlotTweak.setAnnotation(fig2.getAxes(True)[ind], annotationCollection[case], xPosition=100, yPosition=ymax-100)
            PlotTweak.setXLim(fig2.getAxes(True)[ind],0,xmax)
            PlotTweak.setYLim(fig2.getAxes(True)[ind],0,ymax)
            fig2.getAxes(True)[ind].plot( [0,xmax], [0, ymax], 'k-', alpha=0.75, zorder=0)
    
        PlotTweak.setXaxisLabel( fig2.getAxes(True)[2], "LWP", "g m^{-2}", useBold=True)
        PlotTweak.setXaxisLabel( fig2.getAxes(True)[3], "LWP", "g m^{-2}", useBold=True)
        PlotTweak.setYaxisLabel( fig2.getAxes(True)[0], "LWP", "g m^{-2}", useBold=True)
        PlotTweak.setYaxisLabel( fig2.getAxes(True)[2], "LWP", "g m^{-2}", useBold=True)
        PlotTweak.setLegend(fig2.getAxes(True)[0], {"Change > +20%" : Colorful.getDistinctColorList("red"),
                                                    "Change < 20% " : "white",
                                                    "Change < -20%" : Colorful.getDistinctColorList("blue"),
                                                        }, loc=(0.02,0.6), fontsize = 6)
        fig2.save()
        
    if CloudFracFigureFlag:
        print(" ")
        print("cloudtop")
        # create figure object
        fig2 = Figure(figurefolder,"cloudtop", ncols=2, nrows=2, sharex=True, sharey = True)
        # plot timeseries with unit conversion
        maks = 0
        mini = 0
        for ind, case in enumerate(caseCollection):
            for emul in list(simulationCollection[case])[:keisseja]:
                dataset = simulationCollection[case][emul].getTSDataset()
                muuttuja = dataset["zc"]
                
                alku = muuttuja.sel(time =1.5, method = "nearest").values
                loppu = muuttuja.isel(time = -1).values
                conversion = 1
                colorParam = loppu/alku
                if colorParam > 1.2:
                    color = Colorful.getDistinctColorList("red")
                    zorderParam = 10
                    print('"' +  case + '"' + " : " + '"' + emul + '"' + ",")
                    cloudTopOutliers[case] = emul
                elif colorParam < 0.8:
                    color = Colorful.getDistinctColorList("blue")
                    zorderParam = 9
                    print('"' +  case + '"' + " : " + '"' + emul + '"' + ",")
                    cloudTopOutliers[case] = emul
                else:
                    color = "white"
                    zorderParam  = 6
                      
                        
                        
                maks = max(colorParam, maks)
                mini = min(colorParam, mini)
                
                fig2.getAxes(True)[ind].plot( alku*conversion,  loppu*conversion,
                                                 marker = "o",
                                                 markerfacecolor = color,
                                                 markeredgecolor = "black",
                                                 markeredgewidth=0.2,
                                                 markersize = 6,
                                                 alpha = 0.5,
                                                 zorder=zorderParam
                                                 )
        print("minimi", mini, "maksimi",maks)
            
        xmax = 3600
        ymax = 3600
        
        for ind, case in enumerate(caseCollection):
            PlotTweak.setAnnotation(fig2.getAxes(True)[ind], annotationCollection[case], xPosition=100, yPosition=ymax-300)
            PlotTweak.setXLim(fig2.getAxes(True)[ind],0,xmax)
            PlotTweak.setYLim(fig2.getAxes(True)[ind],0,ymax)
            fig2.getAxes(True)[ind].plot( [0,xmax], [0, ymax], 'k-', alpha=0.75, zorder=0)
        
        
        
        PlotTweak.setLegend(fig2.getAxes(True)[0], {"Change > +20%" : Colorful.getDistinctColorList("red"),
                                                    "Change < 20% " : "white",
                                                    "Change < -20%" : Colorful.getDistinctColorList("blue"),
                                                        }, loc=(0.02,0.6), fontsize = 6)
        
        PlotTweak.setXaxisLabel( fig2.getAxes(True)[2], "Cloud\ top", "m", useBold=True)
        PlotTweak.setXaxisLabel( fig2.getAxes(True)[3], "Cloud\ top", "m", useBold=True)
        PlotTweak.setYaxisLabel( fig2.getAxes(True)[0], "Cloud\ top", "m", useBold=True)
        PlotTweak.setYaxisLabel( fig2.getAxes(True)[2], "Cloud\ top", "m", useBold=True)
        fig2.save()
    
    cloudTopOutliersFlag = True
    if cloudTopOutliersFlag:
        fig2 = Figure(figurefolder,"cloudtopOutliers", ncols=2, nrows=2, sharex=True, sharey = True)
        # plot timeseries with unit conversion
        for ind, case in enumerate(caseCollection):
            for emul in list(simulationCollection[case])[:keisseja]:
                dataset = simulationCollection[case][emul].getTSDataset()
                muuttuja = dataset["zc"]
                
                alku = muuttuja.sel(time =1.5, method = "nearest").values
                loppu = muuttuja.isel(time = -1).values

                fig2.getAxes(True)[ind].plot( alku*conversion,  loppu*conversion,
                                                 marker = "o",
                                                 markerfacecolor = color,
                                                 markeredgecolor = "black",
                                                 markeredgewidth=0.2,
                                                 markersize = 6,
                                                 alpha = 0.5,
                                                 zorder=zorderParam
                                                 )
            
        xmax = 3600
        ymax = 3600
        
        for ind, case in enumerate(caseCollection):
            PlotTweak.setAnnotation(fig2.getAxes(True)[ind], annotationCollection[case], xPosition=100, yPosition=ymax-300)
            PlotTweak.setXLim(fig2.getAxes(True)[ind],0,xmax)
            PlotTweak.setYLim(fig2.getAxes(True)[ind],0,ymax)
            fig2.getAxes(True)[ind].plot( [0,xmax], [0, ymax], 'k-', alpha=0.75, zorder=0)
        
        
        
        PlotTweak.setLegend(fig2.getAxes(True)[0], {"Change > +20%" : Colorful.getDistinctColorList("red"),
                                                    "Change < 20% " : "white",
                                                    "Change < -20%" : Colorful.getDistinctColorList("blue"),
                                                        }, loc=(0.02,0.6), fontsize = 6)
        
        PlotTweak.setXaxisLabel( fig2.getAxes(True)[2], "Cloud\ top", "m", useBold=True)
        PlotTweak.setXaxisLabel( fig2.getAxes(True)[3], "Cloud\ top", "m", useBold=True)
        PlotTweak.setYaxisLabel( fig2.getAxes(True)[0], "Cloud\ top", "m", useBold=True)
        PlotTweak.setYaxisLabel( fig2.getAxes(True)[2], "Cloud\ top", "m", useBold=True)
        fig2.save()        
        
        
        
#    Plot.getTimeseries(fig2.getAxes()[0,0],
#                       list( simulationCollection["LVL3Night"].values())[:10],
#                       "lwp_bar", conversionFactor=1000.)
#    Plot.getVerticalLine(fig2.getAxes()[0,0], 1.5)
#    
#    if True:
#        PlotTweak.setSuperWrapper(fig2.getAxes()[0,0],
#                              xstart = 0,
#                              xend = 3.5,
#                              xtickinterval = 0.5,
#                              xlabelinterval = 1,
        
#                              xticks = None,
#                              xShownLabels = None,
#                              xTickMajorFontSize = 3.5, # matplotlib.rcParams["xtick.major.size"],
#                              yTickMajorFontSize = 3.5, #matplotlib.rcParams["ytick.major.size"],
#                              ystart = 0, 
#                              yend = 800,
#                              ytickinterval = 50,
#                              ylabelinterval = 100,
#                              yticks = None,
#                              yShownLabels = None,
#                              annotationText = None,
#                              annotationXPosition = 2,
#                              annotationYPosition = 30,
#                              xlabel = "Time",
#                              xunit  = "h",
#                              ylabel = "LWP",
#                              yunit  = "g\ m^{-2}",
#                              useBold = True
#                              )
#    PlotTweak.hideYTickLabels( fig2.getAxes()[0,0] )
#    
#    PlotTweak.setAxesOff( fig2.getAxes()[0,1] )
#    PlotTweak.setLegendSimulation(fig2.getAxes()[0,1], [simulationCollection["ICE0_8h"], simulationCollection["ICE1_8h"]])
#    
#    ax, im, levels = Plot.getTimeseriesOfProfile(fig2.getAxes()[1,1],
#                     simulationCollection["ICE0_8h"],
#                     "P_RH",
#                     levels = None,
#                     useLogaritmic = False,
#                     colors = None)
#    PlotTweak.setAxesOff( fig2.getAxes()[1,0] )
#    cax = matplotlib.pyplot.axes([0.05, 0.25, 0.3, 0.03])
#    Plot.getColorBar(im, cax, levels, pad = 0.22)
    
    #Plot.getContourLine(fig2.getAxes()[1,1],"ICE0_8h", color =  'black' , value = 100)
    
    

        
if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print("Script completed in " + str(round((end - start),0)) + " seconds")
