#!/usr/bin/python
# -*- coding: utf-8 -*-
# #                         Mounted nzp    file    windprofile  pres0   par/serial   runNroBegin  runNroEnd thermolevel postfix lista
# python emulator_inputs.py True    200   $DESIGN  ideal        1017.8 serial        59           62        4           noNudge [12,26,28,40,52,54,69,76,85]
"""
Created on Wed Dec 21 14:20:00 2016

@author: aholaj
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 13:40:45 2016

@author: aholaj
"""

import numpy as np



from subprocess import call
#import shlex


from FindCloudBase import calc_rh_profile
#from FindCloudBase import calc_cloud_droplet_diam
from FindCloudBase import rslf
from ECLAIR_calcs import solve_rw_lwp
from ECLAIR_calcs import calc_lwp
from ECLAIR_calcs import solve_q_inv_RH
from math import acos
from math import pi
#from ECLAIR_calcs import solve_rw

import sys
import os
import subprocess
import glob
import generate_namelist

global mounted # if run on local computer
global rootfolder
global designfilu
global tag
global DAY
global explicitAerosol
global nroVariables

DAY = True
explicitAerosol = True

designfilu = ''

def bool_convert(s):
    if s=="True":
        r = True
    elif s=="False":
        r = False
    else:
        r = True
    return r

mounted = True


if __name__ == "__main__":

    if ( len(sys.argv) > 2):
        try:
            postfix = sys.argv[10]
            postfix = "_" + postfix
        except IndexError:
            postfix = ""
        try:
            lis = sys.argv[11]
        except IndexError:
            lis = "None"
        
        if sys.argv[9] == "3":
            explicitAerosol = False
        with open(sys.argv[3]) as ff:
            first_line = ff.readline()
            
            if "cos_mu" in first_line:
                DAY = True
            else:
                DAY = False
            
            nroVariables = len(first_line.split(","))-1
                    
        print("Daytime:".ljust(14)             + str(DAY) + "\n" +\
              "Aerosol:".ljust(14) + str(explicitAerosol) + "\n" +\
              "Mounted:".ljust(14)          + sys.argv[1] + "\n" +\
                  "nzp:".ljust(14)          + sys.argv[2] + "\n" +\
                 "filu:".ljust(14)          + sys.argv[3] + "\n" +\
          "windprofile:".ljust(14)          + sys.argv[4] + "\n" +\
                "pres0:".ljust(14)          + sys.argv[5] + "\n" +\
              "runmode:".ljust(14)          + sys.argv[6] + "\n" +\
          "runNroBegin:".ljust(14)          + sys.argv[7] + "\n" +\
            "runNroEnd:".ljust(14)          + sys.argv[8] + "\n" +\
                "level:".ljust(14)          + sys.argv[9] + "\n" +\
              "postfix:".ljust(14)          +     postfix + "\n" +\
                "lista:".ljust(14)          +         lis )
                
        mounted = bool_convert( sys.argv[1] )

    home= os.environ["HOME"]
    ibrix = os.environ["IBRIXMOUNT"]
    les = os.environ["LES"]
    
    script = os.environ["SCRIPT"]
    
    lesroot    = les + '/'
    designroot = ibrix + '/DESIGN/'
    
    cwd = os.getcwd()
    
    
    os.chdir(designroot)
    try:
        tag = subprocess.check_output("git describe --tags | tr -dc '[:alnum:].'", stderr=subprocess.STDOUT , shell=True)
        tag = tag.decode("utf-8")
    except subprocess.CalledProcessError:
        tag = "vx.x.x"
    if ( "Not a git repository" in tag or "not found" in tag):
        tag = "vx.x.x"
        
    rootfolder = lesroot + 'bin/case_emulator_DESIGN_' + tag + postfix + '/'
    for file in glob.glob("*.csv"):
        designbasename=file
    
    os.chdir(cwd)
    
    designfilu = designroot + designbasename

if mounted:
    import matplotlib.pyplot as plt
    from ModDataPros import plottaa
    from plot_profiles import PlotProfiles
    from ModDataPros import initializeColors

#if (len(sys.argv) > 1):
#    for i in sys.argv[1:]:
#        rootfolder = sys.argv[1]
#        filu = sys.argv[2]


def deltazvanha( pblh, nzp ):
    deltaz = max( 1., min( 20. , round( 1.3333 * pblh / float(nzp) ) ) )
   
   
    return deltaz, nzp

