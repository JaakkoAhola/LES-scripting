#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  4 12:52:08 2018

@author: aholaj
"""
import os
import numpy as np
import xarray as xr

import ModDataPros as mdp
import matplotlib.pyplot as plt
import sys
nconc = np.asarray([155.24,    6.37])
ice = range(1,5)
aero = [0.1, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
muuttuja = 'iwp_bar'
#print(muuttuja.ljust(22) + " & ", end="")
#for st in range(len(ice)):
#    st1 = "ice " + str(ice[st])
#    if st != ice.index(ice[-1]):
#        print( st1.ljust(11), end = "& ")
#    else:
#        print( st1.ljust(11), end = '\\\\ ')
#print(" ")
#print("-"*131)

#
#yht = len(aero)*len(ice)
#for aeroK in range(len(aero)) :
#    k = 0
#    for iceK in range(len(ice)):
#        vec = nconc*aero[aeroK]
#        string="testinumero=v5.2_RadiationOn_aero"+ str(aero[aeroK])   +" ice=" + str(float(ice[iceK])/1.) + " n='" + "{0:7.3f}".format(vec[0])+"," +  "{0:7.3f}".format(vec[1])+", 0., 0., 0., 0. 0.'"                ' iradtyp=3 case_name="default" jaakkoNL=false th00=263. sound_in=sound_in3.5 LVL=5 submit=true exe=les.mpi.Jaakko.JJAv5.2.intel.fast dim3=true ${SCRIPT}/testiajot.bash'
#        #print(string)
#        file = "case_isdac_LVL5_2D_ice" + str(ice[iceK]) + "_v5.2_RadiationOn_aero" + str(aero[aeroK])
#        #print(" ")
#        #print(file)
#        
#        lustre = os.environ["LUSTRE"]
#        
#        #os.chdir("/home/aholaj/mounttauskansiot/lustremount/UCLALES-SALSA")
#        dataset = xr.open_dataset( lustre + "/ISDAC/ISDAC_Radiation_aero/" + file + "/" + file + ".ts.nc" )
#        alku = dataset.time[-1].values - np.asarray(3600.)
#        alkuI = np.argmin( np.abs( dataset.time - alku ))
#        alkuI = alkuI.values
#        loppuI = len(dataset.time)
#        #print(alkuI)
#        #print(loppuI)
#        ka = np.mean(dataset[muuttuja].isel(time=range(alkuI,loppuI)))*1000.
#        
#        if k == 0:
#            #print('aero ' + str(aeroK).ljust(10) + " |", end='')
#            print("n=  {0:7.3f}, {1:7.3f}   &".format(vec[0], vec[1]).ljust(8) + " ", end='')
#        
#        if iceK  != ice.index(ice[-1]):
#            print( str(round(float(ka.values),2)).ljust(10) + " & ", end='')
#        else:
#            print( str(round(float(ka.values),2)).ljust(10) + " \\\\ ", end='')
#            #print("poop" + " \\\\ ", end='')
#        k += 1
#        
#        
#    print("")
#    print("\\hline")


#sys.exit()
icingTime = np.zeros( ( len(aero),len(ice) ) )    
yht = len(aero)*len(ice)
for aeroK in range(len(aero)) :
    
    for iceK in range(len(ice)):
        vec = nconc*aero[aeroK]
        string="testinumero=v5.2_RadiationOn_aero"+ str(aero[aeroK])   +" ice=" + str(float(ice[iceK])/1.) + " n='" + "{0:7.3f}".format(vec[0])+"," +  "{0:7.3f}".format(vec[1])+", 0., 0., 0., 0. 0.'"                ' iradtyp=3 case_name="default" jaakkoNL=false th00=263. sound_in=sound_in3.5 LVL=5 submit=true exe=les.mpi.Jaakko.JJAv5.2.intel.fast dim3=true ${SCRIPT}/testiajot.bash'
        print(string)
#        file = "case_isdac_LVL5_2D_ice" + str(ice[iceK]) + "_v5.2_RadiationOn_aero" + str(aero[aeroK])
#        
#        lustre = os.environ["IBRIX"]
#        
#        kokopolku = lustre + "/ISDAC/ISDAC_Radiation_aero/" + file + "/" + file + ".ts.nc"
#        
#        dataset = xr.open_dataset( kokopolku )
##        print(dataset['iwp_bar'].where(dataset['iwp_bar'] < 1e-5, True, False).values)
#        
#        aikaSpinup = np.argmin( np.abs( dataset["time"].values - 2*3600.)) +1
#        valla = dataset['iwp_bar'].values[ aikaSpinup : ]*1000.
#        try:
#            icingTime[aeroK,iceK] = dataset["time"].values[next(i for i,v  in enumerate(valla) if v < 0.01)]
#            
#        except StopIteration:
#            icingTime[aeroK,iceK] = 0.
#            continue
sys.exit()    
icingTime = icingTime/3600.
colorMap = mdp.truncate_colormap(  plt.cm.Greys, minval = 0.3)
newfig = True

for aeroK in range(len(aero)) :
    for iceK in range(len(ice)):
        aerosolConc = aeroK + 1
        mdp.plottaa([iceK+1], icingTime[aeroK, iceK], uusikuva= newfig, scatter = True, omavari=colorMap(aerosolConc/len(aero)))
        newfig = False
mdp.plot_lopetus()        
#        for t in range(len(dataset.time)):
#            path = dataset[muuttuja].isel(time=t)*1000.
#            
#            if path.values > 0.01:
#                continue    
#            print (path.values, t)
            
                
#                print(ice[iceK], aero[aeroK], dataset.time[t].values)
#                break
        
        
        
