def calc_psat_w(T):
    # Function calculates the saturation vapor pressure (Pa) of liquid water as a function of temperature (K)
    #
    # thrm.f90:  real function rslf(p,t)
    c0=0.6105851e+03
    c1=0.4440316e+02
    c2=0.1430341e+01
    c3=0.2641412e-01
    c4=0.2995057e-03
    c5=0.2031998e-05
    c6=0.6936113e-08
    c7=0.2564861e-11
    c8=-.3704404e-13
    #
    x=max(-80.,T-273.16)
    return c0+x*(c1+x*(c2+x*(c3+x*(c4+x*(c5+x*(c6+x*(c7+x*c8)))))))
 
def rsif(p,t):
    
    c0=0.6114327e+03
    c1=0.5027041e+02
    c2=0.1875982e+01
    c3=0.4158303e-01
    c4=0.5992408e-03
    c5=0.5743775e-05
    c6=0.3566847e-07
    c7=0.1306802e-09
    c8=0.2152144e-12
    
    x=max(-80.,t-273.16)
    esi=c0+x*(c1+x*(c2+x*(c3+x*(c4+x*(c5+x*(c6+x*(c7+x*c8)))))))
     
    return .622*esi/(p-esi)

  


def calc_sat_mixr(p,T):
    # Function calculates saturation mixing ratio for water (kg/kg)
    #
    # thrm.f90: real function rslf(p,t)
    #
    # r=m_w//m_air
    # R/Rm=287.04/461.5=.622
    #
    esl=calc_psat_w(T)
    return .622*esl/(p-esl)


def calc_rh(rw,T,press):
    # Calculate RH (%) from water vapor mixing ratio rw (r=m_w/m_air [kg/kg]), temperature (K) and pressure (Pa)
    #
    # r=m_w//m_air=pw/Rm/(pair/R)=pw/(p-pw)*R/Rm => pw=p*r/(R/Rm+r)
    #
    R=287.04    # Specific gas constant for dry air (R_specific=R/M), J/kg/K
    Rm=461.5    # Specific gas constant for water
    ep=R/Rm
    #
    psat=calc_psat_w(T)
    return press*rw/(ep+rw)/psat*100
    # When ep>>rw => RH=press*rw/(ep*psat)*100

def calc_rw( rh, T, press ):
    # for given rh(%), Temp [k] (liq. pot. temp), press
    # return rw = water vapor mixing ratio [kg/kg]
    R=287.04    # Specific gas constant for dry air (R_specific=R/M), J/kg/K
    Rm=461.5    # Specific gas constant for water
    ep=R/Rm
    
    psat=calc_psat_w(T)
    
    return rh*ep*psat/(press*100.-rh*psat)

def calc_cloud_base(p_surf,theta,rw):
    # Calulate cloud base heigh when liquid water potential temperature (theta [kK) and water
    # vapor mixing ratio (rw [kg/kg]) are constants. Surface pressure p_surf is given in Pa.
    # For more information, see "lifted condensation level" (LCL).
    #
    # Constants
    R=287.04    # Specific gas constant for dry air (R_specific=R/M), J/kg/K
    Rm=461.5    # -||- for water
    ep2=Rm/R-1.0 #M_air/M_water-1
    cp=1005.0    # Specific heat for a constant pressure
    rcp=R/cp
    cpr=cp/R
    g=9.8
    p00=1.0e+05
    #
    # Integrate to cloud base altitude
    dz=1.            # 1 m resolution
    z=0.                # The first altitude
    press=p_surf    # Start from surface
    RH=0
    while RH<100 and z<10000:
        # Temperature (K)
        tavg=theta*(press/p00)**rcp
        #
        # Current RH (%)
        RH=calc_rh(rw,tavg,press)
        if RH>100: break
        #
        # From z to z+dz
        z+=dz
        # Virtual temperature: T_virtual=T*(1+ep2*rl)
        xsi=(1+ep2*rw)
        # Pressure (Pa)
        press-=g*dz*press/(R*tavg*xsi)
    #
    # No cloud
    if RH<100: return -999
    #
    # Return cloud base altitude
    return z