def deltaz( pblh, nzp_orig ):
    
    if (pblh > 3000.) :
        
        dz = 20.
        nzp = round(1.3333 * pblh / dz, 0)
        deltaz = dz
    
    else:
        dz = max( 1., min( 20. , round( max( 1.3333 * pblh, pblh + 500.) / float(nzp_orig) ) ) )
    
        if ( dz < 10.0 ):
            deltaz = 10.0
            nzp = int(( nzp_orig-1.5 )*dz/deltaz )
        else:
            deltaz = dz
            nzp = nzp_orig

    return deltaz, nzp
    
def define_z( pblh, deltaz, nzp ):
#z = [ 100., 200., 500.,790.,795.,800.,850.,900.,950.,1000.,1050.,1100.,1150.,1200.,1250.,1300.,1350.,1400.,1450.,1500.,1550.,1600.,1650.,1700.,1750.,1800.,1850.,1900.,1950.,2000.]
    
    zt = []    
    
    zt.append(-deltaz/2.)
    
    for i in range(nzp-1):
        zt.append(zt[i]+deltaz)
    
    if (pblh > zt[-1]):
        sys.exit("MODEL HEIGHT NOT ABOVE PBLH: " + str(pblh) + " model height: " + str(zt[-1]))
    
    return zt

def tot_wat_mix_rat_LIN(  z, pblh, q_pbl, q_inv, invThi = 50. ):
    if ( z < pblh ):
        q = q_pbl # g/kg
    elif (z > pblh + invThi ):
        q = q_pbl - q_inv - ( z - ( pblh + invThi ))*tot_wat_mix_rat_LIN( pblh + invThi, pblh, q_pbl, q_inv, invThi )/2000.
    else:
        q = q_pbl - q_inv/invThi * ( z - pblh )
       
    return q

def pot_temp_LIN( z, pblh, tpot_pbl, tpot_inv, t_grad, invThi = 50., dtdzFT = 0.003  ):
    if (z < pblh ):
        theta = tpot_pbl
    elif( z > pblh + invThi):
        theta = tpot_pbl + tpot_inv + dtdzFT*( z - ( pblh + invThi ))
    else:
        theta = tpot_pbl + t_grad * ( z - pblh )
    
    return theta


def tot_wat_mix_rat_IT( z, pblh, q_pbl, q_inv, invThi = 50., q_toa = 2.  ):
    if ( z < pblh ):
        q = q_pbl # g/kg
    elif (z > pblh + invThi ):
        q = (q_pbl - q_inv) - ( q_pbl - q_inv - q_toa) * (1. - np.exp( -( z-pblh-invThi ) / 500. ) ) # g/kg
    else:
        q = -q_inv/invThi * ( z - pblh ) + q_pbl
        
       
    return q

def pot_temp_IT( z, pblh, tpot_pbl, tpot_inv, invThi = 50. ):
    if   (z < pblh ):
        theta = tpot_pbl
    elif (z > pblh + invThi ):
        theta = tpot_pbl + tpot_inv +np.power( z-pblh-invThi , 1./3. )
    else:
        theta = tpot_inv/invThi * ( z - pblh )  + tpot_pbl
    
    return theta

def dthcon(tpot_pbl, sst, pres0 ):
    # CONSTANTS    
    R = 287.04    # Specific gas constant for dry air (R_specific=R/M), J/kg/K
    Rm = 461.5    # -||- for water
    ep = R/Rm
    ep2 = Rm/R-1.0 #M_air/M_water-1
    cp = 1005.0    # Specific heat for a constant pressure
    rcp = R/cp
    cpr = cp/R
    g = 9.8
    p00 =1.0e+05
    p00i = 1./p00
    alvl   = 2.5e+06
    ############
    dthcon = tpot_pbl - sst*(p00/pres0)**rcp
    
    return dthcon
    
def drtcon( q_pbl, sst, pres0 ):
    drtcon = q_pbl - rslf(pres0,sst)

    return drtcon    

def absT( theta, p, conversion = 100. ):
    p = p*conversion # conversion from hPa to Pa by default
    R = 287.04    # Specific gas constant for dry air (R_specific=R/M), J/kg/K
    p00 =1.0e+05
    p00i = 1./p00
    cp = 1005.0    # Specific heat for a constant pressure
    rcp = R/cp

    absolut = theta*(p*p00i)**rcp
    
    return absolut

def potT( t, p, conversion = 100.):
    p = p*conversion # conversion from hPa to Pa by default
    R = 287.04    # Specific gas constant for dry air (R_specific=R/M), J/kg/K
    p00 =1.0e+05
#    p00i = 1./p00
    cp = 1005.0    # Specific heat for a constant pressure
    rcp = R/cp

    theta = t*(p00/p)**rcp
    
    return theta

def wind_0(z):
    u = 0.
    v = 0.
    return u,v

def wind_ideal(z):
    u = 10.
    v = 0.
    return u,v    
    
