#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 13:14:55 2020

@author: Jaakko Ahola, Finnish Meteorological Institute
@licence: MIT licence Copyright
"""
import numpy
import pathlib
import xarray

class Simulation:
    
    def __init__(self, folder, label, color, linewidth = None):
        self.folder = pathlib.Path(folder)
        self.label = label
        self.color = color
        self.nc = None
        self.ps = None
        self.ts = None
        self.linewidth = linewidth
        
    def getColor(self):
        return self.color
    
    def getLabel(self):
        return self.label
    
    def getLineWidth(self):
        return self.linewidth
        
    def getNCDataset(self):
        if self.nc is None:
            self.nc = self._getDataset("nc")
                
        return self.nc
    
    def getPSDataset(self):
        if self.ps is None:
            self.ps = self._getDataset("ps")
        
        return self.ps
    
    def getTSDataset(self):
        if self.ts is None:
            self.ts = self._getDataset("ts")
        
        
        return self.ts
    
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
            raise FileNotFoundError(ncMode, "file not found from", self.folder)
        
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

    
    def setUnitToLatexMathMode(dataset):
        dataset.attrs["units"] = r'$' + dataset.attrs["units"] + '$'
        return dataset
    
    def setTimeCoordToHours(self):
        if self.nc is not None:
            self.nc = self.nc.assign_coords(time = (self.nc.time / 3600))
        if self.ps is not None:
            self.ps = self.ps.assign_coords(time = (self.ps.time / 3600))
        if self.ts is not None:
            self.ts = self.ts.assign_coords(time = (self.ts.time / 3600))
            
    def setLineWidth(self, linewidth):
        self.linewidth = linewidth