def calc_lwc_altitude(p_surf,theta,rw,zz):
    # Calculate cloud water mixing ratio at a given altitude z (m) when liquid water potential 
    # temperature (theta [k]) and water vapor mixing ratio (rw [kg/kg]) are constants. 
    # Surface pressure p_surf is given in Pa.
    #
    # Constants
    R=287.04    # Specific gas constant for dry air (R_specific=R/M), J/kg/K
    Rm=461.5    # -||- for water
    ep2=Rm/R-1.0 #M_air/M_water-1
    cp=1005.0    # Specific heat for a constant pressure
    rcp=R/cp
    cpr=cp/R
    g=9.8
    p00=1.0e+05
    alvl = 2.5e+06 #  ! latent heat of vaporization
    #
    # a) Integrate to cloud base altitude
    dz=1.            # 1 m resolution
    z=0.                # The first altitude
    press=p_surf    # Start from surface
    RH=0
    while z<zz:
        # Temperature (K) 
        tavg=theta*(press/p00)**rcp
        #
        # Current RH (%)
        RH=calc_rh(rw,tavg,press)
        if RH>100: break
        #
        # From z to z+dz
        z+=dz
        # Virtual temperature: T_virtual=T*(1+ep2*rl)
        xsi=(1+ep2*rw)
        # Pressure (Pa)
        press-=g*dz*press/(R*tavg*xsi)
    #
    # No cloud or cloud water
    if RH<100: return 0.0
    #
    # b) Integrate up to given altitude
    while z<zz:
        # From z to z+dz
        z+=dz
        #
        # Moist adiabatic lapse rate
        q_sat=calc_sat_mixr(press,tavg)
        tavg-=g*(1+alvl*q_sat/(R*tavg))/(cp+alvl**2*q_sat/(Rm*tavg**2))*dz
        #
        # New pressure
        xsi=(1+ep2*q_sat)
        press-=g*dz*press/(R*tavg*xsi)
    #
    # Return cloud water mixing ratio = totol - vapor
    return rw-q_sat

def calc_lwp(p_surf,theta,pblh,rt):
    # Calculate liquid water path (kg/m^2) when boundary layer liquid water potential temperature (theta [K]) and total
    # water mixing ratio (rt [kg/kg]) are constants from surface (p_surf, Pa) up to boundary layer top (pblh, Pa or km).
    # In addition to the liquid water path, function returns cloud base and top heights (m) and the maximum (or cloud top)
    # liquid water mixing ratio (kg/kg).
    #
    # Constants
    R=287.04    # Specific gas constant for dry air (R_specific=R/M), J/kg/K
    Rm=461.5    # -||- for water
    ep2=Rm/R-1.0 #M_air/M_water-1
    cp=1005.0    # Specific heat for a constant pressure
    rcp=R/cp
    g=9.8
    p00=1.0e+05
    alvl = 2.5e+06 #  ! latent heat of vaporization
    #
    # It is assumed that a pblh value smaller than 10 is in kilometers and a value larger than that is Pa
    if pblh<10.0:
        z_top=pblh*1000. # from km to m (above surface)
        p_top=0.
    else:
        z_top=10e3
        p_top=p_surf-pblh # Pa (above surface)
    #
    # Outputs
    lwp=0.    # Liquid water path (g/m^2)
    zb=-999.    # Cloud base height (m)
    zc=-999.    # Cloud top height (m)
    clw_max=0.    # Maximum cloud liquid water
    #
    # a) Integrate to cloud base altitude
    dz=1.            # 1 m resolution
    z=0.                # The first altitude
    press=p_surf    # Start from surface
    RH=0
    while press>p_top and z<=z_top:
        # Temperature (K) 
        tavg=theta*(press/p00)**rcp
        #
        # Current RH (%)
        RH=calc_rh(rt,tavg,press)
        if RH>100:
            zb=z
            break
        #
        # From z to z+dz
        z+=dz
        # Virtual temperature: T_virtual=T*(1+ep2*rl)
        xsi=(1+ep2*rt)
        # Pressure (Pa)
        press-=g*dz*press/(R*tavg*xsi)
    #
    # No cloud or cloud water
    if RH<=100: return lwp,zb,zc,clw_max
    zb=z
    #
    # b) Integrate up to the given altitude
    while press>p_top and z<=z_top:
        # From z to z+dz
        z+=dz
        #
        # Moist adiabatic lapse rate
        #q_sat=calc_sat_mixr(press,tavg)
        q_sat=calc_sat_mixr(press,tavg)
        tavg-=g*(1+alvl*q_sat/(R*tavg))/(cp+alvl**2*q_sat/(Rm*tavg**2))*dz
        #
        # New pressure
        xsi=(1+ep2*q_sat)
        press-=g*dz*press/(R*tavg*xsi)
        #
        # Cloud water mixing ratio = totol - vapor
        rc=max(0.,rt-q_sat)
        # LWP integral
        lwp+=rc*dz*press/(R*tavg*xsi)
    #
    # Cloud top height
    zc=z
    clw_max=rc
    #
    # Return LWP (kg/m^2) and boundary layer height (m)
    return lwp,zb,zc,clw_max


