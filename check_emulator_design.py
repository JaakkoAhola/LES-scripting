#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 21 16:48:41 2016

@author: aholaj
"""

import numpy as np

#try:
#	PLOT = True
#	import matplotlib.pyplot as plt
#	print "matplotlib.pyplot imported"
#except ImportError:
#	PLOT = False

try:
	COLOR = True
	from termcolor import colored
	print('colored imported')
except ImportError: 
	COLOR = False

import emulator_inputs as ei
import ECLAIR_calcs
import sys
import os
import glob
import subprocess
import getopt
from itertools import cycle
from netCDF4 import Dataset
from math import acos
from math import pi
from datetime import datetime
from PythonMethods import stringToBoolean
from PythonMethods import Logger
from copy import deepcopy

global DAY
global explicitAerosol
global nroVariables

### default folder and design###########
ibrix = os.environ["IBRIXMOUNT"]
folder=ibrix+'/DESIGN/'
cwd = os.getcwd()
os.chdir(folder)
for file in glob.glob("*.csv"):
    designbasename=file
filu = folder+designbasename
os.chdir(cwd)
########################################

# default values
DAY = False
explicitAerosol = True
writeNetCDF = True


apu = []
for arra in sys.argv[1:]:
    if arra[0:2] == '--':
        apu.append(arra)
        
argv = apu        
try:
       opts, args = getopt.getopt(argv,"h:",[ \
                                             "netcdfwrite=",\
                                             "designfile=" \
                                             ])
except getopt.GetoptError:
   print('ERROR, usage: test.py -i <inputfile> -o <outputfile>')
   sys.exit(2)    

for opt, arg in opts:
    if opt == '-h':
        print('test.py -i <inputfile> -o <outputfile>')
        sys.exit()
        
    elif opt in ("--designfile"):
        filu = arg
        folder = os.path.dirname(os.path.realpath( filu ))    
            
    elif opt in ("--netcdfwrite"):
        writeNetCDF = stringToBoolean(arg)


    elif opt in ("--design"):
        design = arg


    
with open(filu) as ff:
    first_line = ff.readline()
    
    nroVariables = len(first_line.split(","))-1
    if "cos_mu" in first_line:
        DAY = True
    else:
        DAY = False
        
    if ("rdry_AS_eff" in first_line) or ("as" in first_line):
        explicitAerosol = True
    else:
        explicitAerosol = False

riviLKM = subprocess.check_output( "cat " + filu + " | wc -l ", shell=True).decode("utf-8")
nroCases = int( riviLKM )-1
etunolla = len(str(nroCases))

os.chdir(folder)
tag =subprocess.check_output("git describe --tags | tr -dc '[:alnum:].'", shell=True)   
tag = tag.decode("utf-8")

if writeNetCDF:
    ncfolder = ibrix + '/DESIGNnetcdf/' + tag + '/'
    subprocess.call(['mkdir','-p', ncfolder])
    
    sys.stdout = Logger(ncfolder + "design_" + tag  + "_checkup.txt" )


ljustN = 16  
print("")
print("Designfile:".ljust(ljustN)         + str(filu) + "\n" +\
      "Designversion:".ljust(ljustN)       + str(tag) + "\n" +\
      "Cases:".ljust(ljustN)          + str(nroCases) + "\n" +\
      "Daytime:".ljust(ljustN)             + str(DAY) + "\n" +\
      "Aerosol:".ljust(ljustN) + str(explicitAerosol) + "\n" +\
      "writeNetCDF:".ljust(ljustN) + str(writeNetCDF)  )


####################################################
design     = np.zeros( ( nroCases, nroVariables ) )
    
caselist   = np.chararray(nroCases, itemsize = etunolla)

q_inv     = np.zeros( nroCases )
tpot_inv  = np.zeros( nroCases )
lwp       = np.zeros( nroCases )
tpot_pbl  = np.zeros( nroCases )
pblh      = np.zeros( nroCases )
num_pbl   = np.zeros( nroCases )
q_pbl     = np.zeros( nroCases )
clw_max   = np.zeros( nroCases )
cloudbase = np.zeros( nroCases )
if DAY:
    cntlat   = np.zeros(nroCases)
if explicitAerosol:
    num_ks      = np.zeros( nroCases )
    num_as      = np.zeros( nroCases )
    num_cs      = np.zeros( nroCases )
    dpg_as = np.zeros( nroCases )


if (not DAY) and (not explicitAerosol):
        caselist,    design[:,0], design[:,1], design[:,2], design[:,3], design[:,4], design[:,5]                        = ei.read_design( filu, nroVariables = nroVariables, DAY = DAY, explicitAerosol = explicitAerosol )
elif DAY and (not explicitAerosol):
        caselist,    design[:,0], design[:,1], design[:,2], design[:,3], design[:,4], design[:,5], design[:,-1]          = ei.read_design( filu, nroVariables = nroVariables, DAY = DAY, explicitAerosol = explicitAerosol )
elif (not DAY) and explicitAerosol:
        caselist, design[:,0], design[:,1], design[:,2], design[:,3], design[:,4], design[:,5], design[:,6], design[:,7], design[:,8]               = ei.read_design( filu, nroVariables = nroVariables, DAY = DAY, explicitAerosol = explicitAerosol )
elif DAY and explicitAerosol:
        caselist, design[:,0], design[:,1], design[:,2], design[:,3], design[:,4], design[:,5], design[:,6], design[:,7], design[:,8], design[:,-1] = ei.read_design( filu, nroVariables = nroVariables, DAY = DAY, explicitAerosol = explicitAerosol )      




p_surf = 101780.

for i in range(nroCases):
    caselist[i] = str(caselist[i].decode("utf-8"))
    q_inv[i]    = design[ i, 0 ]
    tpot_inv[i] = design[ i, 1 ]
    lwp[i]      = design[ i, 2 ]
    tpot_pbl[i] = design[ i, 3 ]
    pblh[i]     = design[ i, 4 ]
    
    
    if DAY:
        cntlat[i] = acos(design[ i, -1 ])*180./pi
        
    if explicitAerosol:
        num_ks[i] = design[ i, 5 ]*1e-6
        num_as[i] = design[ i, 6 ]*1e-6
        num_cs[i] = design[ i, 7 ]*1e-6
        dpg_as[i] = design[ i, 8 ]*2e6
    else:
        num_pbl[i]  = design[ i, 5 ]        
    
    

    q_pbl[i]                            = ECLAIR_calcs.solve_rw_lwp( p_surf, tpot_pbl[i],lwp[i]*0.001, pblh[i]*100. ) # kg/kg 
    lwp_apu, cloudbase[i], pblh_m, clw_max[i] = ECLAIR_calcs.calc_lwp( p_surf, tpot_pbl[i] , pblh[i]*100., q_pbl[i] )

    q_pbl[i]     = q_pbl[i] * 1000. # kg/kg -> g/kg
    clw_max[i]   = clw_max[i] * 1000.
    pblh[i]      = pblh_m
    design[i,4]  = pblh[i]
    if DAY:
        design[i,-1] = cntlat[i]
    if explicitAerosol:
        design[ i, 5 ] = num_ks[i]
        design[ i, 6 ] = num_as[i]
        design[ i, 7 ] = num_cs[i]
        design[ i, 8 ] = dpg_as[i]

    
ekarivi = first_line.replace('"', '').replace("\n", "").split(",")
ekarivi[0] = "case"
ekarivi.append("cloudbase")
ekarivi.append("thickness")
ekarivi.append("q_pbl")
ekarivi.append("clw_max")

if explicitAerosol:
    ekarivi[ekarivi.index("rdry_AS_eff")] = "dpg_as"
if DAY:
    ekarivi[ekarivi.index("cos_mu")] = "cntlat"

tabs = np.zeros(len(ekarivi)) #[  7,  7,  9,  8, 10, 9, 8, 10, 10,  6]

tabs[0] = 6

units = deepcopy(ekarivi)

units[0] = "unit"
for k in range(1,len(ekarivi)):
    if ekarivi[k] in ["q_inv", "q_pbl", "clw_max"]:
        units[k] = "g/kg"
    elif ekarivi[k] in ["tpot_pbl", "tpot_inv"]:
        units[k] = "K"
    elif ekarivi[k] == "lwp":
        units[k] = "g/m^2"
    elif ekarivi[k] in ["pblh", "cloudbase" , "thickness" ]:
        units[k] = "m"
    elif ekarivi[k] in ["ks", "as", "cs", "num_pbl" ]:
        units[k] = "#/mg"
    elif ekarivi[k] == "dpg_as":    
        units[k] = "\u03BCm"
    elif ekarivi[k] == "cntlat":    
        units[k] = chr(176)
        
        

for k in range(np.size(design,1)):
    ind = k + 1 
    tabs[ind] = np.max([ len(str(round(np.max(design[:,k]),2))) + 2, len(ekarivi[ ind ])+1, len(units[ind]) +1 ])

i = ind    
i = i + 1
tabs[i] = np.max([ len(str( round(np.max( cloudbase ), 2) )) + 2, len( ekarivi[i])+1, len(units[i]) +1 ])

i = i + 1
tabs[i] = np.max([ len(str( round(np.max( pblh - cloudbase ), 2))) + 2, len( ekarivi[i])+1, len(units[i]) +1 ])

i = i + 1
#print("i",i, str( round(np.max( q_pbl ), 2)), max( len(str( round(np.max( q_pbl ), 2))) + 1, len( ekarivi[i])+1 ))
tabs[i] = np.max([ len(str( round(np.max( q_pbl ), 2))) + 2, len( ekarivi[i])+1, len(units[i]) +1 ])

i = i + 1
#print("i",i, str( round(np.max( q_pbl ), 2)), max( len(str( round(np.max( q_pbl ), 2))) + 1, len( ekarivi[i])+1 ))
tabs[i] = np.max([ len(str( round(np.max( clw_max ), 2))) + 2, len( ekarivi[i])+1, len(units[i]) +1 ])

tabs = tabs.astype(int)

#print(tabs)


printtaus = []

listtabs = tabs

Ltabs = len(tabs)
Stabs = sum(tabs)
tabs = cycle(tabs)    


temp = ''
for k in range(len(ekarivi)):
    temp = temp + ekarivi[k].rjust(listtabs[k])
printtaus.append(temp)

temp = ''
for k in range(len(units)):
    temp = temp + units[k].rjust(listtabs[k])
unittulostus = temp



if writeNetCDF:
    
    ncfile = Dataset( ncfolder + 'design_'+tag + '.nc', 'w', format='NETCDF4' )
    today = datetime.today()
    
    ncfile.description = "Design version " + tag + " and some additional derived variables"
    ncfile.history = "Created " + today.strftime("%d/%m/%y")
    ncfile.daytimesimulation = str(DAY)
    ncfile.aerosol = str(explicitAerosol)
    
    ncfile.createDimension('case', nroCases )
    
    q_inv_ncf         = ncfile.createVariable( 'q_inv',     np.dtype('float32').char, ('case') )
    q_inv_ncf[:]      = q_inv
    q_inv_ncf.unit    = "g/kg"
    
    tpot_inv_ncf      = ncfile.createVariable( 'tpot_inv',  np.dtype('float32').char, ('case') )
    tpot_inv_ncf[:]   = tpot_inv
    tpot_inv_ncf.unit = "K"
    
    clw_max_ncf      = ncfile.createVariable( 'clw_max',   np.dtype('float32').char, ('case') )
    clw_max_ncf[:]   = clw_max
    clw_max_ncf.unit = "g/kg"
    
    tpot_pbl_ncf      = ncfile.createVariable( 'tpot_pbl',  np.dtype('float32').char, ('case') )
    tpot_pbl_ncf[:]   = tpot_pbl
    tpot_pbl_ncf.unit = "K"
    
    pblh_ncf      = ncfile.createVariable( 'pblh',      np.dtype('float32').char, ('case') )
    pblh_ncf[:]   = pblh
    pblh_ncf.unit = "m"

    q_pbl_ncf      = ncfile.createVariable( 'q_pbl',     np.dtype('float32').char, ('case') )
    q_pbl_ncf[:]   = q_pbl
    q_pbl_ncf.unit = "g/kg"
    
    cloudbase_ncf      = ncfile.createVariable( 'cloudbase', np.dtype('float32').char, ('case') )
    cloudbase_ncf[:]   = cloudbase
    cloudbase_ncf.unit = "m"
    
    thickness_ncf      = ncfile.createVariable( 'thickness', np.dtype('float32').char, ('case') )
    thickness_ncf[:]   = pblh - cloudbase
    thickness_ncf.unit = "m"
    
    if DAY:
        cntlat_ncf  = ncfile.createVariable( 'cntlat', np.dtype('float32').char, ('case') )
        cntlat_ncf[:] = cntlat
        cntlat_ncf.unit =chr(176)
        
    if explicitAerosol:
        num_ks_ncf         = ncfile.createVariable( 'num_ks', np.dtype('float32').char, ('case') )
        num_ks_ncf[:]      = num_ks
        num_ks_ncf.unit        = "#/mg"
        
        num_as_ncf         = ncfile.createVariable( 'num_as', np.dtype('float32').char, ('case') )
        num_as_ncf[:]      = num_as
        num_as_ncf.unit    = "#/mg"
        
        num_cs_ncf         = ncfile.createVariable( 'num_cs', np.dtype('float32').char, ('case') )
        num_cs_ncf[:]      = num_cs
        num_cs_ncf.unit    = "#/mg"
        
        dpg_as_ncf        = ncfile.createVariable( 'dpg_as', np.dtype('float32').char, ('case') )
        dpg_as_ncf[:]     = dpg_as
        dpg_as_ncf.unit = "\u03BCm"
    else:
        num_pbl_ncf      = ncfile.createVariable( 'num_pbl',   np.dtype('float32').char, ('case') )
        num_pbl_ncf[:]   = num_pbl
        num_pbl_ncf.unit = "#/mg"
    
    ncfile.close()
#####################################################################################    

def check_constrain( variable, lowerbound, upperbound, variablename, lowerboundNAME, upperboundNAME, unit, dimensions = 90 ):
    if check_constrain.counter >= 1:
        check_constrain.checkoutALA = np.column_stack(( check_constrain.checkoutALA, np.zeros(( dimensions, 1)) ))
        check_constrain.checkoutYLA = np.column_stack(( check_constrain.checkoutYLA, np.zeros(( dimensions, 1)) ))
    else:
        check_constrain.checkoutALA = np.column_stack(( np.arange(1,dimensions+1),   np.zeros(( dimensions, 1)) ))
        check_constrain.checkoutYLA = np.column_stack(( np.arange(1,dimensions+1),   np.zeros(( dimensions, 1)) ))
    check_constrain.counter += 1
    wi = int( np.log(max( np.max(variable), np.max(np.abs(lowerbound)), np.max(np.abs(upperbound)) )) ) + 2
    if isinstance( lowerbound, float ):
        lowerbound = lowerbound * np.ones(dimensions)
    if isinstance( upperbound, float ):
        upperbound = upperbound * np.ones(dimensions)

    print("""
