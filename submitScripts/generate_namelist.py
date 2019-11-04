#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  4 12:49:49 2018

@author: aholaj
"""



#def main(argv):
#   timmax1 = ''
#   Tspinup = ''
#   try:
#      opts, args = getopt.getopt(argv,"h:",["timmax=","Tspinup="])
#   except getopt.GetoptError:
#      print 'ERROR, usage: test.py -i <inputfile> -o <outputfile>'
#      sys.exit(2)
#   for opt, arg in opts:
#      if opt == '-h':
#         print 'test.py -i <inputfile> -o <outputfile>'
#         sys.exit()
#      elif opt in ("--timmax"):
#         timmax1 = arg
#         print "ti"
#      elif opt in ("--Tspinup"):
#         Tspinup = arg
#         print "ts", arg
#   print 'timmax file is ', timmax1
#   print 'Tspinup file is ', Tspinup
#
import getopt, sys, os, subprocess
   
def skip(s):
    s = str(s)
    r = True
    if s.lower() == 'skip':
        r = False
    return r


def write_namelist( argv, filu="NAMELIST"):

    
    apu = []
    for arra in argv:
        if arra[0:2] == '--':
            apu.append(arra)
            
    argv = apu

    Tspinup = '5400.'
    erikoiskeissi = 'not'
    
    design   = \
    case     = \
    q_inv    = \
    tpot_inv = \
    lwp  = \
    tpot_pbl = \
    pblh     = \
    num_pbl  = \
    'skip'
    
    os.chdir(os.environ["LES"])
    try:
        ver =subprocess.check_output("git describe --tags | tr -dc '[:alnum:].'", stderr=subprocess.STDOUT , shell=True).decode("utf-8")
    except subprocess.CalledProcessError:
        ver = "latest"
    if ("Not a git repository" in ver or "not found" in ver):
        ver = "latest"
        
    ################################
    ### NAMELIST values 
    ################################
    # &model
    level ="3"
    nxp =   "204" # Number of points in x direction
    nyp =   "204" # Number of points in y direction
    nzp =   "200" # Number of vertical levels
    deltax = "50." # Grid spacing in x
    deltay = "50." # Grid spacing in y
    deltaz = "20." # Grid spacing in the vertical
    nxpart = ".true."
    dzmax = "3500." # Height above which start stretching vertical grid
    dzrat = "1.0"   # Factor for vertical grid stretching
    dtlong = "2."   # Max. timestep
    distim = "100." # Timescale for the dissipation in sponge layer
    timmax = "12600."
    runtype = '"INITIAL"' # INITIAL or HISTORY (restart) run
    CCN = "600.e6"
    corflg = ".false." # Apply coriolis force
    prndtl = "-0.3333333"
    
    filprf = "'emul'" # Output filename profile
    hfilin = "'emul.rst'"
    
    ssam_intvl = "300." # Interval for statistical output
    savg_intvl = "300." # Averaging interval for stat output
    
    frqanl = "5400."  # Interval for full domain output
    frqhis = "30000."
    lbinanl = ".false." # Write binned microphysical output (with level >= 4)
    
    salsa_b_bins = ".FALSE."
    mcflg = ".FALSE." # Do mass conservation statistics
    
    sed_aero_switch = ".FALSE." # Calculate sedimentation of aerosol particles
    sed_cloud_switch = ".TRUE." # - '' - cloud droplets
    sed_cloud_delay = Tspinup
    sed_precp_switch = ".TRUE." # precipitation
    sed_precp_delay = Tspinup
    sed_ice_switch = ".FALSE." # ice particles
    sed_snow_switch = ".FALSE." # snow flakes/precipitating ice
    bulk_autoc_switch = ".TRUE."
    bulk_autoc_delay = Tspinup # Autoconversion switch for level = 1-3
    
    itsflg = "1" # Flag for temperature type in input sounding
    
    lnudging = ".TRUE." # Master switch for nudging scheme
    lemission = ".FALSE." # Master switch for aerosol emissions 
    iradtyp = "3" # Radiation/large scale forcing
    strtim = "180.0"# Start time
    cntlat = "30." # latitude
    case_name = "'default'" # Case name for large-scale forcing schemes
    div = "1.5e-6" # Large-scale divergence
    dthcon = "0." # heat flux 18.4613 # Sensible heat flux
    drtcon = "0."# latent 84.8921 # Latent heat flux
    isfctyp = 'skip' #2"
    sst = "271.35" # Surface temperature
    zrough = "0.01" # Roughness length
    ubmin= "-0.25"
    th00 = "289." # Reference temperature
    umean ="10."
    vmean = "0."

    # &radiation    
    radsounding = "'datafiles/kmls.lay'" 
    RadPrecipBins = "1"
    sfc_albedo = "0.05"
    zenithFlag = ".TRUE."

    # &nudge
    
    nudge_time = timmax # Overall time for nudging from the start of the simulation
    
    ndg_theta_nudgetype = "1"
    ndg_theta_tau_type = "2" # Type of relaxation time (0:constant, 1-3: increasing)
    ndg_theta_tau_min = "300." # Min relaxation time (with tau_type=1-3 and constant tau)
    ndg_theta_tau_max = "3600." # Max relaxation time (with tau_type=1-3)
    ndg_theta_tau_max_continue = ".FALSE."
    
    
     
    # &salsa
     
    lscoag_switch= ".TRUE." # Master coagulation switch
    lscoag_delay = Tspinup
     
    lscnd_switch = ".TRUE." # Master condensation switch
    
    lsauto_switch= ".TRUE." # Master autoconversion switch
    lsauto_delay = Tspinup
     
    lsactiv_switch = ".TRUE."# Master cloud activation switch
     
    lsicenucl_switch = ".FALSE."# Switch for ice nucleation
    lsicenucl_delay = Tspinup
    
    lsautosnow_switch = ".FALSE." # Master snow autoconversion switch
    
    lsicemelt_switch = ".FALSE." # Switch for ice'n' snow melting
    
    
    lscgcc = ".TRUE." # Self-collection of cloud droplets
    lscgpp = ".TRUE." # Self-collection of rain drops
    lscgpc = ".TRUE." # Rain collection of cloud droplets
    lscgaa = ".FALSE."# Aerosol coagulation
    lscgca = ".TRUE." # Cloud collection of aerosols
    lscgpa = ".TRUE." # Rain collection of aerosols
    lscgia = ".TRUE." # Ice collection of aerosols
    lscgic = ".TRUE." # Ice collection of cloud droplets
    lscgii = ".TRUE." # Self-collection of ice
    lscgip = ".TRUE." # Ice collection of rain drops
    lscgsa = ".TRUE." # Snow collection of aerosols
    lscgsc = ".TRUE." # Snow collection of cloud droplets
    lscgsi = ".TRUE." # Snow collection of ice particles
    lscgsp = ".TRUE." # Snow collection of rain drops
    lscgss = ".TRUE." # Self-collection of snow
    
    
    lscndgas   = ".FALSE." # --Aerosol precursor gas codensation
    lscndh2oae = ".TRUE."  # --Condensation of water on aerosols (if FALSE, equilibrium assumed)
    lscndh2ocl = ".TRUE."  # --Condensation of water on cloud droplets (and drizzle)
    lscndh2oic = ".TRUE."  # --Condensation of water on ice particles
    
    lsactbase  = ".FALSE."  # --Switch for parameterized cloud base activation
    lsactintst = ".TRUE."  # --Switch for interstitial activation based on host model Smax
    
    lscheckarrays = ".FALSE."
    
    lsfreeRH_switch = ".TRUE."
    lsfreeRH_delay = Tspinup
    rhlim = "1.001" # RH limit for SALSA during initialization and spinup
    
    isdtyp = "0"
    nspec = "1"
    listspec = "'SO4','','','','','',''" #### "'SO4','DU','OC','','','',''"
    volDistA = "1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0"
    volDistB = "0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0"
    nf2a = "1.0"
    
    sigmag = "1.3, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0"  # Stdev for initial aerosol size distribution for isdtyp == 0 (uniform)  
    dpg = "0.1, 1.0, 0.2, 0.2, 0.2, 0.2, 0.2"  # Mode mean diameters in micrometers
    nconc= "46.2502241367474, 0. , 0., 0., 0., 0., 0."  # Mode number concentrations in #/mg
    
    try:
       opts, args = getopt.getopt(argv,"h:",[ \
                                             "Tspinup=",\
                                             "erikoiskeissi=",\
                                             "design=",\
                                             "case=",\
                                             "q_inv=",\
                                             "tpot_inv=",\
                                             "lwp=",\
                                             "tpot_pbl=",\
                                             "pblh=",\
                                             "num_pbl=",\
                                             "timmax=",\
                                             "level=",\
                                             "nxp=",\
                                             "nyp=",\
                                             "nzp=",\
                                             "deltax=",\
                                             "deltay=",\
                                             "deltaz=",\
                                             "nxpart=",\
                                             "dzmax=",\
                                             "dzrat=",\
                                             "dtlong=",\
                                             "distim=",\
                                             "timmax=",\
                                             "runtype=",\
                                             "CCN=",\
                                             "corflg=",\
                                             "prndtl=",\
                                             "filprf=",\
                                             "hfilin=",\
                                             "ssam_intvl=",\
                                             "savg_intvl=",\
                                             "frqanl=",\
                                             "frqhis=",\
                                             "lbinanl=",\
                                             "salsa_b_bins=",\
                                             "mcflg=",\
                                             "sed_aero_switch=",\
                                             "sed_cloud_switch=",\
                                             "sed_cloud_delay=",\
                                             "sed_precp_switch=",\
                                             "sed_precp_delay=",\
                                             "sed_ice_switch=",\
                                             "sed_snow_switch=",\
                                             "bulk_autoc_switch=",\
                                             "bulk_autoc_delay=",\
                                             "itsflg=",\
                                             "lnudging=",\
                                             "lemission=",\
                                             "iradtyp=",\
                                             "strtim=",\
                                             "cntlat=",\
                                             "case_name=",\
                                             "div=",\
                                             "dthcon=",\
                                             "drtcon=",\
                                             "isfctyp=",\
                                             "sst=",\
                                             "zrough=",\
                                             "ubmin=",\
                                             "th00=",\
                                             "umean=",\
                                             "vmean=",\
                                             "radsounding=",\
                                             "RadPrecipBins=",\
                                             "sfc_albedo=",\
                                             "zenithFlag=",\
                                             "nudge_time=",\
                                             "ndg_theta_nudgetype=",\
                                             "ndg_theta_tau_type=",\
                                             "ndg_theta_tau_min=",\
                                             "ndg_theta_tau_max=",\
                                             "ndg_theta_tau_max_continue=",\
                                             "lscoag_switch=",\
                                             "lscoag_delay=",\
                                             "lscnd_switch=",\
                                             "lsauto_switch=",\
                                             "lsauto_delay=",\
                                             "lsactiv_switch=",\
                                             "lsicenucl_switch=",\
                                             "lsicenucl_delay=",\
                                             "lsautosnow_switch=",\
                                             "lsicemelt_switch=",\
                                             "lscgcc=",\
                                             "lscgpp=",\
                                             "lscgpc=",\
                                             "lscgaa=",\
                                             "lscgca=",\
                                             "lscgpa=",\
                                             "lscgia=",\
                                             "lscgic=",\
                                             "lscgii=",\
                                             "lscgip=",\
                                             "lscgsa=",\
                                             "lscgsc=",\
                                             "lscgsi=",\
                                             "lscgsp=",\
                                             "lscgss=",\
                                             "lscndgas=",\
                                             "lscndh2oae=",\
                                             "lscndh2ocl=",\
                                             "lscndh2oic=",\
                                             "lsactbase=",\
                                             "lsactintst=",\
                                             "lscheckarrays=",\
                                             "lsfreeRH_switch=",\
                                             "lsfreeRH_delay=",\
                                             "rhlim=",\
                                             "isdtyp=",\
                                             "nspec=",\
                                             "listspec=",\
                                             "volDistA=",\
                                             "volDistB=",\
                                             "nf2a=",\
                                             "sigmag=",\
                                             "dpg=",\
                                             "nconc=",\
                                             "nudge_theta=",\
                                             "nudge_theta_time=",\
                                             "nudge_theta_tau=",\
                                             "nudge_ccn=",\
                                             "nudge_ccn_time=",\
                                             "nudge_ccn_zmin=",\
                                             "nudge_ccn_zmax=",\
                                             "nudge_ccn_tau=",\
                                             "lbinprof=",\
                                             "anl_start=",\
                                             "istpfl=",\
                                             "stat_micro=",\
                                             "stat_micro_ts=",\
                                             "stat_micro_ps=",\
                                             "sed_aero=",\
                                             "sed_cloud=",\
                                             "sed_precp=",\
                                             "zrndamp=",\
                                             "zrndampq=",\
                                             "nlcoag=",\
                                             "nlcgaa=",\
                                             "nlcnd=",\
                                             "nlcndgas=",\
                                             "nlcndh2oae=",\
                                             "nlcndh2ocl=",\
                                             "nlauto=",\
                                             "nlactiv=",\
                                             "nlactbase=",\
                                             "nlactintst="])

    except getopt.GetoptError:
       print('ERROR, usage: test.py -i <inputfile> -o <outputfile>')
       sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -i <inputfile> -o <outputfile>')
            sys.exit()
        
        elif opt in ("--Tspinup"):
            Tspinup = arg
            sed_cloud_delay = Tspinup
            sed_precp_delay = Tspinup
            bulk_autoc_delay = Tspinup
            lscoag_delay = Tspinup
            lsauto_delay = Tspinup
            lsicenucl_delay = Tspinup
            lsfreeRH_delay = Tspinup
        elif opt in ("--erikoiskeissi"):
            erikoiskeissi = arg
        elif opt in ("--design"):
            design = arg
        elif opt in ("--case"):
            case = arg
        elif opt in ("--q_inv"):
            q_inv = arg
        elif opt in ("--tpot_inv"):
            tpot_inv = arg
        elif opt in ("--lwp"):
            lwp = arg
        elif opt in ("--tpot_pbl"):
            tpot_pbl = arg
        elif opt in ("--pblh"):
            pblh = arg
        elif opt in ("--num_pbl"):
            num_pbl = arg
        elif opt in ("--level"):
            level = arg
        elif opt in ("--nxp"):
            nxp = arg
        elif opt in ("--nyp"):
            nyp = arg
        elif opt in ("--nzp"):
            nzp = arg
        elif opt in ("--deltax"):
            deltax = arg
        elif opt in ("--deltay"):
            deltay = arg
        elif opt in ("--deltaz"):
            deltaz = arg
        elif opt in ("--nxpart"):
            nxpart = arg
        elif opt in ("--dzmax"):
            dzmax = arg
        elif opt in ("--dzrat"):
            dzrat = arg
        elif opt in ("--dtlong"):
            dtlong = arg
        elif opt in ("--distim"):
            distim = arg
        elif opt in ("--timmax"):
            timmax = arg
        elif opt in ("--runtype"):
            runtype = arg
        elif opt in ("--CCN"):
            CCN = arg
        elif opt in ("--corflg"):
            corflg = arg
        elif opt in ("--prndtl"):
            prndtl = arg
        elif opt in ("--filprf"):            
            filprf = arg
        elif opt in ("--hfilin"):
            hfilin = arg
        elif opt in ("--ssam_intvl"):            
            ssam_intvl = arg
        elif opt in ("--savg_intvl"):
            savg_intvl = arg
        elif opt in ("--frqanl"):            
            frqanl = arg
        elif opt in ("--frqhis"):
            frqhis = arg
        elif opt in ("--lbinanl"):
            lbinanl = arg
        elif opt in ("--salsa_b_bins"):            
            salsa_b_bins = arg
        elif opt in ("--mcflg"):
            mcflg = arg
        elif opt in ("--sed_aero_switch"):            
            sed_aero_switch = arg
        elif opt in ("--sed_cloud_switch"):
            sed_cloud_switch = arg
        elif opt in ("--sed_cloud_delay"):
            sed_cloud_delay = arg
        elif opt in ("--sed_precp_switch"):
            sed_precp_switch = arg
        elif opt in ("--sed_precp_delay"):
            sed_precp_delay = arg
        elif opt in ("--sed_ice_switch"):
            sed_ice_switch = arg
        elif opt in ("--sed_snow_switch"):
            sed_snow_switch = arg
        elif opt in ("--bulk_autoc_switch"):
            bulk_autoc_switch = arg
        elif opt in ("--bulk_autoc_delay"):
            bulk_autoc_delay = arg
        elif opt in ("--itsflg"):            
            itsflg = arg
        elif opt in ("--lnudging"):            
            lnudging = arg
        elif opt in ("--lemission"):
            lemission = arg
        elif opt in ("--iradtyp"):
            iradtyp = arg
        elif opt in ("--strtim"):
            strtim = arg
        elif opt in ("--cntlat"):
            cntlat = arg
        elif opt in ("--case_name"):
            case_name = arg
        elif opt in ("--div"):
            div = arg
        elif opt in ("--dthcon"):
            dthcon = arg
        elif opt in ("--drtcon"):
            drtcon = arg
        elif opt in ("--isfctyp"):
            isfctyp = arg
        elif opt in ("--sst"):
            sst = arg
        elif opt in ("--zrough"):
            zrough = arg
        elif opt in ("--ubmin"):
            ubmin= arg
        elif opt in ("--th00"):
            th00 = arg
        elif opt in ("--umean"):
            umean = arg
        elif opt in ("--vmean"):
            vmean = arg
        elif opt in ("--radsounding"):        
            radsounding = arg
        elif opt in ("--RadPrecipBins"):
            RadPrecipBins = arg
        elif opt in ("--sfc_albedo"):
            sfc_albedo = arg
        elif opt in ("--zenithFlag"):
            zenithFlag = arg
        elif opt in ("--nudge_time"):            
            nudge_time = arg
        elif opt in ("--ndg_theta_nudgetype"):            
            ndg_theta_nudgetype = arg
        elif opt in ("--ndg_theta_tau_type"):
            ndg_theta_tau_type = arg
        elif opt in ("--ndg_theta_tau_min"):
            ndg_theta_tau_min = arg
        elif opt in ("--ndg_theta_tau_max"):
            ndg_theta_tau_max = arg
        elif opt in ("--ndg_theta_tau_max_continue"):
            ndg_theta_tau_max_continue = arg
        elif opt in ("--lscoag_switch"):            
            lscoag_switch= arg
        elif opt in ("--lscoag_delay"):
            lscoag_delay = arg
        elif opt in ("--lscnd_switch"):             
            lscnd_switch = arg
        elif opt in ("--lsauto_switch"):            
            lsauto_switch= arg
        elif opt in ("--lsauto_delay"):
            lsauto_delay = arg
        elif opt in ("--lsactiv_switch"):             
            lsactiv_switch = arg
        elif opt in ("--lsicenucl_switch"):             
            lsicenucl_switch = arg
        elif opt in ("--lsicenucl_delay"):
            lsicenucl_delay = arg
        elif opt in ("--lsautosnow_switch"):            
            lsautosnow_switch = arg
        elif opt in ("--lsicemelt_switch"):            
            lsicemelt_switch = arg
        elif opt in ("--lscgcc"):                        
            lscgcc = arg
        elif opt in ("--lscgpp"):
            lscgpp = arg
        elif opt in ("--lscgpc"):
            lscgpc = arg
        elif opt in ("--lscgaa"):
            lscgaa = arg
        elif opt in ("--lscgca"):
            lscgca = arg
        elif opt in ("--lscgpa"):
            lscgpa = arg
        elif opt in ("--lscgia"):
            lscgia = arg
        elif opt in ("--lscgic"):
            lscgic = arg
        elif opt in ("--lscgii"):
            lscgii = arg
        elif opt in ("--lscgip"):
            lscgip = arg
        elif opt in ("--lscgsa"):
            lscgsa = arg
        elif opt in ("--lscgsc"):
            lscgsc = arg
        elif opt in ("--lscgsi"):
            lscgsi = arg
        elif opt in ("--lscgsp"):
            lscgsp = arg
        elif opt in ("--lscgss"):
            lscgss = arg
        elif opt in ("--lscndgas"):                        
            lscndgas   = arg
        elif opt in ("--lscndh2oae"):
            lscndh2oae = arg
        elif opt in ("--lscndh2ocl"):
            lscndh2ocl = arg
        elif opt in ("--lscndh2oic"):
            lscndh2oic = arg
        elif opt in ("--lsactbase"):            
            lsactbase  = arg
        elif opt in ("--lsactintst"):
            lsactintst = arg
        elif opt in ("--lscheckarrays"):            
            lscheckarrays = arg
        elif opt in ("--lsfreeRH_switch"):            
            lsfreeRH_switch = arg
        elif opt in ("--lsfreeRH_delay"):
            lsfreeRH_delay = arg
        elif opt in ("--rhlim"):
            rhlim = arg
        elif opt in ("--isdtyp"):            
            isdtyp = arg
        elif opt in ("--nspec"):
            nspec = arg
        elif opt in ("--listspec"):
            listspec = arg
        elif opt in ("--volDistA"):
            volDistA = arg
        elif opt in ("--volDistB"):
            volDistB = arg
        elif opt in ("--nf2a"):
            nf2a = arg
        elif opt in ("--sigmag"):            
            sigmag = arg
        elif opt in ("--dpg"):
            dpg = arg
        elif opt in ("--nconc"):
            nconc = arg
        elif opt in ("--nudge_theta"):
            nudge_theta = arg
        elif opt in ("--nudge_theta_time"):
            nudge_theta_time = arg
        elif opt in ("--nudge_theta_tau"):
            nudge_theta_tau = arg
        elif opt in ("--nudge_ccn"):
            nudge_ccn = arg
        elif opt in ("--nudge_ccn_time"):
            nudge_ccn_time = arg
        elif opt in ("--nudge_ccn_zmin"):
            nudge_ccn_zmin = arg
        elif opt in ("--nudge_ccn_zmax"):
            nudge_ccn_zmax = arg
        elif opt in ("--nudge_ccn_tau"):
            nudge_ccn_tau = arg
        elif opt in ("--lbinprof"):
            lbinprof = arg
        elif opt in ("--anl_start"):
             anl_start = arg
        elif opt in ("--istpfl"):
            istpfl = arg
        elif opt in ("--stat_micro"):
            stat_micro = arg
        elif opt in ("--stat_micro_ts"):
            stat_micro_ts = arg
        elif opt in ("--stat_micro_ps"):
            stat_micro_ps = arg
        elif opt in ("--sed_aero"):
            sed_aero = arg
        elif opt in ("--sed_cloud"):
            sed_cloud = arg
        elif opt in ("--sed_precp"):
            sed_precp = arg    
        elif opt in ("--zrndamp"):
             zrndamp = arg
        elif opt in ("--zrndampq"):
            zrndampq = arg
        elif opt in ("--nlcoag"):
           nlcoag = arg
        elif opt in ("--nlcgaa"):
            nlcgaa = arg
        elif opt in ("--nlcnd"):
             nlcnd = arg
        elif opt in ("--nlcndgas"):
            nlcndgas = arg
        elif opt in ("--nlcndh2oae"):
            nlcndh2oae = arg
        elif opt in ("--nlcndh2ocl"):
           nlcndh2ocl  = arg
        elif opt in ("--nlauto"):
           nlauto  = arg
        elif opt in ("--nlactiv"):
           nlactiv  = arg
        elif opt in ("--nlactbase"):
            nlactbase = arg
        elif opt in ("--nlactintst"):
            nlactintst = arg


            
    lines = []

    lines.append( "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" )  if skip(design) else False
    lines.append( "!!! {0} {1}".format("DESIGN VERSION", design      )) if skip(design) else False
    lines.append( "!!! {0} {1}".format("design variables case", case )) if skip(case) else False
    lines.append( "!!! {0} == {1:7.2f} {2:12s}".format( "q_inv".ljust(8),       float(q_inv),      "[g/kg]" )) if skip(q_inv) else False
    lines.append( "!!! {0} == {1:7.2f} {2:12s}".format( "tpot_inv".ljust(8),    float(tpot_inv),   "[K]"    )) if skip(tpot_inv) else False
    lines.append( "!!! {0} == {1:7.2f} {2:12s}".format( "lwp".ljust(8),     float(lwp),    "[g/m^2]" )) if skip(lwp) else False
    lines.append( "!!! {0} == {1:7.2f} {2:12s}".format( "tpot_pbl".ljust(8),    float(tpot_pbl),   "[K]"    )) if skip(tpot_pbl) else False
    lines.append( "!!! {0} == {1:7.2f} {2:12s}".format( "pblh".ljust(8),        float(pblh),       "[m]"    )) if skip(pblh) else False
    lines.append( "!!! {0} == {1:7.2f} {2:12s}".format( "num_pbl".ljust(8),     float(num_pbl),    "[#/mg]" )) if skip(num_pbl) else False
    lines.append( "!!! {0} == {1:7.2f} {2:12s}".format( "cntlat".ljust(8),     float(cntlat),    "[deg]" )) if skip(cntlat) else False
    lines.append( "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" ) if skip(design) else False
    lines.append("")
    lines.append( " &version")
    lines.append( "  {0} = {1} {2}".format("ver", '"' + ver + '"', "" ))
    lines.append( " /")
    lines.append("")
    
    lines.append( " &model")
    lines.append( "  {0} = {1}  {2}".format("level",  level, "") ) 
    lines.append( "  {0} = {1}  {2}".format("nxp",    nxp, "! Number of points in x direction" ))
    lines.append( "  {0} = {1}  {2}".format("nyp",    nyp, "! Number of points in y direction" ))
    lines.append( "  {0} = {1}  {2}".format("nzp",    nzp, "! Number of vertical levels" ))
    lines.append( "  {0} = {1}  {2}".format("deltax", deltax, "! Grid spacing in x"))
    lines.append( "  {0} = {1}  {2}".format("deltay", deltay, "! Grid spacing in y"))
    lines.append( "  {0} = {1}  {2}".format("deltaz", deltaz, "! Grid spacing in the vertical"))
    lines.append( "  {0} = {1}  {2}".format("nxpart", nxpart, ""))
    lines.append( "  {0} = {1}  {2}".format("dzmax", dzmax, "! Height above which start stretching vertical grid"))
    lines.append( "  {0} = {1}  {2}".format("dzrat", dzrat, "! Factor for vertical grid stretching"))
    lines.append( "  {0} = {1}  {2}".format("dtlong", dtlong, "! Max. timestep"))
    lines.append( "  {0} = {1}  {2}".format("distim", distim, "! Timescale for the dissipation in sponge layer")) if skip(distim) else False
    lines.append( "  {0} = {1}  {2}".format("timmax", timmax, ""))
    lines.append( "  {0} = {1}  {2}".format("runtype", runtype,"! INITIAL or HISTORY (restart) run"))
    lines.append( "  {0} = {1}  {2}".format("CCN", CCN, "" ))
    lines.append( "  {0} = {1}  {2}".format("corflg", corflg, "! Apply coriolis force" ))
    lines.append( "  {0} = {1}  {2}".format("prndtl", prndtl,""))
    lines.append("")  
    lines.append( "  {0} = {1}  {2}".format("filprf", filprf, "! Output filename profile"))
    lines.append( "  {0} = {1}  {2}".format("hfilin", hfilin,"! History filename"))
    lines.append("")  
    lines.append( "  {0} = {1}  {2}".format("ssam_intvl", ssam_intvl, "! Interval for statistical output"))
    lines.append( "  {0} = {1}  {2}".format("savg_intvl", savg_intvl, "! Averaging interval for stat output"))
    lines.append("")
    lines.append( "  {0} = {1}  {2}".format("frqanl", frqanl, "! Interval for full domain output"))
    lines.append( "  {0} = {1}  {2}".format("frqhis", frqhis, ""))
    lines.append( "  {0} = {1}  {2}".format("lbinanl", lbinanl, "! Write binned microphysical output (with level >= 4)"))
    lines.append("")  
    lines.append( "  {0} = {1}  {2}".format("salsa_b_bins", salsa_b_bins, ""))
    lines.append( "  {0} = {1}  {2}".format("mcflg", mcflg, "! Do mass conservation statistics"))
    lines.append("")
    lines.append( "  {0} = {1}  {2}".format("sed_aero%switch", sed_aero_switch, "! Calculate sedimentation of aerosol particles"))
    lines.append( "  {0} = {1}  {2}".format("sed_cloud%switch", sed_cloud_switch, "! - '' - cloud droplets"))
    lines.append( "  {0} = {1}  {2}".format("sed_cloud%delay", sed_cloud_delay, ""))
    lines.append( "  {0} = {1}  {2}".format("sed_precp%switch", sed_precp_switch, "! precipitation"))
    lines.append( "  {0} = {1}  {2}".format("sed_precp%delay", sed_precp_delay, ""))
    lines.append( "  {0} = {1}  {2}".format("sed_ice%switch", sed_ice_switch, "! ice particles"))
    lines.append( "  {0} = {1}  {2}".format("sed_snow%switch", sed_snow_switch, "! snow flakes/precipitating ice"))
    lines.append( "  {0} = {1}  {2}".format("bulk_autoc%switch", bulk_autoc_switch, ""))
    lines.append( "  {0} = {1}  {2}".format("bulk_autoc%delay", bulk_autoc_delay, "! Autoconversion switch for level = 1-3  "))
    lines.append("")  
    lines.append( "  {0} = {1}  {2}".format("itsflg", itsflg, "! Flag for temperature type in input sounding"))
    lines.append( "  {0} = {1}  {2}".format("lnudging", lnudging, "! Master switch for nudging scheme"))
    lines.append( "  {0} = {1}  {2}".format("lemission", lemission, "! Master switch for aerosol emissions   "))
    lines.append( "  {0} = {1}  {2}".format("iradtyp", iradtyp, "! Radiation/large scale forcing"))
    lines.append( "  {0} = {1}  {2}".format("strtim", strtim, "! Start time"))
    lines.append( "  {0} = {1}  {2}".format("cntlat",cntlat, "! latitude"))
    lines.append( "  {0} = {1}  {2}".format("case_name", case_name, "! Case name for large-scale forcing schemes"))
    lines.append( "  {0} = {1}  {2}".format("div", div, "! Large-scale divergence"))
    lines.append( "  {0} = {1}  {2}".format("dthcon", dthcon, "! heat flux 18.4613 ! Sensible heat flux"))
    lines.append( "  {0} = {1}  {2}".format("drtcon", drtcon, "! latent 84.8921   ! Latent heat flux"))
    lines.append( "  {0} = {1}  {2}".format("isfctyp",isfctyp, ""))
    lines.append( "  {0} = {1}  {2}".format("sst", sst, "! Surface temperature"))
    lines.append( "  {0} = {1}  {2}".format("zrough", zrough, "! Roughness length"))
    lines.append( "  {0} = {1}  {2}".format("ubmin", ubmin, ""))
    lines.append( "  {0} = {1}  {2}".format("th00", th00, "! Reference temperature"))
    lines.append( "  {0} = {1}  {2}".format("umean", umean, ""))
    lines.append( "  {0} = {1}  {2}".format("vmean", vmean, ""))
    lines.append("")
    lines.append( " /")
    lines.append( " ! With iradtyp = 3")
    lines.append( " &radiation")
    lines.append("") 
    lines.append( "  {0} = {1}  {2}".format("radsounding",radsounding, ""))
    lines.append( "  {0} = {1}  {2}".format("RadPrecipBins", RadPrecipBins, ""))
    lines.append( "  {0} = {1}  {2}".format("sfc_albedo", sfc_albedo, ""))
    lines.append( "  {0} = {1}  {2}".format("zenithFlag", zenithFlag, ""))
    lines.append( " /")
    lines.append("") 
    lines.append("")
    lines.append( " ! With lnudging = .TRUE. ")
    lines.append( " &nudge")
    lines.append("")
    lines.append( "  {0} = {1}  {2}".format("nudge_time", nudge_time, "! Overall time for nudging from the start of the simulation"))
    lines.append("")
    lines.append( "  {0} = {1}  {2}".format("ndg_theta%nudgetype", ndg_theta_nudgetype,""))
    lines.append( "  {0} = {1}  {2}".format("ndg_theta%tau_type", ndg_theta_tau_type, "! Type of relaxation time (0:constant, 1-3: increasing)"))
    lines.append( "  {0} = {1}  {2}".format("ndg_theta%tau_min",ndg_theta_tau_min, "! Min relaxation time (with tau_type=1-3 and constant tau)"))
    lines.append( "  {0} = {1}  {2}".format("ndg_theta%tau_max", ndg_theta_tau_max, "! Max relaxation time (with tau_type=1-3)"))
    lines.append( "  {0} = {1}  {2}".format("ndg_theta%tau_max_continue", ndg_theta_tau_max_continue,""))
    lines.append("")
    lines.append( " /" )
    lines.append("") 
    lines.append( " &salsa")
    lines.append("") 
    lines.append( "  {0} = {1}  {2}".format("lscoag%switch", lscoag_switch, "! Master coagulation switch"))
    lines.append( "  {0} = {1}  {2}".format("lscoag%delay", lscoag_delay,""))
    lines.append("")   
    lines.append( "  {0} = {1}  {2}".format("lscnd%switch", lscnd_switch, "! Master condensation switch"))
    lines.append("")   
    lines.append( "  {0} = {1}  {2}".format("lsauto%switch", lsauto_switch,  "! Master autoconversion switch"))
    lines.append( "  {0} = {1}  {2}".format("lsauto%delay", lsauto_delay,""))
    lines.append("")   
    lines.append( "  {0} = {1}  {2}".format("lsactiv%switch", lsactiv_switch, "! Master cloud activation switch"))
    lines.append("")   
    lines.append( "  {0} = {1}  {2}".format("lsicenucl%switch", lsicenucl_switch, "! Switch for ice nucleation"))
    lines.append( "  {0} = {1}  {2}".format("lsicenucl%delay",  lsicenucl_delay, ""))
    lines.append("")   
    lines.append( "  {0} = {1}  {2}".format("lsautosnow%switch", lsautosnow_switch, "! Master snow autoconversion switch"))
    lines.append("")   
    lines.append( "  {0} = {1}  {2}".format("lsicemelt%switch", lsicemelt_switch, "! Switch for ice'n' snow melting"))
    lines.append("")
    lines.append("")   
    lines.append( "  {0} = {1}  {2}".format("lscgcc", lscgcc, "! Self-collection of cloud droplets"))
    lines.append( "  {0} = {1}  {2}".format("lscgpp", lscgpp, "! Self-collection of rain drops"))
    lines.append( "  {0} = {1}  {2}".format("lscgpc", lscgpc, "! Rain collection of cloud droplets"))
    lines.append( "  {0} = {1}  {2}".format("lscgaa", lscgaa, "! Aerosol coagulation"))
    lines.append( "  {0} = {1}  {2}".format("lscgca", lscgca, "! Cloud collection of aerosols"))
    lines.append( "  {0} = {1}  {2}".format("lscgpa", lscgpa, "! Rain collection of aerosols"))
    lines.append( "  {0} = {1}  {2}".format("lscgia", lscgia, "! Ice collection of aerosols"))
    lines.append( "  {0} = {1}  {2}".format("lscgic", lscgic, "! Ice collection of cloud droplets"))
    lines.append( "  {0} = {1}  {2}".format("lscgii", lscgii, "! Self-collection of ice"))
    lines.append( "  {0} = {1}  {2}".format("lscgip", lscgip, "! Ice collection of rain drops"))
    lines.append( "  {0} = {1}  {2}".format("lscgsa", lscgsa, "! Snow collection of aerosols"))
    lines.append( "  {0} = {1}  {2}".format("lscgsc", lscgsc, "! Snow collection of cloud droplets"))
    lines.append( "  {0} = {1}  {2}".format("lscgsi", lscgsi, "! Snow collection of ice particles"))
    lines.append( "  {0} = {1}  {2}".format("lscgsp", lscgsp, "! Snow collection of rain drops"))
    lines.append( "  {0} = {1}  {2}".format("lscgss", lscgss, "! Self-collection of snow"))
    lines.append("")
    lines.append("")   
    lines.append( "  {0} = {1}  {2}".format("lscndgas", lscndgas, "! --Aerosol precursor gas codensation"))
    lines.append( "  {0} = {1}  {2}".format("lscndh2oae", lscndh2oae, "! --Condensation of water on aerosols (if FALSE, equilibrium assumed)"))
    lines.append( "  {0} = {1}  {2}".format("lscndh2ocl", lscndh2ocl, "! --Condensation of water on cloud droplets (and drizzle)"))
    lines.append( "  {0} = {1}  {2}".format("lscndh2oic", lscndh2oic, "! --Condensation of water on ice particles"))
    lines.append("")   
    lines.append( "  {0} = {1}  {2}".format("lsactbase", lsactbase, "! --Switch for parameterized cloud base activation"))
    lines.append( "  {0} = {1}  {2}".format("lsactintst", lsactintst, "! --Switch for interstitial activation based on host model Smax"))
    lines.append("")
    lines.append( "  {0} = {1}  {2}".format("lscheckarrays",lscheckarrays,""))
    lines.append("")   
    lines.append( "  {0} = {1}  {2}".format("lsfreeRH%switch",lsfreeRH_switch,""))
    lines.append( "  {0} = {1}  {2}".format("lsfreeRH%delay",lsfreeRH_delay,""))
    lines.append( "  {0} = {1}  {2}".format("rhlim",rhlim, "! RH limit for SALSA during initialization and spinup"))
    lines.append("")
    lines.append( "  {0} = {1}  {2}".format("isdtyp",isdtyp, ""))
    lines.append( "  {0} = {1}  {2}".format("nspec",nspec, ""))
    lines.append( "  {0} = {1}  {2}".format("listspec", listspec, "!!!! 'SO4','DU','OC','','','','' "))
    lines.append( "  {0} = {1}  {2}".format("volDistA", volDistA,""))
    lines.append( "  {0} = {1}  {2}".format("volDistB", volDistB,""))
    lines.append( "  {0} = {1}  {2}".format("nf2a", nf2a, ""))
    lines.append("")
    lines.append( "  {0} = {1}  {2}".format("sigmag", sigmag, "! Stdev for initial aerosol size distribution for isdtyp == 0 (uniform)  "))
    lines.append( "  {0} = {1}  {2}".format("dpg", dpg, "! Mode mean diameters in micrometers"))
    lines.append( "  {0} = {1}  {2}".format("n", nconc, "! Mode number concentrations in #/mg"))
    lines.append( " /" )
    
    
    f = open(filu,'w')
    
    for ll in lines:
        f.write(ll)
        f.write("\n")
    f.close()
                
if __name__ == "__main__":
   write_namelist(sys.argv[1:], filu=os.environ["HOME"]+"NAMELIST")