def solve_rw(p_surf,theta,lwc,zz):
    # Solve total water mixing ratio (rw, kg/kg) from surface pressure (p_surf, Pa), liquid water potential
    # temperature (theta, K) and liquid water mixing ratio (lwc) at altitude zz (m)
    #
    # Constants
    R=287.04    # Specific gas constant for dry air (R_specific=R/M), J/kg/K
    Rm=461.5    # -||- for water
    ep2=Rm/R-1.0 #M_air/M_water-1
    cp=1005.0    # Specific heat for a constant pressure
    rcp=R/cp
    cpr=cp/R
    g=9.8
    p00=1.0e+05
    alvl = 2.5e+06 #  ! latent heat of vaporization
    #
    # Mimimum water vapor mixing ratio is at least lwc
    q_min=lwc
    #
    # Maximum water vapor mixing ratio is unlimited, but should be smaller
    # than that for a cloud which base is at surface
    t_surf=theta*(p_surf/p00)**rcp
    q_max=calc_sat_mixr(p_surf,t_surf)
    #
    k=0
    while k<100:
        q_new=(q_min+q_max)/2
        lwc_calc=calc_lwc_altitude(p_surf,theta,q_new,zz)
        #    
        if abs(lwc-lwc_calc)<1e-7:
            break
        elif lwc<lwc_calc:
            q_max=q_new
        else:
            q_min=q_new
        k+=1
        # Failed
        if k==50: return -999
    #
    return q_new

def solve_rw_lwp(p_surf,theta,lwp,pblh,debug=False):
    #             Pa    K     kg/m^2 km|Pa
    # Solve boundary layer total water mixing ratio (kg/kg) from liquid water potentialtemperature (theta [K]), 
    # liquid water path (lwp, kg/m^2) and boundary layer height (pblh, Pa or km) for an adiabatic cloud.
    # For example, solve_rw_lwp(101780.,293.,100e-3,20000.) would return 0.00723684088331 [kg/kg].
    #
    # Constants
    R=287.04    # Specific gas constant for dry air (R_specific=R/M), J/kg/K
    cp=1005.0    # Specific heat for a constant pressure
    rcp=R/cp
    p00=1.0e+05
    #
    # LWP tolerance: 0.1 % but not more than 0.1e-3 kg/m^2 and not less than 1e-3 kg/kg
    tol=min(max(0.001*lwp,0.1e-3),1e-3)
    #
    # Surface temperature (dry, i.e. no fog)
    t_surf=theta*(p_surf/p00)**rcp
    #
    # The highest LWP when RH=100% at the surface (no fog)
    rw_max= calc_sat_mixr(p_surf,t_surf)
    lwp_max,zb,zc,clw_max=calc_lwp(p_surf,theta,pblh,rw_max)
    # No fog cases
    if lwp_max<lwp:
        if debug: print('Too high LWP (%5.1f g/m2), the maximum is %5.1f g/m2 (theta=%6.2f K, pblh=%3.0f hPa)'%(lwp*1e3, lwp_max*1e3,theta,pblh/100.) )
        return -999.
    #
    # The lowest LWP when RH=0% at the surface
    rw_min=0.
    lwp_min,zb,zc,clw_max=calc_lwp(p_surf,theta,pblh,rw_min)
    if lwp_min>lwp:
        if debug: print('Too low LWP (%5.1f g/m2), the minimum is %5.1f g/m2 (theta=%6.2f K, pblh=%3.0f hPa)'%(lwp*1e3, lwp_max*1e3,theta,pblh/100.))
        return -999.
    #
    k=0
    while k<100:
        rw_new=(rw_min+rw_max)*0.5
        lwp_new,zb,zc,clw_max=calc_lwp(p_surf,theta,pblh,rw_new)
        #
        if abs(lwp-lwp_new)<tol or abs(rw_max-rw_min)<0.001e-3:
            return rw_new
        elif lwp<lwp_new:
            rw_max=rw_new
        else:
            rw_min=rw_new
        k+=1
    #
    # Failed
    if debug: print('Iteration failed: current LWP=%5.1f, target LWP=%5.1f')%(lwp_new*1e3,lwp*1e3)
    return -999.