def wind_dycoms(z):
    u = 3. + 4.2*z/1000.
    v = -9. + 5.6*z/1000.
    return u,v


def wind_ascos(z):
    ascos = PlotProfiles('sound_in', "bin/case_ascos/")
    u = ascos.returnUAppr( z )
    v = ascos.returnVAppr( z )

    return u,v

def calcWind(u,v):
    x = np.asarray(u)
    y = np.asarray(v)    
    t = np.column_stack(( x, y))
    wind = np.zeros(len(u))
    for k in range(len(u)):
        wind[k] = np.linalg.norm(t[k])
    
    return wind
    
def calcWindShear(u,v,z):
    size = len(z)-1
    shear = np.zeros(size)
    for k in range(size):
        shear[k] = np.sqrt( np.power( u[k+1] - u[k], 2 ) + np.power( v[k+1] - v[k], 2 ) ) / ( z[k+1] - z[k] )
    
    return shear
        

# t_grad [ K / m]
def thickness( tpot_inv, t_grad = 0.3   ):

    invThi = tpot_inv / t_grad
    return invThi


def read_design( filu, nroVariables = 5, DAY = False, explicitAerosol = False ):
    
    riviLKM = subprocess.check_output( "cat " + filu + " | wc -l ", shell=True)
    nroCases = int( riviLKM )-1
    etunolla = 3 #int(len(str(nroCases)))
    
    f = open( filu, 'r' )
    
    design     = np.zeros( (   nroCases, nroVariables ) )
    caselist   = np.chararray( nroCases, itemsize = etunolla)
    
    i=0
    for line in f:
        #print line
        if (not DAY) and (not explicitAerosol) :
            A0, A1, A2, A3, A4, A5, A6                        = line.split(',')
        elif DAY and (not explicitAerosol):
            A0, A1, A2, A3, A4, A5, A6, ACOS                  = line.split(',')
        elif (not DAY) and explicitAerosol:
            A0, A1, A2, A3, A4, A5, A6, A7, A8, A9            = line.split(',')
        elif DAY and explicitAerosol:
            A0, A1, A2, A3, A4, A5, A6, A7, A8, A9, ACOS      = line.split(',')
            
        if ( i > 0 ):
            index = i-1 
            caselist[index]    = A0.replace('"',"").zfill(etunolla) # case
            design[ index, 0 ] = float( A1 ) # q_inv
            design[ index, 1 ] = float( A2 ) # tpot_inv
            design[ index, 2 ] = float( A3 ) # lwp
            design[ index, 3 ] = float( A4 ) # tpot_pbl
            design[ index, 4 ] = float( A5 ) # pblh
            if explicitAerosol:
                design[ index, 5 ] = float( A6  ) # ks
                design[ index, 6 ] = float( A7  ) # as
                design[ index, 7 ] = float( A8  ) # cs
                design[ index, 8 ] = float( A9  ) # rdry_AS_eff
        
            else:
                design[ index, 5 ] = float( A6  ) # num_pbl
            if DAY:
                design[ index, -1 ] = float( ACOS ) # cos_mu
            
        i=i+1   
    
        
        
    f.close()
    
    #      case,        q_inv,       tpot_inv,    lwp,     tpot_pbl,    pblh,        num_pbl
    if (not DAY) and (not explicitAerosol):
        return caselist,    design[:,0], design[:,1], design[:,2], design[:,3], design[:,4], design[:,5]
    elif DAY and (not explicitAerosol):
        return caselist,    design[:,0], design[:,1], design[:,2], design[:,3], design[:,4], design[:,5], design[:,-1]
    elif (not DAY) and explicitAerosol:
        return caselist,    design[:,0], design[:,1], design[:,2], design[:,3], design[:,4], design[:,5], design[:,6], design[:,7], design[:,8]
    elif DAY and explicitAerosol:
        return caselist,    design[:,0], design[:,1], design[:,2], design[:,3], design[:,4], design[:,5], design[:,6], design[:,7], design[:,8], design[:,-1]
    


def write_sound_in( input_vector ):
#    input_vector = pres0[0], windprofile[1], case[2], q_inv[3], tpot_inv[4], q_pbl[5], tpot_pbl[6], pblh[7], dz[8], nzp[9] 
    pres0       = float( input_vector[0] )
    windprofile =        input_vector[1]
    case        = str(   input_vector[2] )
    q_inv       = float( input_vector[3] )
    tpot_inv    = float( input_vector[4] )
    q_pbl       = float( input_vector[5] )
    tpot_pbl    = float( input_vector[6] )
    pblh        = float( input_vector[7] )
    dz          = float( input_vector[8] )
    nzp         = int(   input_vector[9] )
    
    
    
    folder = rootfolder+'emul' + case +'/'
    call(['mkdir','-p', folder])
    filename = 'sound_in' #+case