#################################
###                           
### CONSTRAINT """ + str(check_constrain.counter) + ')')
    print('###', lowerboundNAME, '<', variablename, '<', upperboundNAME, unit)
    print("""###
#################################
""")

        
    for i in range(dimensions):        
        if ( variable[i] < lowerbound[i] ):
            print('VIOLATION', i+1, 'constraint', check_constrain.counter)
            print(str(variablename) +  ' too small value:' + str(round( variable[i], 1)).rjust(wi) + ' lower bound:' + str(round( lowerbound[i], 1)).rjust(wi) + ' unit ', unit)
            check_constrain.checkoutALA[i, check_constrain.counter] += 1
        if ( variable[i] > upperbound[i]   ):
            print('VIOLATION', i+1, 'constraint', check_constrain.counter)
            print(str(variablename) +  '  too big value:' + str(round( variable[i], 1)).rjust(wi) + ' upper bound:' + str(round( upperbound[i], 1)).rjust(wi) + ' unit ', unit)
            check_constrain.checkoutYLA[i, check_constrain.counter] += 1
        if ( check_constrain.checkoutALA[ i, check_constrain.counter ] > 0 or check_constrain.checkoutYLA[ i, check_constrain.counter ] > 0 ):
            print(' ')        
    if ( sum(check_constrain.checkoutALA[ :, check_constrain.counter ]) == 0. and sum(check_constrain.checkoutYLA[ :, check_constrain.counter ]) == 0. ):
        print('Constraint', check_constrain.counter, 'is OK')