def solve_q_inv_RH(press,tpot,q,max_RH):
    # Function for adjusting total water mixing ratio so that the calculated RH will be no more
    # than the given RH limit. This function can be used to increase humidity inversion so that RH
    # above cloud is less than 100%. For this purpose the typical inputs are:
    #    press [Pa] = p_surf - pblh
    #    tpot [K] = tpot_pbl + tpot_inv
    #    q [kg/kg] = q_pbl - q_inv
    #    RH [%] = 98.
    #
    # Constants
    R = 287.04    # Specific gas constant for dry air (R_specific=R/M), J/kg/K
    cp = 1005.0    # Specific heat for a constant pressure
    rcp = R/cp
    p00 = 1.0e+05
    #
    # Temperature (K)
    temp = tpot*( press/p00 )**rcp
    #
    # default values to be returned
    q_return = q
    rh_old_return = calc_rh( q, temp, press ) # RH (%)
    rh_new_return = rh_old_return
    
    iterate = True # if true, iterate and solve the new q_inv
    #
    
    #
    # Solve q so that RH=max_RH
    q_min=0.
    q_max=q
    k=0
    if rh_old_return <= max_RH: # nothing to be done original RH doesn't exceed the limit
        iterate = False # solution found
            
    while k < 200 and iterate:
        
        q_new = 0.5*( q_min + q_max )
        
        rh_new = calc_rh( q_new, temp, press )
        #
        if abs( rh_new - max_RH ) < 0.001 :
            iterate = False  # solution found
            q_return = q_new
            rh_new_return = rh_new
            
        elif rh_new > max_RH:
            q_max = q_new
            
        else:
            q_min = q_new
        
        k+=1
    
    
    if iterate: 
        # Failed, since 200 iterations didn't lead to a solution
        print( 'Failed to solve water vapor mixing ratio from given RH!' )
        q_return = -999.
        rh_new_return = -999.
        
    
    return q_return, rh_new_return, rh_old_return #  (solved) q,  (new) RH value, old RH value


#
## Test
## =====
##
#if 1<0: # Row 44 (Desing 17.2.2017)
#    tpot_pbl=296.9053557
#    q_pbl=13.89315857
#    pblh=1.985335669
#elif 1<0: # Row 15 (Desing 17.2.2017)
#    tpot_pbl=300.4348919
#    q_pbl=15.5071073
#    pblh=1.252502431
#else:    # "emul40"
#    tpot_pbl=297.857955
#    q_pbl=13.893159
#    pblh=2.4735
##
## Constant
#p_surf=101780. # Surface pressure (Pa)
#
#
## a) Calculate LWC at the top of boundary layer (maximum LWC)
#lwc_calc = calc_lwc_altitude( p_surf, tpot_pbl, q_pbl*1e-3, pblh*1000 )
#print "LWC(z=pblh)=", lwc_calc, "kg/kg when q_pbl=", q_pbl, "g/kg"
#
## b) Calculate q_pbl from the given maximum LWC
#q_pbl_calc = solve_rw( p_surf, tpot_pbl, lwc_calc, pblh*1000 ) 
#print "q_pbl=", q_pbl_calc, " kg/kg when LWC(z=pblh)=", lwc_calc, "kg/kg"
#
## Cloud base
#zb = calc_cloud_base( p_surf, tpot_pbl, q_pbl*1e-3 )
## Cloud top zc = pblh
## LWP=(zc-zb)*(0.0+LWC_max)/2=(zc-zb)*LWC_max/2
#print " zb=", zb, "m, zc=", pblh*1000, "m, LWP=", (pblh*1000-zb)*lwc_calc/2,'kg/kg'