#    print filename
    filu = folder + filename
    
    
    f = open(filu,'w')
    
    #z = [ 100., 200., 500.,790.,795.,800.,850.,900.,950.,1000.,1050.,1100.,1150.,1200.,1250.,1300.,1350.,1400.,1450.,1500.,1550.,1600.,1650.,1700.,1750.,1800.,1850.,1900.,1950.,2000.]
    
#    print row

    
    z = define_z( pblh, dz, nzp )
    
    print('case '    + str(case))
    print('deltaz '  + str(dz))
    print('korkeus ' + str(z[-1]))
    print('pblh '    + str(round(pblh,2)))
    print('nzp '     + str(nzp))

    print('tpot_pbl ' + str(round(tpot_pbl,2)))
    print('tpot_inv ' + str(round(tpot_inv,2)))
    print('q_pbl '    + str(round(q_pbl,2)))
    print('q_inv '    + str(round(q_inv,2)))
    #print('num_pbl '  + str(round(num_pbl,2)))
    z[0] = pres0
    potTemp = [tpot_pbl]
    wc = [q_pbl]
    u = [0.]
    v = [0.]

#    invThi = 50.
    t_grad = 0.3   
    invThi = thickness( tpot_inv, t_grad )
    print('inversion thickness ' + str(round(invThi,2)))
    print(" ")

    for k in range(1,len(z)):
        
        

#        potTemp.append( pot_temp_IT( z[k], pblh, tpot_pbl, tpot_inv, invThi ) )
#        wc.append(      tot_wat_mix_rat_IT( z[k], pblh, q_pbl, q_inv, invThi, q_toa = min( max( q_pbl-q_inv-0.01, 0.01) , 2. ) ) )

        potTemp.append( pot_temp_LIN(        z[k], pblh, tpot_pbl, tpot_inv, t_grad, invThi, dtdzFT = 0.003 ) ) 
        wc.append(      tot_wat_mix_rat_LIN( z[k], pblh,    q_pbl,    q_inv,  invThi  ) )

        if ( windprofile == 'zero' ):
                u_apu, v_apu = wind_0( z[k] )
        elif ( windprofile == 'ascos' ):
                u_apu, v_apu = wind_ascos( z[k] )
        elif ( windprofile == 'dycoms' ):
                u_apu, v_apu = wind_dycoms( z[k] )
        elif ( windprofile == 'ideal' ):
                u_apu, v_apu = wind_ideal( z[k] )                  
        u.append( u_apu )
        v.append( v_apu )
    if ( windprofile == 'zero' ):
        u_apu, v_apu = wind_0( 0. )
    elif ( windprofile == 'ascos' ):
        u_apu, v_apu = wind_ascos(  0. )
    elif ( windprofile == 'dycoms' ):
        u_apu, v_apu = wind_dycoms(  0. )
    elif ( windprofile == 'ideal' ):
        u_apu, v_apu = wind_ideal(  0. )
    u[0] = u_apu
    v[0] = v_apu        
#    for k in xrange(len(z)):
#        print z[k], potTemp[k]
        
    #    print 'lev '+ str(lev)+' theta '+ str(potTemp(lev))+ ' wc ' + str(wc(lev)) + ' u ' + str(u(lev)) + ' v ' + str(v(lev))

    rh, pressL = calc_rh_profile(  potTemp, np.multiply(np.asarray(wc), 0.001),  z )
    #drop, cloudwater = calc_cloud_droplet_diam( potTemp, np.multiply(np.asarray(wc), 0.001),  pressL, num_pbl*1e6) drawing
    #cloudwater = np.multiply(cloudwater,1000.)
    wind = calcWind(u,v)
    windshear = calcWindShear(u,v,z)
#    if you want to modify water content use the two following commands
#    rh, wc2 = calc_rh_profile(  potTemp, np.multiply(np.asarray(wc), 0.001),  z, True )
#    wc = np.multiply(wc,1000.)[7]

    # write to sound_in    

    for k in range(len(z)):
        
        row= ' {0:15f} {1:15.6f} {2:15.6f} {3:15.6f} {4:15.6f}\n'.format(            \
                                        z[k],                           \
                                        potTemp[k],                  \
                                        wc[k],                          \
                                        u[k],                           \
                                        v[k]                            )
        f.write(row)                                        
    
    f.close()
    
