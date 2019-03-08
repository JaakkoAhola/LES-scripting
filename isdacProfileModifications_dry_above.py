#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 28 13:38:05 2018

@author: aholaj
"""

import numpy as np

import sound_in_profiles as sp

import PythonMethods as pm

import ModDataPros as mdp

from copy import deepcopy

from FindCloudBase import calc_rh_profile
from ECLAIR_calcs import calc_rw

import time

start = time.time()


isdac = sp.Profiles("sound_in3.5","bin/case_isdac")

rh = isdac.getRH()

q  = isdac.getQ()

z  = isdac.getZ()

t  = isdac.getT()

p  = isdac.getPS()

u  = isdac.getU()

v  = isdac.getV()


osc=rh-100.*np.ones(np.shape(rh))
ab=osc[0];
for s in range(len(osc)):
    if np.sign(ab)*np.sign(osc[s]) == -1:
        print(s)
    ab = osc[s]
    

dry0 = 236
dryL =364
#size = 40
rh_target = 20
rh_mod = deepcopy(rh)

rh_mod[dry0:(dryL+1)] = rh_target
#
#

#for kk in xrange(dry0,(dryL+1)):
#    
#    q_mod[kk] = 1000.*calc_rw( rh[kk], t[kk], p[kk] ) 


z[0] = isdac.getP0()
#
q_mod = deepcopy(q)
q_mod = np.multiply(q_mod, 1.e-3)
rh_temp = 100000.*np.ones(np.shape(rh))



for i in range(dry0,dryL+1): #size
    k = 1
    incr = 1. #1.e-6
    incr = incr*1.e-3
    etumerkki = 1.
    print('z', i)
    vanha = np.abs( rh_temp[i] - rh_mod[i] )
    switchCount = 0
    while (( vanha > 0.01 )  and (switchCount < 300)): #and (k < 10000)
        
        q_mod[i] =  np.max(q_mod[i]-etumerkki*k*incr,0)
        
        rh_temp, b = calc_rh_profile( t, q_mod,   z )
        uusi = np.abs( rh_temp[i] - rh_mod[i] )
        
        if uusi-vanha > 0:
            print('switch')
            etumerkki = -1*etumerkki
            incr = incr*1.e-1
            switchCount += 1
        incr = max(incr, 1.e-9)    
        vanha = uusi    
        k += 1
        print(uusi, rh_temp[i], rh_mod[i])
        
    
    print('q[i]', q[i], 'q_mod[i]', q_mod[i]*1.e+3)
    print(' ')    

rh_iter, ps_iter = calc_rh_profile( t, q_mod,  z )


q_mod = np.multiply(q_mod, 1.e3)
#isdac.writeNewSoundIn("sound_in3.5_rh_dry_above_"+str(rh_target), z, t, q_mod, u, v)
    

#####################
### plotting ########
####################
z[0] = 0.

fig, ax = mdp.plottaa( rh, z, tit = 'Relative humidity', xl = 'rel. humid. [%]', yl = 'height [m]', markers=False, uusikuva = True, LEGEND = True, omavari = 'k' )

fig, ax = mdp.plottaa( rh_mod[dry0-1:(dryL+1)+1], z[dry0-1:(dryL+1)+1], tit = 'Relative humidity dry-above', xl = 'rel. humid. [%]', yl = 'height [m]', markers=False, uusikuva = False, LEGEND = True, omavari = 'r' )

#mdp.plottaa( rh_iter[dry0:(dryL+1)], z[dry0:(dryL+1)], tit = 'Relative humidity dry-above iterated', xl = 'rel. humid. [%]', yl = 'height [m]', markers=False, uusikuva = False, LEGEND = True, omavari = 'b' )
xticks = list(range(0, 111, 10))
xlabels = list(map(str, xticks))
ax.set_xticks( xticks )
ax.set_xticklabels( xlabels )

####################
mdp.plottaa( q, z, tit = 'Total water mixing ratio', xl = 'mix. rat. [g/kg]', yl = 'height [m]', markers=False, uusikuva = True, LEGEND = True, omavari = 'k' )

mdp.plottaa( q_mod[dry0:(dryL+1)], z[dry0:(dryL+1)], tit = 'Total water mixing ratio dry-below', xl = 'mix. rat. [g/kg]', yl = 'height [m]', markers=False, uusikuva = False, LEGEND = True, omavari = 'b' )



mdp.plot_lopetus()
#




end = time.time()

print('suoritusaika', end-start)