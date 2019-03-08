#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  4 16:27:25 2018

@author: aholaj
"""

from scipy.stats import lognorm
import numpy as np
#import matplotlib.pyplot as plt
import ModDataPros as mdp
from math import pi
from math import sqrt

def aeroDist( sigmag, dpg, n, xmax = 10., sample = 200 ):

    # sigmag = [ 1.5,    2.45 ] # Stdev for initial aerosol size distribution
    
    # dpg    = [ 0.2,    0.7  ] # Mode mean diameters in micrometers
    
    # n      = [ 155.24, 6.37 ] # Mode number concentrations in #/mg
    
    dist = np.empty(np.shape(sigmag) , dtype = object)
    
    for i in range(len(dist)):
        dist[i] = lognorm(  s = np.log( sigmag[i] ), loc= dpg[i], scale = 1./n[i] )
        
    x=np.linspace(0,xmax, sample)
    y=np.zeros(np.shape(x))
    for i in range(np.shape(sigmag)[0]):
        y = y + dist[i].pdf(x/dpg[i])
    
    return x, y

def aeroDist2( sigmag, dpg, n, xmax = 10, sample = 200, x = None ):

    GSD = sigmag #= [ 1.5,    2.45 ] # Stdev for initial aerosol size distribution
    
    CMD = dpg
    
    
    # n      = [ 155.24, 6.37 ] # Mode number concentrations in #/mg
    
    
    
#    for i in range(len(dist)):
#        dist[i] = lognorm([sigmag[i]],loc= dpg[i])
       
    if x is None:
        x=np.linspace(0,xmax, sample)
        
    y=np.zeros(np.shape(x))
    
    for i in range( len(x) ):
        y[i] = n/(sqrt(2.*pi)*np.log(GSD))*np.exp(- (1./2.)*np.power( ( np.log( x[i] ) - np.log( CMD ) )/( np.log( GSD ) ), 2) ) 
    
    return x, y

x1, y1 = aeroDist2( sigmag = 1.5, dpg = 0.2, n = 155.24, xmax = 100, sample = 10000 )#sigmag = [ 1.5, 2.45 ], dpg = [ 0.2,    0.7 ], n = [ 155.24, 6.37 ])
x2, y2 = aeroDist2( sigmag = 2.45, dpg = 0.7, n = 6.37, x = x1 )

x = x1
y = y1 +y2

fig, ax = mdp.plottaa( x, y, tit = 'Aerosol particle size distribution', xl = 'diam [' +r'$\mu$' + 'm]', yl = '', markers=False, uusikuva = True, LEGEND = True, omavari = 'k', a=10, b=20, log=True )

xticks = [0.1, 1, 10]
xlabels = list(map(str, xticks))
ax.set_xticks( xticks )
ax.set_xticklabels( xlabels )

x, y = aeroDist( sigmag = [ 1.5, 2.45 ], dpg = [ 0.2,    0.7 ], n = [ 155.24, 6.37 ])

fig, ax = mdp.plottaa( x, y, tit = 'Aerosol particle size distribution', xl = 'diam [' +r'$\mu$' + 'm]', yl = '', markers=False, uusikuva = True, LEGEND = True, omavari = 'k', a=10, b=20, log=True )

xticks = [0.1, 1, 10]
xlabels = list(map(str, xticks))
ax.set_xticks( xticks )
ax.set_xticklabels( xlabels )