#     plotting if mounted
    if ( mounted ):
        print("Plotataan case " +str(case) )
        print(" ")
        LEGEND =  False
        markers=True
        z[0] = 0.
        initializeColors(7)

        plottaa( potTemp, z, tit = case+' liq. pot. temp., pblh: ' + str( round(pblh,2) ) + ' [m] invThi.: ' +str( round(invThi,2) ) + ' [m]', xl = 'liquid potential temperature [K]', yl = 'height [m]', markers=markers, uusikuva = True, LEGEND = LEGEND )
        plt.axhline( y = pblh )
#        plt.axhline( y = pblh + invThi )
#        plt.plot([tpot_pbl,tpot_pbl+tpot_inv], [pblh,pblh+invThi], color='r', marker='o')
#        plt.ylim( [pblh-1.*dz, pblh + invThi+1*dz])
#    #    ax.set_yticks(z)
#    #    ax.set_yticks([pblh, pblh+invThi], minor=True)
        plt.savefig( folder + case + '_0_'+ 'liquid_potential_temperature'  + '.png', bbox_inches='tight')    
        plt.close()
        
        plottaa( wc, z, tit = case+' '+ r'$H_{2}$' + ' mix. rat., pblh: ' + str( round(pblh,2) ) + ' [m] invThi.: ' +str( round(invThi,2) ) + ' [m]', xl =  'water mixing ratio [g/kg]', yl = 'height [m]', markers=markers, uusikuva = True, LEGEND = LEGEND )
        plt.axhline( y = pblh )
#        plt.axhline( y = pblh + invThi )
#        plt.plot([q_pbl,q_pbl-q_inv], [pblh,pblh+invThi], color='r', marker='o')
#        plt.ylim( [pblh-1.*dz, pblh + invThi+1*dz])
        plt.savefig( folder + case + '_0_'+ 'water_mixing_ratio'  + '.png', bbox_inches='tight')    
        plt.close()

        plottaa( rh, z, tit = case+' relative humidity', xl = 'relative humidity [%]', yl = 'height [m]', markers=markers, uusikuva = True, LEGEND = LEGEND )
        plt.savefig( folder + case + '_'+ 'relative_humidity'  + '.png', bbox_inches='tight')    
        plt.close()
        

#        plottaa( drop, z, tit = case+' cloud droplet diameter', xl = r'diameter [$\mu$]', yl = 'height [m]', markers=markers, uusikuva = True, LEGEND = LEGEND )
#        plt.savefig( folder + case + '_'+ 'cloud_droplet_diameter'  + '.png', bbox_inches='tight')   
#        plt.close()

#        plottaa( cloudwater, z, tit = case+' cloud water mixing ratio', xl = 'cloud water mixing ratio [g/kg]', yl = 'height [m]', markers=markers, uusikuva = True, LEGEND = LEGEND )
#        plt.savefig( folder + case + '_'+ 'cloud_water_mixing_ratio'  + '.png', bbox_inches='tight')         
#        plt.close()

        plottaa( wind, z, tit = case+' wind '+ windprofile, xl = 'wind [m/s]', yl = 'height [m]', markers=markers, uusikuva = True, LEGEND = LEGEND )
        plt.savefig( folder + case + '_'+ 'wind'  + '.png', bbox_inches='tight')
        plt.close()

        plottaa( windshear, z[:-1], tit = case+' wind shear '+ windprofile, xl = 'wind shear '+ r'[$s^{-1}$]', yl = 'height [m]', markers=markers, uusikuva = True, LEGEND = LEGEND )
        plt.savefig( folder + case + '_'+ 'windshear'  + '.png', bbox_inches='tight')
        plt.close()

    else:
        print('Not plotting initial conditions')
    
    return True
    
def write_namelist( input_vector ):
    #write_namelist( [pres0, level, case[k], nzp[k], dz[k], q_inv[k], tpot_inv[k], lwp[k], tpot_pbl[k], pblh[k], num_ks[k], num_as[k], num_cs[k], cntlat[k] ] )
    pres0    = float( input_vector[0] )
    level    =        input_vector[1]
    case     = str(   input_vector[2] )
    nzp      = int(   input_vector[3] )
    dz       = float( input_vector[4] )
    q_inv    = float( input_vector[5] )
    tpot_inv = float( input_vector[6] )
    lwp      = float( input_vector[7] )
    tpot_pbl = float( input_vector[8] )    
    pblh     = float( input_vector[9] )
    if not explicitAerosol:
        num_pbl  = float( input_vector[10] )
    elif explicitAerosol:
        num_ks = float( input_vector[10] )
        num_as = float( input_vector[11] )
        num_cs = float( input_vector[12] )
        dpg_as = float( input_vector[13] )
    
    if DAY:
        cntlat   = float(input_vector[-1])
        




    folder = rootfolder +'emul' + case 
    call(['mkdir','-p', folder])
    sst = absT( tpot_pbl, pres0 )

    