print(' ')
check_constrain.counter = 0
alvl=2500.
cp=1005.
check_constrain( q_inv,     0.,                     q_pbl,                      'q_inv',      '0.',                     'q_pbl',     'g/kg', nroCases )
check_constrain( tpot_inv,  0.,                  tpot_pbl,                      't_inv',      '0.',                  'tpot_pbl',        'K', nroCases )
check_constrain( pblh,      0.,                     3000.,                       'pblh',      '0.',                      '3000',        'm', nroCases )

# forming CSV
for i in range(nroCases):
    temp = str(caselist[i], "utf-8").rjust(next(tabs)) 
    for k in range(np.size(design,1)):
        temp = temp + str( round( float( design[i, k] ),2 ) ).rjust( next(tabs) )
    temp = temp + str( round(cloudbase[i],2)).rjust(next(tabs)) + str( round(pblh[i] - cloudbase[i], 2)).rjust(next(tabs))
    temp = temp + str(round(q_pbl[i],2)).rjust(next(tabs))
    temp = temp + str(round(clw_max[i],2)).rjust(next(tabs))
    
    printtaus.append( temp )
###############
   
argminimums = np.zeros(Ltabs-1)
argmaximums = np.zeros(Ltabs-1)

for k in range(np.size(design,1)):
    argminimums[k] = np.argmin( design[:,k])
