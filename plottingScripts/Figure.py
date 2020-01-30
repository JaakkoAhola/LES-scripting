#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 13:16:21 2020

@author: Jaakko Ahola, Finnish Meteorological Institute
@licence: MIT licence Copyright
"""
import matplotlib
import numpy
import pathlib
import seaborn

class Figure:
    
    def __init__(self, figurefolder, name,
                 nrows = 1, ncols =1, sharex=False, sharey=False, style = "seaborn-paper"):
        
        self._setContext(style)
        
        self.figurefolder = pathlib.Path(figurefolder)
        self.name = name
        self.absoluteName = self.figurefolder / name
        self.fig, self.axes = matplotlib.pyplot.subplots( nrows = nrows, ncols=ncols, sharex=sharex, sharey=sharey, figsize=(matplotlib.rcParams['figure.figsize']) )
        self.oldContextValues = {}
        
    def getFig(self):
        return self.fig
    
    def getAxes(self, getFlatten = False):
        if getFlatten:
            axes =  numpy.asarray(self.axes).flatten()
        else:
            axes =  self.axes
        
        return axes
    
    def getOldContextValues(self):
        return self.oldContextValues

    def modifyContext(self, parameter, factorForOldValue = None, newValue = None):
        self.oldContextValues[ parameter ] = matplotlib.rcParams[parameter]
        
        if factorForOldValue is not None:
            matplotlib.rcParams[ parameter ] = Figure._modifyContextFactor(parameter, factorForOldValue)
        elif newValue is not None:
            matplotlib.rcParams[ parameter ] = newValue
            

    def _modifyContextFactor(parameter, factorForOldValue ):
        if isinstance(matplotlib.rcParams[parameter], int):
            newValue = matplotlib.rcParams[parameter] * factorForOldValue
            
        elif isinstance(matplotlib.rcParams[parameter], list):
            newValue = list(numpy.asarray(matplotlib.rcParams[parameter])*factorForOldValue)
            
        return newValue

    def _setContext(self, style = "seaborn-paper", printing = False):
        matplotlib.rcParams.update(matplotlib.rcParamsDefault)
        matplotlib.pyplot.style.use(style)
#        seaborn.set_context("poster")
#        matplotlib.rcParams['figure.figsize'] = list(numpy.asarray(matplotlib.rcParams["figure.figsize"])*2)
#        if printing: print('figure.figsize', matplotlib.rcParams['figure.figsize'])
#    
#        if printing: print('figure.dpi', matplotlib.rcParams['figure.dpi'])
        matplotlib.rcParams['savefig.dpi'] = 300.
#        if printing: print('savefig.dpi', matplotlib.rcParams['savefig.dpi'])
#        matplotlib.rcParams['legend.fontsize'] = 14
#        if printing: print('legend.fontsize', matplotlib.rcParams['legend.fontsize'])
#        matplotlib.rcParams['axes.titlesize'] = 42
#        matplotlib.rcParams['axes.labelsize'] = 42
#        matplotlib.rcParams['xtick.labelsize'] = 42 #22
#        matplotlib.rcParams['ytick.labelsize'] = 42 #22
        matplotlib.rcParams['font.weight']= 'bold' #this should be changed
#        if printing: print('axes.titlesize', matplotlib.rcParams['axes.titlesize'])
#        if printing: print('axes.labelsize', matplotlib.rcParams['axes.labelsize'])
#        if printing: print('xtick.labelsize', matplotlib.rcParams['xtick.labelsize'])
#        if printing: print('ytick.labelsize', matplotlib.rcParams['ytick.labelsize'])
#        if printing: print("lines.linewidth", matplotlib.rcParams['lines.linewidth'])
#        matplotlib.rcParams['text.latex.unicode'] = False
#        matplotlib.rcParams['text.usetex'] = False
#        if printing: print("text.latex.unicode", matplotlib.rcParams['text.latex.unicode'])
#        matplotlib.rcParams['text.latex.preamble']=[r'\usepackage{amsmath}']
        matplotlib.rc('text', usetex = False)
    
    def setAdjusting(self, hspace = 0.05, wspace = 0.05, left = None, right = None, top = None, bottom = None):
        self.fig.subplots_adjust( hspace=hspace, wspace = wspace, left = left, right = right, top = top, bottom = bottom)
        
    #, padding = 0.06, bbox_inches = "tight"
    def save(self, file_extension = ".pdf", useTight = True, close = True):
        if useTight:
            self.fig.tight_layout()
            
        #self.fig.savefig( self.absoluteName.with_suffix( file_extension ), pad_inches = padding, bbox_inches = bbox_inches )
        self.fig.savefig( self.absoluteName.with_suffix( file_extension ))
        
        if close:
            matplotlib.pyplot.close()