#    dth = dthcon( tpot_pbl, sst, pres0 )
#    drt = drtcon( q_pbl, sst, pres0 )
#              ' dthcon=' + str(dth)                              +\
#              ' drtcon=' + str(drt)                              +\


    argv = sys.argv[1:]
    
    filu = folder + "/" + "NAMELIST"
    argv.append('--design='   + tag )
    argv.append('--case='     + case )
    argv.append('--q_inv='    + str(q_inv))
    argv.append('--tpot_inv=' + str(tpot_inv))
    argv.append('--lwp='  + str(lwp))
    argv.append('--tpot_pbl=' + str(tpot_pbl))
    argv.append('--pblh='     + str(pblh))
    argv.append('--level='    + level)
    argv.append('--Tspinup=5400.')
    argv.append('--nzp='      + str(nzp))
    argv.append('--deltaz='   + str(dz))
    
    argv.append('--sst='      + str(sst))
    argv.append('--filprf=' +  '"emul' + case + '"')
    argv.append('--hfilin=' + '"emul' + case + '.rst"')
    
    
    argv.append('--th00='      + str(tpot_pbl))
    argv.append("--nudge_ccn_zmax=" + str(dz))
    
    if not explicitAerosol:
        argv.append('--CCN='      + str(num_pbl*1e6))
        argv.append('--num_pbl='  + str(num_pbl))
        
        
    elif explicitAerosol:
        argv.append('--nconc='+ str(num_ks) + "," + str(num_as) + "," + str(num_cs) + ',0.,0.,0.,0.')
        argv.append('--dpg='+'0.0209,' + str(dpg_as) + ',0.9626,0.2,0.2,0.2,0.2')
        
    if DAY:
        argv.append("--cntlat=" + str(cntlat))
    #argv.append("--timmax=350.")
    
    


    generate_namelist.write_namelist( argv, filu)
    
    print('generated NAMELIST ' + str(case))
    print(' ')
    
    return True
    
def main( nzp_orig=200, filu = designfilu, windprofile = 'ideal', pres0 = 1017.8, runmode='parallel', runNroBegin = 1, runNroEnd = 90, level = '3', lista=None ):
    nzp_orig = int(nzp_orig)
    pres0 = float(pres0)
    
 
    
    if lista is None:
        runNroBegin = int(runNroBegin)
        runNroEnd   = int(runNroEnd)
        A = runNroBegin - 1
        B = runNroEnd   
        lista = list(range(A, B))
    else:
        runNroBegin = np.min(lista)
        runNroEnd   = np.max(lista)
        
