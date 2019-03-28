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
    nxp =   "204"
    nyp =   "204"
    nzp =   "178"
    deltax = "50."
    deltay = "50."
    deltaz = "10."
    nxpart = ".true."
    dzmax = "3500."
    dzrat  = "1.0"
    dtlong = "2."
    timmax = "12600."
    Tspinup = "5400."

    nudge_theta = "1" #! Continuous liquid water potential temperature nudging
    nudge_theta_time = "12600."
    nudge_theta_tau = "3600."

    nudge_ccn = "1" #! Nudge aerosol for the lowermost layer
    nudge_ccn_time = "12600."
    nudge_ccn_zmin = "0."
    nudge_ccn_zmax = "10." #! Set this to deltaz
    nudge_ccn_tau = "3600."

    runtype = "'INITIAL'"
    level = "4" #! Level 3 or 4
    CCN = "74490576.0" #! Level 3 CDNC
    prndtl = "-0.3333333"
    filprf = "'emul076'"
    hfilin = "'emul076.rst'"
    ssam_intvl = "300."
    savg_intvl = "300."
    lbinprof = ".FALSE."
    frqhis  = "30000."
    frqanl = "900."
    anl_start = "9000." #! Save 3D outputs from the last simulation hour
    istpfl = "1"
    corflg = ".false."
    itsflg = "1"
    sed_aero = ".FALSE."
    sed_cloud = ".TRUE."
    sed_precp = ".TRUE."
    iradtyp = "3"
    case_name = "'default'" #! default = simple divergence forcing with specified div
    div = "1.5e-6"
    strtim = "-180.0"
    cntlat = "90." #! Solar zenith angle in degrees
    sfc_albedo = "0.05"
    radsounding = "'auto'"
    RadPrecipBins = "1"
    sst = "292.74" #! Sea-surface and surface skin temperature

    stat_micro = ".TRUE." #! Statistics about microphysical processes
    stat_micro_ts = ".TRUE."
    stat_micro_ps = ".TRUE."

    isfctyp = "0"
    dthcon = "0.0"
    drtcon = "0.0"
    ubmin  = "0.25"
    zrough = "0.0002"
    th00 = "291.27" #! Potential temperature at the surface

    umean =  "10."
    vmean = "0."

    zrndamp = "0."
    zrndampq = "0."
 
 #&salsa    
    nlcoag = ".TRUE."       #! Master coagulation switch
    nlcgaa = ".FALSE."      #! Aerosol coagulation

    nlcnd       = ".TRUE."  #! Master condensation switch
    nlcndgas    = ".FALSE."  #! --Aerosol precursor gas condensation
    nlcndh2oae  = ".TRUE."  #! --Condensation of water on aerosols
    nlcndh2ocl  = ".TRUE."  #! --Condensation of water on cloud droplets and drizzle
    nlauto      = ".TRUE."  #! Master autoconversion switch

    nlactiv     = ".TRUE."  #! Master cloud activation switch
    nlactbase   = ".FALSE."  #! --Switch for parameterized cloud base activation
    nlactintst  = ".TRUE."  #! --Switch for interstitial activation based on host model Smax

    rhlim = "1.2"          #! RH limit for SALSA during initialization and spinup

    nspec = "1"
    listspec = "'SO4','','','','','',''"
    volDistA = "1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0"
    volDistB = "0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0"
    nf2a = "1.0"
    
    rainbinlim = "skip" #"20.0,25.2,31.7,40.0,50.3,63.5,80.0,100.,127.,160.,201.,254.,320.,403.,508.,640.,806.,1001.,1280.,1612.,2000."
    ira_stat = "skip" # "7"

    sigmag = "1.59, 1.59, 2.0, 2.0, 2.0, 2.0, 2.0"  #! Stdev for initial aerosol size distribution
    dpg    = " 0.0209, 0.2, 0.9626, 0.2, 0.2, 0.2, 0.2"     #! Mode mean diameters in micrometers
    nconc  = "74.490576, 0., 0., 0., 0., 0., 0."  #! Mode number concentrations in #/mg
 
    
    try:
       opts, args = getopt.getopt(argv,"h:",[ \
                                             "Tspinup=",\
                                             "erikoiskeissi=",\
                                             "ver=",\
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
                                             "rainbinlim=",\
                                             "ira_stat=",\
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
        elif opt in ("--ver"):
            ver = arg
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
        elif opt in ("--rainbinlim"):
            rainbinlim = arg            
        elif opt in ("--ira_stat"):
            ira_stat = arg            
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
    lines.append( "  {0} = {1}  {2}".format("level".ljust(7),  level, "") ) 
    lines.append( "  {0} = {1}  {2}".format("nxp".ljust(7),    nxp, "! Number of points in x direction" ))
    lines.append( "  {0} = {1}  {2}".format("nyp".ljust(7),    nyp, "! Number of points in y direction" ))
    lines.append( "  {0} = {1}  {2}".format("nzp".ljust(7),    nzp, "! Number of vertical levels" ))
    lines.append( "  {0} = {1}  {2}".format("deltax".ljust(7), deltax, "! Grid spacing in x"))
    lines.append( "  {0} = {1}  {2}".format("deltay".ljust(7), deltay, "! Grid spacing in y"))
    lines.append( "  {0} = {1}  {2}".format("deltaz".ljust(7), deltaz, "! Grid spacing in the vertical"))
    lines.append( "  {0} = {1}  {2}".format("nxpart".ljust(7), nxpart, ""))
    lines.append( "  {0} = {1}  {2}".format("dzrat".ljust(7), dzrat, "! Factor for vertical grid stretching"))
    lines.append( "  {0} = {1}  {2}".format("dtlong".ljust(7), dtlong, "! Max. timestep"))
    #lines.append( "  {0} = {1}  {2}".format("distim", distim, "! Timescale for the dissipation in sponge layer")) if skip(distim) else False
    lines.append( "  {0} = {1}  {2}".format("timmax".ljust(7), timmax, ""))
    lines.append( "  {0} = {1}  {2}".format("Tspinup".ljust(7), Tspinup, ""))
    lines.append("")  
    
    lines.append( "  {0} = {1}  {2}".format("nudge_theta", nudge_theta, "! Continuous liquid water potential temperature nudging"))
    lines.append( "  {0} = {1}  {2}".format("nudge_theta_time", nudge_theta_time, ""))
    lines.append( "  {0} = {1}  {2}".format("nudge_theta_tau", nudge_theta_tau, ""))
    lines.append("")  
    
    lines.append( "  {0} = {1}  {2}".format("nudge_ccn", nudge_ccn, ""))
    lines.append( "  {0} = {1}  {2}".format("nudge_ccn_time", nudge_ccn_time, ""))
    lines.append( "  {0} = {1}  {2}".format("nudge_ccn_zmin", nudge_ccn_zmin, ""))
    lines.append( "  {0} = {1}  {2}".format("nudge_ccn_zmax", nudge_ccn_zmax, "! Set this to deltaz"))
    lines.append( "  {0} = {1}  {2}".format("nudge_ccn_tau", nudge_ccn_tau, ""))
    lines.append("")  
    
    lines.append( "  {0} = {1}  {2}".format("runtype", runtype,"! INITIAL or HISTORY (restart) run"))
    lines.append( "  {0} = {1}  {2}".format("CCN", CCN, "" ))
    lines.append( "  {0} = {1}  {2}".format("prndtl", prndtl,""))
    
    lines.append( "  {0} = {1}  {2}".format("filprf", filprf, "! Output filename profile"))
    lines.append( "  {0} = {1}  {2}".format("hfilin", hfilin,"! History filename"))
    lines.append("")  
    
    lines.append( "  {0} = {1}  {2}".format("ssam_intvl", ssam_intvl, "! Interval for statistical output"))
    lines.append( "  {0} = {1}  {2}".format("savg_intvl", savg_intvl, "! Averaging interval for stat output"))
    lines.append("")
    
    lines.append( "  {0} = {1}  {2}".format("lbinprof", lbinprof, ""))
    lines.append( "  {0} = {1}  {2}".format("frqhis", frqhis, ""))
    lines.append( "  {0} = {1}  {2}".format("frqanl", frqanl, "! Interval for full domain output"))
    
    lines.append( "  {0} = {1}  {2}".format("anl_start", anl_start, "! Save 3D outputs from the last simulation hour"))
    lines.append( "  {0} = {1}  {2}".format("istpfl", istpfl, ""))
    lines.append( "  {0} = {1}  {2}".format("corflg", corflg, "! Apply coriolis force" ))
    lines.append( "  {0} = {1}  {2}".format("itsflg", itsflg, "! Flag for temperature type in input sounding"))
    lines.append( "  {0} = {1}  {2}".format("sed_aero", sed_aero, ""))
    lines.append( "  {0} = {1}  {2}".format("sed_cloud", sed_cloud, ""))
    lines.append( "  {0} = {1}  {2}".format("sed_precp", sed_precp, ""))
    lines.append( "  {0} = {1}  {2}".format("iradtyp", iradtyp, "! Radiation/large scale forcing"))
    lines.append( "  {0} = {1}  {2}".format("case_name", case_name, "! Case name for large-scale forcing schemes"))
    lines.append( "  {0} = {1}  {2}".format("div", div, "! Large-scale divergence"))
    lines.append( "  {0} = {1}  {2}".format("strtim", strtim, "! Start time"))
    lines.append( "  {0} = {1}  {2}".format("cntlat",cntlat, "! Solar zenith angle in degrees"))
    lines.append( "  {0} = {1}  {2}".format("sfc_albedo", sfc_albedo, ""))
    lines.append( "  {0} = {1}  {2}".format("radsounding",radsounding, ""))
    lines.append( "  {0} = {1}  {2}".format("RadPrecipBins", RadPrecipBins, ""))
    lines.append( "  {0} = {1}  {2}".format("sst", sst, "! Surface temperature"))
    lines.append("")  
    
    lines.append( "  {0} = {1}  {2}".format("stat_micro", stat_micro, "! Statistics about microphysical processes"))
    lines.append( "  {0} = {1}  {2}".format("stat_micro_ts",  stat_micro_ts, ""))
    lines.append( "  {0} = {1}  {2}".format("stat_micro_ps", stat_micro_ps, ""))
    lines.append("")  
    
    lines.append( "  {0} = {1}  {2}".format("isfctyp",isfctyp, ""))
    lines.append( "  {0} = {1}  {2}".format("dthcon", dthcon, "! Sensible heat flux"))
    lines.append( "  {0} = {1}  {2}".format("drtcon", drtcon, "! Latent heat flux"))
    lines.append( "  {0} = {1}  {2}".format("ubmin", ubmin, ""))
    lines.append( "  {0} = {1}  {2}".format("zrough", zrough, "! Roughness length"))
    lines.append( "  {0} = {1}  {2}".format("th00", th00, "! Reference temperature"))
    lines.append("")
    
    lines.append( "  {0} = {1}  {2}".format("umean", umean, ""))
    lines.append( "  {0} = {1}  {2}".format("vmean", vmean, ""))
    lines.append("")
    
    
    lines.append( "  {0} = {1}  {2}".format("zrndamp", zrndamp, ""))
    lines.append( "  {0} = {1}  {2}".format("zrndampq", zrndampq, ""))
    lines.append( " /" )
    lines.append("") 
    
    lines.append( " &salsa")
    lines.append("") 
    lines.append( "  {0} = {1}  {2}".format("nlcoag".ljust(12), nlcoag, "! Master coagulation switch"))
    lines.append( "  {0} = {1}  {2}".format("nlcgaa".ljust(12), nlcgaa, "! Aerosol coagulation"))
    lines.append("")
    lines.append( "  {0} = {1}  {2}".format("nlcnd".ljust(12), nlcnd, "! Master condensation switch"))
    lines.append( "  {0} = {1}  {2}".format("nlcndgas".ljust(12), nlcndgas, "! --Aerosol precursor gas codensation"))
    lines.append( "  {0} = {1}  {2}".format("nlcndh2oae".ljust(12), nlcndh2oae, "! --Condensation of water on aerosols (if FALSE, equilibrium assumed)"))
    lines.append( "  {0} = {1}  {2}".format("nlcndh2ocl".ljust(12), nlcndh2ocl, "! --Condensation of water on cloud droplets (and drizzle)"))
    lines.append( "  {0} = {1}  {2}".format("nlauto".ljust(12), nlauto, "! Master autoconversion switch"))
    lines.append("")   
    
    lines.append( "  {0} = {1}  {2}".format("nlactiv".ljust(12), nlactiv, "! Master cloud activation switch"))
    lines.append( "  {0} = {1}  {2}".format("nlactbase".ljust(12), nlactbase, "! --Switch for parameterized cloud base activation"))
    lines.append( "  {0} = {1}  {2}".format("nlactintst".ljust(12), nlactintst, "! --Switch for interstitial activation based on host model Smax"))
    lines.append("")   
    
    
    lines.append( "  {0} = {1}  {2}".format("rhlim",rhlim, "! RH limit for SALSA during initialization and spinup"))
    lines.append("")   
    
    lines.append( "  {0} = {1}  {2}".format("nspec",nspec, ""))
    lines.append( "  {0} = {1}  {2}".format("listspec", listspec, ""))
    lines.append( "  {0} = {1}  {2}".format("volDistA", volDistA,""))
    lines.append( "  {0} = {1}  {2}".format("volDistB", volDistB,""))
    lines.append( "  {0} = {1}  {2}".format("nf2a", nf2a, ""))
    if skip(rainbinlim): lines.append( "  {0} = {1}  {2}".format("rainbinlim(1:21)", rainbinlim, ""))
    if skip(ira_stat):   lines.append( "  {0} = {1}  {2}".format("ira_stat", ira_stat, ""))
    lines.append("")
    
    lines.append( "  {0} = {1}  {2}".format("sigmag".ljust(7), sigmag, "! Stdev for initial aerosol size distribution for isdtyp == 0 (uniform)  "))
    lines.append( "  {0} = {1}  {2}".format("dpg".ljust(7), dpg, "! Mode mean diameters in micrometers"))
    lines.append( "  {0} = {1}  {2}".format("n".ljust(7), nconc, "! Mode number concentrations in #/mg"))
    lines.append( " /" )
    
    
    f = open(filu,'w')
    
    for ll in lines:
        f.write(ll)
        f.write("\n")
    f.close()
                
if __name__ == "__main__":
   write_namelist(sys.argv[1:], filu=os.environ["HOME"]+"NAMELIST")