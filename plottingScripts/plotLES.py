#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 10:50:04 2020

@author: Jaakko Ahola, Finnish Meteorological Institute
@licence: MIT licence Copyright
"""
import matplotlib
import numpy
import pathlib
import seaborn
import time
import xarray

from collections import defaultdict
from math import ceil
from math import floor


class Simulation:
    
    def __init__(self, folder, namelabel, color):
        self.folder = pathlib.Path(folder)
        self.namelabel = namelabel
        self.color = color
            
    def getNCDataset(self):
        return self._getDataset("nc")
    
    def getPSDataset(self):
        return self._getDataset("ps")
    
    def getTSDataset(self):
        return self._getDataset("ts")
    
    def _getDataset(self, ncMode):
    
        if "." not in ncMode:
            ncModeSuffix = "." + ncMode
        
        fileAbs = None
        for ncFile in list(self.folder.glob("*.nc")):
            if ncMode != "":
                if ncModeSuffix in ncFile.suffixes:
                    fileAbs = ncFile
            else:
                if ".ps" not in ncFile.suffixes and ".ts" not in ncFile.suffixes:
                    fileAbs = ncFile
        if fileAbs is not None:
            dataset = xarray.open_dataset(fileAbs)
        else:
            dataset = None
        
        return dataset
    
    def getEntrainment(self,
                       divergence = 5.e-6):
        ts = self.getTSDataset()
        z = ts.zi1_bar.values
        t = ts.time.values
        dzdt = numpy.diff(z) / numpy.diff(t)
        we = xarray.DataArray( dzdt + divergence*z[1:], dims={"h":ts.time.values[1:]/3600}, coords = {"time":ts.time.values[1:]/3600}, attrs={"longname":"Entrainment velocity", "units":"m/s"})
        return we
    
    ####
    #### need revision
    ####
    def getNormalisedHeight(h, cloudbase, cloudtop):
        x_incloud = [cloudbase,cloudtop]
        y_incloud = [0,1]
        z_incloud = numpy.polyfit(x_incloud,y_incloud,1)
    
        x_belowcloud = [0,cloudbase]
        y_belowcloud = [-1,0]
        z_belowcloud = numpy.polyfit(x_belowcloud,y_belowcloud,1)
        
        if h<cloudbase:
            rr = numpy.poly1d(z_belowcloud)(h)
        else:
            rr = numpy.poly1d(z_incloud)(h)
        return rr
    
    
class Figure:
    
    def __init__(self, figurefolder, name,
                 nrows = 1, ncols =1, sharex=False, sharey=False):
        
        self._setContext()
        
        self.figurefolder = pathlib.Path(figurefolder)
        self.name = name
        self.absoluteName = self.figurefolder / name
        self.fig, self.axes = matplotlib.pyplot.subplots( nrows = nrows, ncols=ncols, sharex=sharex, sharey=sharey, figsize=() )
    
    def getFig(self):
        return self.fig
    
    def getAxes(self):
        return self.axes

    def _setContext(printing = False):
        
        matplotlib.pyplot.style.use('seaborn-paper')
        seaborn.set_context("poster")
        matplotlib.rcParams['figure.figsize'] = [ matplotlib.rcParams['figure.figsize'][0]*2.0, matplotlib.rcParams['figure.figsize'][1]*2.0 ]
        print('figure.figsize', matplotlib.rcParams['figure.figsize'])
    
        print('figure.dpi', matplotlib.rcParams['figure.dpi'])
        matplotlib.rcParams['savefig.dpi'] = 300.
        print('savefig.dpi', matplotlib.rcParams['savefig.dpi'])
        matplotlib.rcParams['legend.fontsize'] = 14
        print('legend.fontsize', matplotlib.rcParams['legend.fontsize'])
        matplotlib.rcParams['axes.titlesize'] = 42
        matplotlib.rcParams['axes.labelsize'] = 42
        matplotlib.rcParams['xtick.labelsize'] = 42 #22
        matplotlib.rcParams['ytick.labelsize'] = 42 #22
        matplotlib.rcParams['font.weight']= 'bold' #this should be changed
        print('axes.titlesize', matplotlib.rcParams['axes.titlesize'])
        print('axes.labelsize', matplotlib.rcParams['axes.labelsize'])
        print('xtick.labelsize', matplotlib.rcParams['xtick.labelsize'])
        print('ytick.labelsize', matplotlib.rcParams['ytick.labelsize'])
        print("lines.linewidth", matplotlib.rcParams['lines.linewidth'])
        matplotlib.rcParams['text.latex.unicode'] = False
        matplotlib.rcParams['text.usetex'] = False
        print("text.latex.unicode", matplotlib.rcParams['text.latex.unicode'])
        matplotlib.rcParams['text.latex.preamble']=[r'\usepackage{amsmath}']
        matplotlib.rc('text', usetex = True)
        
    def save(self, file_extension = ".png", padding = 0.06, bbox_inches = "tight", close = True):

        self.fig.savefig( self.absoluteName.with_suffix( file_extension ), pad_inches = padding, bbox_inches = bbox_inches )
        
        if close:
            matplotlib.pyplot.close()
            
class Plot:
    
    def hideXLabels(ax, xLabelListShowBoolean, xLabelListMajorLineBoolean):
        k = 0
        for label in ax.xaxis.get_ticklabels():
            label.set_visible(xLabelListShowBoolean[k])
            k = k + 1
        
        k = 0
        for line in ax.xaxis.get_ticklines()[0::2]:
            if xLabelListMajorLineBoolean[k]:
                line.set_markersize(matplotlib.rcParams["xtick.major.size"])
            else:
                line.set_markersize(matplotlib.rcParams["xtick.minor.size"])
            k= k + 1

        return ax
    
    def setXTicksLabelsAsTime(ax, timeHvalues, tickInterval = 16, unit = "h", startPoint = 0,  xLabelListShow = None, xLabelListMajorLine = None, setXlabel = True):
        first = timeHvalues[0]
        last = timeHvalues[-1]
        xticks = numpy.arange(first,last+0.1, 0.5) 
        #xticks = xticks[::tickInterval]
        xticklabels = [ str(int(round(elem,1))) for elem in list(xticks) ]
        #print(xticks)
        ax.set_xticks( xticks )
        ax.set_xticklabels(xticklabels)
        
        timesize = numpy.shape(xticks)[0]
        #####################
        if xLabelListShow is None:
            xLabelListShowBoolean = [False]*timesize
            #timesize = numpy.shape(timeHvalues)[0]
            
            for i in range(timesize):
                if numpy.mod(i, tickInterval) == 0:
                    xLabelListShowBoolean[i] = True
        else:
            xLabelListShowBoolean = Data.maskingList( xticks, xLabelListShow)
        #############################
        if xLabelListMajorLine is None:
            xLabelListMajorLineBoolean = [False]*timesize
            
            for i in range(timesize):
                if numpy.mod(i, tickInterval) == 0:
                    xLabelListMajorLineBoolean[i] = True
        else:
            xLabelListMajorLineBoolean = Data.maskingList( xticks, xLabelListMajorLine)
        
            
        ax = Plot.hideXLabels(ax, xLabelListShowBoolean, xLabelListMajorLineBoolean)
        
        if setXlabel:
            ax.set_xlabel(r"$\mathbf{time (" + unit + ")}$") 
        else:
            ax.set_xlabel(None)
        ax.set_xlim( first ,last )
    
        return ax
    
    def profileTimeseries(simulation : Simulation,
                          ax,
                          muuttuja, 
                         useContours = True,
                         useColorBar = True,
                         showXaxisLabels = True,
                         showXLabel = True,
                         yticks = None,
                         folder = "/home/aholaj/case_isdac_LVL5_3D_iceD_inter_48h",
                         kuvakansio = "/home/aholaj/OneDrive/000_WORK/000_ARTIKKELIT/000-Manuscript-ICE/kuvat/bini/",
                         kuvakansioPDF = None,
                         filenamePDF  = "prof",
                         figurePrefix = "",
                         levels = None,
                         timeStartH = 0., timeEndH = 48,
                         uusikuva = True, title = None, colors = None, plotSpinup = True):

        ps = simulation.getPSDataset()
        ts = simulation.getTSDataset()
        
        if ps is None:
            return "FileNotFound"
        
        timeStartInd = Data.getClosestIndex( ps.time.values, timeStartH*3600 )
        timeEndInd   = Data.getClosestIndex( ps.time.values, timeEndH*3600 )
        ps = ps.isel(time = slice(timeStartInd,timeEndInd))
        ts = ts.isel(time = slice(timeStartInd,timeEndInd))
        ps = ps.assign_coords(time = (ps.time / 3600))
        ts = ts.assign_coords(time = (ts.time / 3600))
        
            
        
        
        try:
            data = ps[muuttuja]
        except KeyError:
            return
        
        
    #    data = data.assign_coords(time = (data.time / 3600))
    
    #    fig = matplotlib.figure()
        
        if levels is None:
            levels, rangePotenssi, minimiPotenssi, maksimiPotenssi = Data.getLogScale(data.values)
            
            levels = rangePotenssi#numpy.power(10,levels)
            print(levels, minimiPotenssi, maksimiPotenssi, rangePotenssi)
    #    negPotenssi = -15
    #    posPotenssi = 4
        
        
        xLabelListShow = numpy.arange(0, 48+1, 8)
        
        
        xLabelListMajorLine = numpy.arange(4, 48+1, 4)
        
        ax = Plot.setXTicksLabelsAsTime(ax, ps.time.values, xLabelListShow = xLabelListShow, xLabelListMajorLine = xLabelListMajorLine)
        if yticks is not None:
            ax.set_yticklabels( list(map(str, yticks)))
        data.values  = numpy.log10(data.values)
        im = data.plot.contourf("time","zt", ax = ax, levels=levels, add_colorbar = False, colors = colors) #
        
        if useContours:
            ps.P_RHi.plot.contour(x="time", y="zt",ax=ax, colors ="black", vmin = 100-1e-12, vmax = 100 + 1e-12)#e6194B
            ts.zb.where(ts.zb>0).plot(ax=ax, color="#f58231") 
        
    #    im = data.plot(x="time",y="zt",) #
        if useColorBar:
            cb = matplotlib.colorbar(im, ticks = levels, orientation='horizontal', pad = 0.22) #, pad=0.21
            cb.ax.set_xticklabels([r"$10^{" + str(int(elem)) + "}$" for elem in levels]) 
            
            colorbarLabelListShowBoolean = getIntegerExponentsAsBoolean( levels )
            piilotaColorbarXLabels(cb, colorbarLabelListShowBoolean)
            cb.ax.tick_params(labelsize=36)
        
    #    xticks = numpy.arange(0,data["time"].values[-1]+0.1, 0.5) 
    #    xticks = xticks[::16]
    #    xticklabels = [ str(int(round(elem,1))) for elem in list(xticks) ]
        #print(xticks)
        
        ax.set_yticks( numpy.arange(0, 1001, 250))
    #    ax.set_xticks( xticks )
       
        if not showXaxisLabels:
            ax.set_xticklabels([])
        
        if showXLabel:    
            matplotlib.xlabel(r"$\mathbf{time (h)}$")
        else:
            matplotlib.xlabel(None)
            
        matplotlib.ylabel(r"$\mathbf{height (m)}$")
        matplotlib.xlim( 0 ,data["time"].values[-1] )
        matplotlib.ylim(0, 1000)
        if plotSpinup:
            matplotlib.axvline(2, color = "black", linestyle = "--")
        if title is None:
            title = data.longname
        
           
        matplotlib.title(title)
        
        #data.plot.contourf("time","zt")#, levels=levels, cbar_kwargs={"ticks": levels})
        
        saveFig( kuvakansio,  figurePrefix + muuttuja, padding = 0.10)
        
        if kuvakansioPDF is not None:
             saveFig(kuvakansioPDF, figurePrefix + filenamePDF, file_extension="pdf", dpi = 80)
    
        
class Data:
    def isCloseToEpsilon(dataarray : numpy.array, limit = numpy.finfo(float).eps ):
        zero =  False
        if (numpy.abs(numpy.min(dataarray) - numpy.max(dataarray)) < limit ):
            zero = True
    
        return zero
    
    def getLogScale(dataarray : numpy.array, minimiPotenssi = None, maksimiPotenssi = None):
        
        if minimiPotenssi is None:
            minimiPotenssi = max( floor( numpy.log10(numpy.min(dataarray[numpy.where(dataarray > numpy.finfo(float).eps)])) ), ceil(numpy.log10(numpy.finfo(float).eps)))
        maksimiPotenssi = ceil( numpy.log10(numpy.max(dataarray)) )
        rangePotenssi = list(numpy.arange(minimiPotenssi, maksimiPotenssi +1))
        potenssidict = defaultdict(list)
        
        for num in rangePotenssi:
            if num < 0:
                potenssidict['neg'].append(num)
            else: # This will also append zero to the positive list, you can change the behavior by modifying the conditions 
                potenssidict['pos'].append(num)
        
        if len(potenssidict['neg'])>0:
            negLevels = 1/numpy.power(10, -1*numpy.asarray(potenssidict['neg']))
        else:
            negLevels = numpy.asarray([])
            
        if len(potenssidict['pos'])>0:
            posLevels = numpy.power(10, numpy.asarray(potenssidict['pos']))
        else:
            posLevels = numpy.asarray([])
        
        levels = numpy.concatenate((negLevels,posLevels))
        
        return levels, rangePotenssi, minimiPotenssi, maksimiPotenssi

    def getClosestIndex(dataarray, searchValue):
        return numpy.argmin(numpy.abs(searchValue- dataarray))
    
    def maskingList(dataarray, listOfValues, initial = False):
        booleanList = [initial]*numpy.shape(dataarray)[0]
        
        indexes = [ numpy.argmin(numpy.abs(elem - dataarray)) for elem in listOfValues ]
        
        for i in indexes:
            booleanList[i] = (not initial)
        
        return booleanList

def main():
    pass
if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print("Script completed in " + str(round((end - start),0)) + " seconds")
