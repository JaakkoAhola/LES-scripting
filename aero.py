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
import matplotlib as mpl
import seaborn as sns
import sys
#import plotLesOutput as pl
#import time
#tic = time.clock()













plt.style.use('seaborn-paper')
sns.set_context("poster")
mpl.rcParams['figure.figsize'] = [mpl.rcParams['figure.figsize'][0]*2.0, mpl.rcParams['figure.figsize'][1]*2.0]
print('figure.figsize', mpl.rcParams['figure.figsize'])

print('figure.dpi', mpl.rcParams['figure.dpi'])
mpl.rcParams['savefig.dpi'] = 300.
print('savefig.dpi', mpl.rcParams['savefig.dpi'])
mpl.rcParams['legend.fontsize'] = 14
print('legend.fontsize', mpl.rcParams['legend.fontsize'])
picturefolder = os.environ["HOME"] + "/Dropbox/Ilmatieteen_Laitos/artikkelit/First_draft_acp/kuvat/"

nconc = np.asarray([155.24,    6.37])
ice = range(1,4)
aero = [0.1, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
muuttuja = 'lwp_bar'

prinTaulukko = False
printTestiAjotKomennot = False
plotIcingTime = False
plotMuuttujaAsFunctionOfAeroConc = True
if prinTaulukko:
    ###############
    #
    # print taulukon eka rivi
    # 
    ################
    
    print(muuttuja.ljust(22) + " & ", end="")
    for st in range(len(ice)):
        st1 = "ice " + str(ice[st])
        if st != ice.index(ice[-1]):
            print( st1.ljust(11), end = "& ")
        else:
            print( st1.ljust(11), end = '\\\\ ')
    print(" ")
    print("-"*131)
    
    
    ###############
    #
    # print ice-aero taulukko
    # 
    ################
    
    yht = len(aero)*len(ice)
    for aeroK in range(len(aero)) :
        k = 0
        for iceK in range(len(ice)):
            vec = nconc*aero[aeroK]
            string="testinumero=v5.2_RadiationOn_aero"+ str(aero[aeroK])   +" ice=" + str(float(ice[iceK])/1.) + " n='" + "{0:7.3f}".format(vec[0])+"," +  "{0:7.3f}".format(vec[1])+", 0., 0., 0., 0. 0.'"                ' iradtyp=3 case_name="default" jaakkoNL=false th00=263. sound_in=sound_in3.5 LVL=5 submit=true exe=les.mpi.Jaakko.JJAv5.2.intel.fast dim3=true ${SCRIPT}/testiajot.bash'
            #print(string)
            file = "case_isdac_LVL5_2D_ice" + str(ice[iceK]) + "_v5.2_RadiationOn_aero" + str(aero[aeroK])
            #print(" ")
            #print(file)
            
            lustre = os.environ["LUSTRE"]
            
            #os.chdir("/home/aholaj/mounttauskansiot/lustremount/UCLALES-SALSA")
            dataset = xr.open_dataset( lustre + "/ISDAC/ISDAC_Radiation_aero/" + file + "/" + file + ".ts.nc" )
            alku = dataset.time[-1].values - np.asarray(3600.)
            alkuI = np.argmin( np.abs( dataset.time - alku ))
            alkuI = alkuI.values
            loppuI = len(dataset.time)
            #print(alkuI)
            #print(loppuI)
            ka = np.mean(dataset[muuttuja].isel(time=range(alkuI,loppuI)))*1000.
            
            if k == 0:
                #print('aero ' + str(aeroK).ljust(10) + " |", end='')
                print("n=  {0:7.3f}, {1:7.3f}   &".format(vec[0], vec[1]).ljust(8) + " ", end='')
            
            if iceK  != ice.index(ice[-1]):
                print( str(round(float(ka.values),2)).ljust(10) + " & ", end='')
            else:
                print( str(round(float(ka.values),2)).ljust(10) + " \\\\ ", end='')
                #print("poop" + " \\\\ ", end='')
            k += 1
            
            
        print("")
        print("\\hline")
    
    
    
if printTestiAjotKomennot:
    ################
    ##
    ## print ice-aero testi-ajot komennot
    ## 
    #################
    
    
    
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


if plotIcingTime:
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
        
        
if plotMuuttujaAsFunctionOfAeroConc:
    colorsice1234 = ["#f58231","#f032e6","#469990","#4363d8"]
    newfig = True
    saveTag = "asFuncOfAeroConc"
    for aeroK in range(len(aero)) :
        for iceK in range(len(ice)):
            vec = nconc*aero[aeroK]        
            print(aero[aeroK], nconc,vec, sum(vec), end = " ")
            file = "case_isdac_LVL5_3D_ice" + str(ice[iceK]) + "_v5.2_RadiationOn_aero" + str(aero[aeroK])
            print(file, end = " ")
            juuri = os.environ["IBRIX"]
            
            kokopolku = juuri + "/ISDAC/ISDAC_Radiation_aero3D/" + file + "/" + file 
            paateTS =  ".ts.nc"
            paateNC = ".nc"
            
            filenameNC = kokopolku + paateNC
            
            filenameTS = kokopolku + paateTS
            
            dataset = xr.open_dataset( filenameTS )
            
            
            q_data = mdp.read_Data( filenameNC, "q" )
            l_data = mdp.read_Data( filenameNC, "l" )
            r_data = mdp.read_Data( filenameNC, "r" )
            
            
            time_data = mdp.read_Data( filenameNC, 'time'   )
            dn0_data  = mdp.read_Data( filenameNC, 'dn0'    )
            zt_data   = mdp.read_Data( filenameNC, 'zt'     )
            zm_data   = mdp.read_Data( filenameNC, 'zm'     )
            
            korkeus = ( zm_data - zt_data )*2.0
            
            mdp.laske_path_aikasarjaXYZ
            
            
            
            
            
            print(q_rat-l_rat-r_rat)
            
            
            
            alku = dataset.time[-1].values - np.asarray(3600.)*2. #last two hours
            alkuI = np.argmin( np.abs( dataset.time - alku ))
            alkuI = alkuI.values
            loppuI = len(dataset.time)
            #print(alku, end=" ")
            #print(alkuI)
            #print(loppuI)
            ka = np.mean(dataset[muuttuja].isel(time=range(alkuI,loppuI)))*1000.
            print(l_rat - dataset[muuttuja].values )
            print(ka.values)
            mdp.plottaa(sum(vec), ka, uusikuva= newfig, scatter = True, omavari=colorsice1234[iceK], yl = r'[$10^{-3}kg/m^2$]', xl = r'[$\#/10^{-6}kg$]', LEGEND=False )
            newfig = False
            
            
            
            
    plt.savefig( picturefolder + muuttuja + "_" + saveTag + '.png')
            
            
            
            
            
            
            
            
            
            