#    args=['rm','-rf', rootfolder+'*']
#    call(args)
    args ='rm -rf '+ rootfolder+'*'
    os.system(args)
    cwd = os.getcwd()
    designfolder = os.path.dirname( os.path.realpath( filu ) )
    os.chdir( designfolder )
    os.chdir( cwd )
            
    if (not DAY) and (not explicitAerosol):
        case, q_inv, tpot_inv, lwp, tpot_pbl, pblh, num_pbl                              = read_design( filu, nroVariables = nroVariables, DAY = DAY, explicitAerosol = explicitAerosol )
    elif DAY and (not explicitAerosol):
        case, q_inv, tpot_inv, lwp, tpot_pbl, pblh, num_pbl, cntlat                      = read_design( filu, nroVariables = nroVariables, DAY = DAY, explicitAerosol = explicitAerosol )
    elif (not DAY) and explicitAerosol:
        case, q_inv, tpot_inv, lwp, tpot_pbl, pblh, num_ks, num_as, num_cs, dpg_as         = read_design( filu, nroVariables = nroVariables, DAY = DAY, explicitAerosol = explicitAerosol )
    elif DAY and explicitAerosol:
        case, q_inv, tpot_inv, lwp, tpot_pbl, pblh, num_ks, num_as, num_cs, dpg_as, cntlat = read_design( filu, nroVariables = nroVariables, DAY = DAY, explicitAerosol = explicitAerosol )
    if runNroEnd > len(case):
        runNroEnd = len(case)        
        sys.exit('runNroEnd too big: '+ str( runNroEnd ) + ' max value: ' + str( len(case) ) )
    
    max_RH=98.

    # define resolutions and nzp's    
    dz = np.zeros(len(case))
    nzp = np.zeros(len(case))
    q_pbl = np.zeros(len(case))    
    
    
    q_inv_changes_list = [tag]
    for k in lista:
        temp = ''
        case[k] = str(case[k].decode("utf-8"))
        q_changed = [False, False]
        #q_pbl[k]      = solve_rw( pres0*100., tpot_pbl[k], lwp[k]*0.001, pblh[k] )*1000.
        q_inv_vanha = q_inv[k]
        q_pbl[k]      = solve_rw_lwp( pres0*100., tpot_pbl[k],lwp[k]*0.001, pblh[k]*100. )  # kg/kg
        
        
        
        lwp_apu, cloudbase, pblh_m, clw_max = calc_lwp( pres0*100., tpot_pbl[k] , pblh[k]*100., q_pbl[k] )
        q_pbl[k] = q_pbl[k]*1000. # kg/kg -> g/kg
        
        lwp_suht_ero = np.abs(max(lwp_apu*1000., lwp[k])/min(lwp_apu*1000., lwp[k])-1)*100.
        if lwp_suht_ero > 10.:
            sys.exit("case: " + str(case[k]) + " designin lwp:n ja laskennallisen lwp:n ero on yli 10%: " + lwp_suht_ero + " %")
        
        if q_inv[k] > q_pbl[k]:
            q_inv[k] = min( q_inv[k], q_pbl[k]-1e-4 )
            q_changed[0] = True
            
        
        if (q_pbl[k] < 0. ):
            sys.exit('q_pbl NEGATIVE VALUE')
            
        q_new, rh_new, rh_vanha = solve_q_inv_RH( ( pres0 - pblh[k] )*100., tpot_pbl[k] + tpot_inv[k] , max( 0., q_pbl[k] - q_inv[k] )*1e-3, max_RH)
        q_new = q_new*1e3
        q_inv_new = q_pbl[k] - q_new
        if abs(q_inv_new - q_inv[k] )>1e-7:
            q_inv[k] = q_inv_new
            
        if rh_vanha > max_RH:    
            q_changed = [True, True]
            
        if q_changed[0]:
            temp = temp + "case: {0:03d} q_inv: {1:15.6f} [g/kg] q_inv_old: {2:15.6f} [g/kg]".format(int(case[k].decode("utf-8")), q_inv[k], q_inv_vanha )
        
        if q_changed[1]:
            temp = temp + " Above inversion: RH_new {0:5.2f} [%]  RH_old: {1:5.2f} [%]".format(rh_new, rh_vanha )
        if any(q_changed):
            print(temp)
            q_inv_changes_list.append(temp)
        
        pblh[k]  = pblh_m
        
        if DAY:
            cntlat[k] = acos(cntlat[k])*180./pi
        if explicitAerosol:
            num_ks[k] = num_ks[k]*1e-6
            num_as[k] = num_as[k]*1e-6
            num_cs[k] = num_cs[k]*1e-6
            dpg_as[k] = dpg_as[k]*2e6
        
        dz[k], nzp[k] = deltaz( pblh[k], nzp_orig )
    
    q_inv_log_folder = ibrix + '/DESIGNnetcdf/'+tag +"/"
    call(['mkdir','-p', q_inv_log_folder])
    q_inv_log = q_inv_log_folder + 'design_' + tag + '_q_inv_changes.txt'        
    with open(q_inv_log, 'w') as qlog:
        for rivi in q_inv_changes_list:
            qlog.write(rivi + '\n')
    
    nzp = nzp.astype(int)
    

