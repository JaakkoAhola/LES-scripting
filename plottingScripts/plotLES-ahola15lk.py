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
    
    
class Figure:
    
    def __init__(self, figurefolder, name,
                 nrows = 1, ncols =1, sharex=False, sharey=False):
        
        self._setContext()
        
        self.figurefolder = pathlib.Path(figurefolder)
        self.name = name
        self.absoluteName = self.figurefolder / name
        self.fig, self.axList = matplotlib.pyplot.subplots( nrows = nrows, ncols=ncols, sharex=sharex, sharey=sharey, figsize=() )
        

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
    pass
#    def 
    
        
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
    def getEntrainment(folder = "/home/aholaj/case_isdac_LVL5_3D_iceD_inter_48h",
                kuvakansio = "/home/aholaj/OneDrive/000_WORK/000_ARTIKKELIT/000-Manuscript-ICE/kuvat/bini/",
                divergence = 5.e-6):
    ts = readDataset(folder, "ts")
    z = ts.zi1_bar.values
    t = ts.time.values
    dzdt = np.diff(z) / np.diff(t)
    we = xr.DataArray(dzdt + divergence*z[1:], dims={"h":ts.time.values[1:]/3600}, coords = {"time":ts.time.values[1:]/3600}, attrs={"longname":"Entrainment velocity", "units":"m/s"})
    return we
    

def main():
    pass
if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print("Script completed in " + str(round((end - start),0)) + " seconds")
