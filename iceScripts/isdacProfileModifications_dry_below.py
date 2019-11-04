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

size = 40
rh_mod_part = []
for zz in z[0:size]:
    rh_mod_part.append( pm.giveValue(zz,  0., z[39], 80., rh[39]  ) )

rh_mod = deepcopy(rh_mod_part)
rh_mod.extend(rh[size:])



#for kk in xrange(len(rh_mod_part)):
#    
#    q_mod_part.append( 1000.*calc_rw( rh[kk], t[kk], p[kk] ) )
#
#q_mod = deepcopy(q_mod_part)
#q_mod.extend(q[size:])
z[0] = isdac.getP0()

qq_modaa = deepcopy(q)
qq_modaa = np.multiply(qq_modaa, 1.e-3)
rh_temp = 100000.*np.ones(size)
point = 0
for i in range(point+1): #size
    k = 1
    incr = 1.e-6 #1.e-6
    incr = incr*1.e-3
    etumerkki = 1.
    print('z', i)
    vanha = np.abs( rh_temp[i] - rh_mod[i] )
    
    while (( vanha > 0.01 ) or (k < 3)):
        
        qq_modaa[i] =  np.max(qq_modaa[i]-etumerkki*k*incr,0)
        
        rh_temp, b = calc_rh_profile( t, qq_modaa,   z )
        uusi = np.abs( rh_temp[i] - rh_mod[i] )
        
#        if uusi-vanha > 0:
#            #print 'switch'
#            etumerkki = -1*etumerkki
        vanha = uusi    
        k = k + 1
        print(uusi, rh_temp[i], rh_mod[i])
        
    #q_mod_part[i] = q[i]-k*incr
    
    print('q[i]', q[i], 'qq_modaa[i]', qq_modaa[i]*1.e+3)
    

#q_mod = np.concatenate( ( q_mod_part,q[size:] ) )
q_mod = np.zeros(size)
q_mod[0] = qq_modaa[0]*1.e+3
for zi in range(1,size):
    q_mod[zi] =  pm.giveValue(z[zi],  0., z[size-1], qq_modaa[point]*1.e+3, q[size-1]  )  # giveValue( z,  z1, z2, V1, V2  )
    
q_mod = np.concatenate( ( q_mod,q[size:] ) )
rh_iter, ps_iter = calc_rh_profile( t, np.multiply( q_mod, 1.e-3),  z )

#isdac.writeNewSoundIn("sound_in3.5_rh_dry_below_80", z, t, q_mod, u, v)
#####################
### plotting ########
####################
z[0] = 0.

fig, ax = mdp.plottaa( rh, z, tit = 'Relative humidity', xl = 'rel. humid. [%]', yl = 'height [m]', markers=False, uusikuva = True, LEGEND = True, omavari = 'k' )

fig, ax = mdp.plottaa( rh_mod_part, z[0:40], tit = 'Relative humidity dry-below', xl = 'rel. humid. [%]', yl = 'height [m]', markers=False, uusikuva = False, LEGEND = True, omavari = 'r' )

#mdp.plottaa( rh_iter[0:40], z[0:40], tit = 'Relative humidity dry-below iterated', xl = 'rel. humid. [%]', yl = 'height [m]', markers=False, uusikuva = False, LEGEND = True, omavari = 'b' )

xticks = list(range(0, 111, 10))
xlabels = list(map(str, xticks))
ax.set_xticks( xticks )
ax.set_xticklabels( xlabels )
####################
mdp.plottaa( q, z, tit = 'Total water mixing ratio', xl = 'mix. rat. [g/kg]', yl = 'height [m]', markers=False, uusikuva = True, LEGEND = True, omavari = 'k' )

mdp.plottaa( q_mod[0:40], z[0:40], tit = 'Total water mixing ratio dry-below', xl = 'mix. rat. [g/kg]', yl = 'height [m]', markers=False, uusikuva = False, LEGEND = True, omavari = 'b' )



mdp.plot_lopetus()





end = time.time()

print('suoritusaika', end-start)