#    pres0    = float( input_vector[0] )
#    level    =        input_vector[1]
#    case     =        input_vector[2]
#    nzp      = int(   input_vector[3] )
#    dz       = float( input_vector[4] )
#    q_inv    = float( input_vector[5] )
#    tpot_inv = float( input_vector[6] )
#    lwp      = float( input_vector[7] )
#    tpot_pbl = float( input_vector[8] )    
#    pblh     = float( input_vector[9] )
#    num_pbl  = float( input_vector[10] )    

    
    if ( runmode == 'serial' ) :
        print('serial mode')
        for k in lista:
            
            if (not DAY) and (not explicitAerosol):
                write_namelist( [pres0, level, case[k], nzp[k], dz[k], q_inv[k], tpot_inv[k], lwp[k], tpot_pbl[k], pblh[k], num_pbl[k] ] )
            elif DAY and (not explicitAerosol):
                write_namelist( [pres0, level, case[k], nzp[k], dz[k], q_inv[k], tpot_inv[k], lwp[k], tpot_pbl[k], pblh[k], num_pbl[k], cntlat[k] ] )
            elif (not DAY) and explicitAerosol:
                write_namelist( [pres0, level, case[k], nzp[k], dz[k], q_inv[k], tpot_inv[k], lwp[k], tpot_pbl[k], pblh[k], num_ks[k], num_as[k], num_cs[k], dpg_as[k] ] )
            elif DAY and explicitAerosol:
                write_namelist( [pres0, level, case[k], nzp[k], dz[k], q_inv[k], tpot_inv[k], lwp[k], tpot_pbl[k], pblh[k], num_ks[k], num_as[k], num_cs[k], dpg_as[k], cntlat[k] ] )

            write_sound_in([pres0, windprofile, case[k], q_inv[k], tpot_inv[k], q_pbl[k], tpot_pbl[k], pblh[k], dz[k], nzp[k] ] )           
            
    elif ( runmode == 'parallel' ):
        print('parallel mode')
        koko = len(case)
        windprofile = np.asarray( [windprofile]*koko )
        pres0       = np.asarray( [pres0]*koko )
        level       = np.asarray( [level]*koko )
        
        from multiprocessing import Pool
        pool = Pool(processes= 4)
        
        if (not DAY) and (not explicitAerosol):
            namelist_iter = iter( np.column_stack( ( pres0[ lista ], level[ lista ], case[ lista ], nzp[ lista ], dz[ lista ], q_inv[ lista ], tpot_inv[ lista ], lwp[ lista ], tpot_pbl[ lista ], \
                                                 pblh[ lista ], num_pbl[ lista ] ) ) )
        elif DAY and (not explicitAerosol):
            namelist_iter = iter( np.column_stack( ( pres0[ lista ], level[ lista ], case[ lista ], nzp[ lista ], dz[ lista ], q_inv[ lista ], tpot_inv[ lista ], lwp[ lista ], tpot_pbl[ lista ], \
                                                 pblh[ lista ], num_pbl[ lista ], cntlat[ lista ] ) ) )
        elif (not DAY) and explicitAerosol:
            namelist_iter = iter( np.column_stack( ( pres0[ lista ], level[ lista ], case[ lista ], nzp[ lista ], dz[ lista ], q_inv[ lista ], tpot_inv[ lista ], lwp[ lista ], tpot_pbl[ lista ], \
                                                 pblh[ lista ], num_ks[ lista ], num_as[ lista ], num_cs[ lista ], dpg_as[ lista ] ) ))
        elif DAY and explicitAerosol:
            namelist_iter = iter( np.column_stack( ( pres0[ lista ], level[ lista ], case[ lista ], nzp[ lista ], dz[ lista ], q_inv[ lista ], tpot_inv[ lista ], lwp[ lista ], tpot_pbl[ lista ], \
                                                 pblh[ lista ], num_ks[ lista ], num_as[ lista ], num_cs[ lista ], dpg_as[ lista ], cntlat[ lista ] ) ) )
        
        sound_in_iter = iter( np.column_stack( ( pres0[ lista ], windprofile[ lista ], case[ lista ], q_inv[ lista ], tpot_inv[ lista ], q_pbl[ lista ], tpot_pbl[ lista ], pblh[ lista ], \
                                                   dz[ lista ], nzp[ lista ] ) ) )
        
        # run as unordered parallel processes    
        for k in pool.imap_unordered( write_namelist, namelist_iter ):
            pass
        for i in pool.imap_unordered( write_sound_in, sound_in_iter ):
            pass

            

#def dycoms():
#    call(['rm','-rf', rootfolder+'*'])
#    case = 'dycoms'
#    q_inv = 4.45
#    tpot_inv = 6.7
#    q_pbl = 9.45
#    tpot_pbl = 288.3
#    pblh = 795.
#    write_sound_in( case, q_inv, tpot_inv, q_pbl, tpot_pbl, pblh)
#    write_namelist( case, 20., 660. )
#    
if __name__ == "__main__":
    
    if ( len(sys.argv) > 2):
        print(sys.argv[2])
        try:
            lista = list(map(int, sys.argv[11].strip('[]').split(',')))
            lista = np.asarray( [p-1 for p in lista] )
        except IndexError:
            lista = None
        
        try:
            if (int(sys.argv[7]) == 0 or int(sys.argv[8]) == 0) and (lista == None): # if runNroBegin or runNroEnd given as 0, generate the whole design automatically
                runNroBegin = 1
                designtiedosto = sys.argv[3]
                runNroEnd = int(subprocess.check_output( "cat " + designtiedosto + " | wc -l ", shell=True).decode("utf-8"))-1
                
            else:
                runNroBegin = sys.argv[7]
                runNroEnd   =  sys.argv[8]
        except IndexError:
            sys.exit("Problem in initializing the runNroBegin and runNroEnd")
            
        main( nzp_orig = sys.argv[2], filu =  sys.argv[3], windprofile = sys.argv[4], pres0 = sys.argv[5], runmode = sys.argv[6], runNroBegin = runNroBegin, runNroEnd =  runNroEnd, level = sys.argv[9], lista = lista )
        print('generated by using Command Line arguments')
    else:
        main()
        print('generated by using default values')


#main(200, filu, 'ascos')
#dycoms()
#plot_lopetus()
