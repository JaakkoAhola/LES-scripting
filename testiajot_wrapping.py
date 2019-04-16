#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 17:43:12 2019

@author: aholaj
"""
import numpy as np
import xarray as xr
import subprocess
import os
global skripti
skripti = os.environ["SCRIPT"]
global debug



def ajakomento(testinumero     = "interactive",\
qsub            = "true",\
interactive     = "true",\
n               = "155.24,6.37,0.,0.,0.,0.,0.'",\
nspec           = "2",\
listspec        = '"SO4","DU","","","","",""',\
volDistA        = '0.99,0.,0.,0.,0.,0.,0.',\
volDistB        = '0.01,1.,0.,0.,0.,0.,0.',\
nf2a            = "0.999",\
isoT            = "28800.",\
pikkuT          = "120.",\
nudge_time      = "0.",\
frqhis          = "180000.",\
iradtyp         = "3",\
case_name       = '"default"',\
jaakkoNL        = "false",\
th00            = "263.",\
sound_in        = "sound_in3.5",\
LVL             = "5",\
submit          = "true",\
exe             = "les.mpi.Jaakko.JJAv5.2.1.intel.fast",\
dim1            = "false",\
dim2            = "false",\
dim3            = "false",\
extra           = None \
):

    komento= ["testinumero=" + testinumero, \
    "qsub=" + qsub, \
    "interactive=" + interactive, \
    "n=" + n, \
    "nspec=" + nspec, \
    "listspec=" + listspec, \
    "volDistA=" + volDistA, \
    "volDistB=" + volDistB, \
    "nf2a=" + nf2a, \
    "isoT=" + isoT, \
    "pikkuT=" + pikkuT, \
    "nudge_time=" + nudge_time, \
    "frqhis=" + frqhis, \
    "iradtyp=" + iradtyp, \
    "case_name=" + case_name, \
    "jaakkoNL=" + jaakkoNL, \
    "th00=" + th00, \
    "sound_in=" + sound_in, \
    "LVL=" + LVL, \
    "submit=" + submit, \
    "exe=" + exe, \
    "dim1=" + dim1, \
    "dim2=" + dim2, \
    "dim3=" + dim3, \
    skripti + "/" + "testiajot.bash"]

    if extra is not None:
        for ex in extra:
            komento.insert(-1, ex)
    komentoS = " ".join(komento)
    if debug:
        print(komentoS)
        print(" ")
    else:
        os.system(komentoS)

    return komento

def analysoiPrinttaaTaulukko( muuttuja = "iwp_bar",\
testinumero     = "interactive",\
ice             = "1",\
dim1            = "false",\
dim2            = "true",\
dim3            = "false",\
rootfolder      = "LUSTRE",\
valihakemisto   = "",\
ekarivi         = False,\
normirivi       = False,\
vika            = False\
):


    if dim1 == "true":
        dimensio = "1D"
    elif dim2 == "true":
        dimensio = "2D"
    elif dim3 == "true":
        dimensio = "3D"

    file = "case_isdac_LVL5_" + dimensio + "_ice" + ice + "_"  + testinumero

    print(" ")
    print(file)

    highfolder = os.environ[rootfolder]


    dataset = xr.open_dataset( highfolder + valihakemisto + file + "/" + file + ".ts.nc" )
    alku = dataset.time[-1].values - np.asarray(3600.) # viimeisen tunnin alkuarvo
    alkuI = np.argmin( np.abs( dataset.time - alku )) # viimeisen tunnin alkuindeksi
    alkuI = alkuI.values # arvo viimeisen tunnin alussa
    loppuI = len(dataset.time) # viimeisen hetken aikaindeksi

    ka = np.mean(dataset[muuttuja].isel(time=range(alkuI,loppuI)))*1000.

    if ekarivi:
        print(muuttuja.ljust(22) + " & ", end="")
        for st in range(len(ice)):
            st1 = "ice " + str(ice[st])
            if st != ice.index(ice[-1]):
                print( st1.ljust(11), end = "& ")
            else:
                print( st1.ljust(11), end = '\\\\ ')
        print(" ")
        print("-"*131)

        #print('aero ' + str(aeroK).ljust(10) + " |", end='')
        print("n=  {0:7.3f}, {1:7.3f}   &".format(vec[0], vec[1]).ljust(8) + " ", end='')

    if iceK  != ice.index(ice[-1]):
        print( str(round(float(ka.values),2)).ljust(10) + " & ", end='')
    else:
        print( str(round(float(ka.values),2)).ljust(10) + " \\\\ ", end='')
            #print("poop" + " \\\\ ", end='')



def interactive_aero_testi( testinumeroetuliite, aero, nconc, nf2aList, volList, exeList = ["les.mpi.Jaakko.JJAv5.2.1.intel.fast"], aja = False, analysoi = False, extra = None ):
    for aeroK in range(len(aero)) :
        for frac in range(len(nf2aList)):
            for indVola in range(len(volList)):
                for exe in range(len(exeList)):
                    mis = str(round(exeList[exe],1))
                    volaA = volList[indVola]
                    volaB = 1.-volaA
                    vec = nconc*aero[aeroK]
                    n = str(round(vec[0],3))+"," +  str(round(vec[1],3))+",0.,0.,0.,0.,0."
                    volDistA        = str(round(volaA,2))+ ',0.,0.,0.,0.,0.,0.'
                    volDistB        = str(round(volaB,2))+ ',1.,0.,0.,0.,0.,0.'
                    nf2a = str( nf2aList[frac] ) #ound(nf2aList[frac],3)
                    duConc = str(round((1-nf2aList[frac])*(vec[0] + vec[1] )*1000.,2))
                    print("DUST " + duConc + " #/g")
                    testinumero = testinumeroetuliite + "DU_" +duConc +"g"   # "nf2a" + nf2a + + str(aero[aeroK]) +"volA" + str(round(volaA,2))+
                    if aja:
                        #ajakomento(qsub="true", n = n, nf2a = nf2a, volDistA=volDistA, volDistB=volDistB, testinumero = testinumero, extra = extra, dim1 = "true", exe = "les.seq.Jaakko.JJAv5.2.1.intel.fast" )
                        ajakomento(qsub="true", n = n, nf2a = nf2a, volDistA=volDistA, volDistB=volDistB, testinumero = testinumero, extra = extra, dim3 = "true", exe = "les.mpi.Jaakko.IceV1.0.mis" + mis + ".intel.fast", pikkuT = "7200.")
                    if analysoi:
                        analysoiPrinttaaTaulukko(testinumero = testinumero)

def giveList_nf2a(sumnconc, duTargetList):
    nf2aList= [];
    for du in duTargetList:
        nf2aList.append(1-du/(sumnconc))
    return nf2aList

aero        = [1.0] #[0.5, 1.5] #[0.75, 1.0, 1.25] #[0.1, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
#nf2aList    = np.arange(0.99, 0.999, 0.001)
#nf2aList    = np.append(nf2aList, 0.999)
#nf2aList    = [0.99, 0.995, 0.998, 0.9985, 0.99845]

#nf2aList    = [0.9907930529705776,
# 0.9953965264852888,
# 0.9976982632426444,
# 0.9988491316213222,
# 0.9994245658106611,
# 0.9997122829053305,
# 0.9998561414526653,
# 0.9999280707263326,
# 0.9999640353631664,
# 0.9999820176815831]

#nf2aList = [0.9999640353631664]

#volList = np.arange(0.5, 0.91, 0.1)
#volList = np.append(volList, 0.99)
volList = [0.99]
print(volList)

exeList = [0.7] #np.arange(0.1, 0.91, 0.1)
print(exeList)
testinumeroetuliite = ""
nconc = np.asarray([155.24,    6.37])
sumnconc = np.sum(nconc)
dulist = np.concatenate( (np.asarray([1.]), np.arange(2.5, 10.1, 2.5)) )*1e-3

nf2aList = giveList_nf2a( sumnconc, dulist  )
nf2aList = np.flip( nf2aList )
nf2aList = np.insert( nf2aList, 0 , 0.9999640353631664 ) 
print(nf2aList)

debug = False


interactive_aero_testi( testinumeroetuliite, aero, nconc, nf2aList, volList, exeList=exeList, aja = True, extra = ["nlcoag=.TRUE."])