argminimums[k+1] = np.argmin(cloudbase)
argminimums[k+2] = np.argmin(pblh-cloudbase)
argminimums[k+3] = np.argmin(q_pbl)
argminimums[k+4] = np.argmin(clw_max)

for k in range(np.size(design,1)):
    argmaximums[k] = np.argmax( design[:,k])
argmaximums[k+1] = np.argmax(cloudbase)
argmaximums[k+2] = np.argmax(pblh-cloudbase)
argmaximums[k+3] = np.argmax(q_pbl)
argmaximums[k+4] = np.argmax(clw_max)

    

#printing
 
kokonaispituus = sum(listtabs)
sys.stdout.write(printtaus[0])
sys.stdout.write('\n')
print('-'*Stabs)
sys.stdout.write(unittulostus)
sys.stdout.write('\n')
print('-'*Stabs)
for printindeksi in range( 1, np.size(printtaus) ): #
    i = printindeksi - 1
    argu = np.column_stack(( argminimums, argmaximums))
    if i in argu: #i in argminimums:            
        summat = [0]
        MINI = np.where( argminimums == i)[0]
        MAXI = np.where( argmaximums == i)[0]
        molemmat = np.sort( np.concatenate((MINI,MAXI )) )
        for k in np.where( argu == i)[0]:
            
            summat.append( sum(listtabs[:min(k+1,len(listtabs))]) )
            summat.append( sum(listtabs[:min(k+2,len(listtabs))]) )
        summat.append( sum(listtabs) )
        
        itersu=iter(summat)
        alku = next(itersu)
        loppu = next(itersu)
        sys.stdout.write( printtaus[printindeksi][alku : loppu ] )
        for k in range(len(molemmat)): #(len(summat)-2)/2
            alku = loppu
            loppu = next(itersu)
            if molemmat[int(k)] in MINI and molemmat[int(k)] not in MAXI:
                sys.stdout.write( colored( printtaus[printindeksi][ alku : loppu ], "blue" ) ) if COLOR else sys.stdout.write( printtaus[printindeksi][ alku : loppu ] )
            elif molemmat[int(k)] in MAXI and molemmat[int(k)] not in MINI:
                sys.stdout.write( colored( printtaus[printindeksi][ alku : loppu ], "red" ) ) if COLOR else sys.stdout.write( printtaus[printindeksi][ alku : loppu ] )
            elif molemmat[int(k)] in MAXI and molemmat[int(k)] in MINI:
                sys.stdout.write( colored( printtaus[printindeksi][ alku : loppu ], "green" ) ) if COLOR else sys.stdout.write( printtaus[printindeksi][ alku : loppu ] )
            else:
                sys.stdout.write( printtaus[printindeksi][alku : loppu ] )                
                
            alku = loppu
            loppu = next(itersu)
            sys.stdout.write(printtaus[printindeksi][alku : loppu ])
        sys.stdout.write('\n')

    else:
        sys.stdout.write( printtaus[printindeksi] )
        sys.stdout.write('\n')

    
