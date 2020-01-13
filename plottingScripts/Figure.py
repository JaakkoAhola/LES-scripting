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
                 nrows = 1, ncols =1, sharex=False, sharey=False):
        
        self._setContext()
        
        self.figurefolder = pathlib.Path(figurefolder)
        self.name = name
        self.absoluteName = self.figurefolder / name
        self.fig, self.axes = matplotlib.pyplot.subplots( nrows = nrows, ncols=ncols, sharex=sharex, sharey=sharey, figsize=(matplotlib.rcParams['figure.figsize']) )
    
    def getFig(self):
        return self.fig
    
    def getAxes(self, getFlatten = False):
        axes = self.axes
        if getFlatten:
            axes =  numpy.asarray(self.axes).flatten()
        else:
            axes =  self.axes
        
        return axes

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