print('-'*Stabs)
print(printtaus[0])
print('-'*Stabs)
# MINIMUM
temp = "min".rjust( next(tabs))
for k in range(np.size(design,1)):
    temp = temp + str( round(np.min( design[:,k] ),2) ).rjust( next(tabs))
temp = temp + str( round( np.min(cloudbase),2 )).rjust(next(tabs))+ str( round( np.min( pblh - cloudbase ),2 )).rjust(next(tabs))
temp = temp + str(round( np.min(  q_pbl),2 )).rjust(next(tabs))
temp = temp + str(round( np.min(  clw_max),2 )).rjust(next(tabs))
print(temp)    

# MAXIMUM
temp = "max".rjust( next(tabs))
for k in range(np.size(design,1)):
    temp = temp + str( round(np.max( design[:,k] ),2) ).rjust( next(tabs))
temp = temp + str( round( np.max(cloudbase),2 )).rjust(next(tabs))+ str( round( np.max( pblh - cloudbase ),2 )).rjust(next(tabs))
temp = temp + str(round( np.max(  q_pbl),2 )).rjust(next(tabs))
temp = temp + str(round( np.max(  clw_max),2 )).rjust(next(tabs))
print(temp)

# MEAN
temp = "mean".rjust( next(tabs))
for k in range(np.size(design,1)):
    temp = temp + str( round(np.average( design[:,k] ),2) ).rjust( next(tabs))
temp = temp + str( round( np.average(cloudbase),2 )).rjust(next(tabs))+ str( round( np.average( pblh - cloudbase ),2 )).rjust(next(tabs))
temp = temp + str(round( np.average(  q_pbl),2 )).rjust(next(tabs))
temp = temp + str(round( np.average(  clw_max),2 )).rjust(next(tabs))
print(temp)     

# ARGUMENT MINIMUM
temp = "argmin".rjust( next(tabs))
for k in range(np.size(design,1)):
    temp = temp + str( np.argmin( design[:,k] ) +1 ).rjust( next(tabs))
temp = temp + str( np.argmin(cloudbase) +1 ).rjust(next(tabs)) + str( np.argmin( pblh - cloudbase ) +1 ).rjust(next(tabs))
temp = temp + str( np.argmin( q_pbl ) +1 ).rjust(next(tabs))
temp = temp + str( np.argmin( clw_max ) +1 ).rjust(next(tabs))
print(temp)    

# ARGUMENT MAXIMUM
temp = "argmax".rjust( next(tabs))
for k in range(np.size(design,1)):
    temp = temp + str( np.argmax( design[:,k] ) +1 ).rjust(next(tabs))
temp = temp + str( np.argmax( cloudbase ) +1 ).rjust(next(tabs)) + str( np.argmax( pblh - cloudbase ) +1 ).rjust(next(tabs))
temp = temp + str( np.argmax(  q_pbl) +1 ).rjust(next(tabs))
temp = temp + str( np.argmax(  clw_max) +1 ).rjust(next(tabs))
print(temp) 

print('-'*Stabs)
print(printtaus[0])
print('-'*Stabs)
print(unittulostus)
print('-'*Stabs)

#print ' '
#print 'abs'
#for i in xrange(nroCases):
#    if ( pblh[i] - cloudbase[i]  < 50.  ):
#        print str(i+1).rjust(2), str(round(cloudbase[i], 2)).rjust(9), str(round(pblh[i], 2)).rjust(9), str(round(pblh[i]- cloudbase[i], 2)).rjust(9)

        
print(' ')
print('lower boundary violations')
for i in range(nroCases):
    a = str(int(check_constrain.checkoutALA[i,0])).rjust(2) + ' |'
    if ( sum( check_constrain.checkoutALA[i, 1:] ) > 0.0 ):
        for k in check_constrain.checkoutALA[i,1:]: 
            if int(k) == 0:
                p = '.'
            else:
                p = 'X'
            a = a + ' ' + p
        print(a)
            
print(' ')
print('upper boundary violations')
for i in range(nroCases):
    a = str(int(check_constrain.checkoutYLA[i,0])).rjust(2) + ' |'
    if ( sum( check_constrain.checkoutYLA[i, 1:] ) > 0.0 ):
        for k in check_constrain.checkoutYLA[i,1:]: 
            if int(k) == 0:
                p = '.'
            else:
                p = 'X'
            a = a + ' ' + p
        print(a)
        
ala = sum( check_constrain.checkoutALA[ :, 1: ] )
yla = sum( check_constrain.checkoutYLA[ :, 1: ] )
print(' ')

lbv = 'lower boundaries violations'
vv  = len(lbv)
for i in ala:
    lbv = lbv + ' ' + str(int(i)).rjust(2)
print(lbv)
    
ubv = 'upper boundaries violations'
for i in yla:
    ubv = ubv + ' ' + str(int(i)).rjust(2)
print(ubv)

ww = 3*check_constrain.counter
vv = vv + ww
uu = '-'*vv
print(uu)
print('total number of violations ' + str(int(sum( ala + yla ))).rjust(ww))
print(' ')


print('version', tag)
