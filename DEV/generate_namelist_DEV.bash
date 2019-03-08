#!/bin/bash

# Exit on error
set -e


##########################
###                    ###
### write the namelist ###
###                    ###
##########################

########### version
command -v git 2>&1 >/dev/null
if [ $? -eq 0 ]; then
    ver=`git describe --tags 2>&1`
    if [ $? -ne 0 ]; then
        echo "Ignore possible error, git just doesn't find a version tag - using default value"
        ver=vx.x.x
    fi
else
    ver=latest
fi
########### end version

cat > ${dir}/NAMELIST <<EOF
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!! DESIGN VERSION ${design}
!!! design variables case ${case}
!!! q_inv    == ${q_inv}     [g/kg]
!!! tpot_inv == ${tpot_inv}    [K]
!!! clw_max  == ${clw_max}    [g/kg]
!!! tpot_pbl == ${tpot_pbl}  [K]
!!! pblh     == ${pblh} [m]
!!! num_pbl  == ${num_pbl}   [#/mg]
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

 &version
  ver="${ver}"
 /

 &model
  level = ${level:-3}
  nxp =   ${nxp:-204} ! Number of points in x direction
  nyp =   ${nyp:-204} ! Number of points in y direction
  nzp =   ${nzp:-200} ! Number of vertical levels
  deltax = ${deltax:-50.} ! Grid spacing in x
  deltay = ${deltay:-50.} ! Grid spacing in y
  deltaz = ${deltaz:-20.} ! Grid spacing in the vertical
  nxpart = ${nxpart:-.true.}
  dzmax  = ${dzmax:-3500.} ! Height above which start stretching vertical grid
  dzrat  = ${dzrat:-1.0}   ! Factor for vertical grid stretching
  dtlong = ${dtlong:-2.}   ! Max. timestep
  distim = ${distim:-100.} ! Timescale for the dissipation in sponge layer
  timmax = ${timmax:-12600.}
  runtype = ${runtype:-'"INITIAL"'} ! INITIAL or HISTORY (restart) run
  CCN = ${CCN:-600.e6}
  corflg = ${corflg:-.false.} ! Apply coriolis force
  prndtl = ${prndtl:--0.3333333}
  
  filprf = ${filprf:-"'emul'"} ! Output filename profile
  hfilin = ${hfilin:-"'emul.rst'"}
  
  ssam_intvl = ${ssam_intvl:-300.} ! Interval for statistical output
  savg_intvl = ${savg_intvl:-300.} ! Averaging interval for stat output

  frqanl = ${frqanl:-5400.}  ! Interval for full domain output
  frqhis  = ${frqhis:-30000.}
  lbinanl = ${lbinanl:-.false.} ! Write binned microphysical output (with level >= 4)
  
  salsa_b_bins = ${salsa_b_bins:-.FALSE.} ! ?
  mcflg = ${mcflg:-.FALSE.} ! Do mass conservation statistics

  sed_aero%switch = ${sed_aero:-.FALSE.}          ! Calculate sedimentation of aerosol particles
  sed_cloud%switch = ${sed_cloud:-.TRUE.}          ! - '' - cloud droplets
  sed_cloud%delay = ${Tspinup:-5400.}
  sed_precp%switch = ${sed_precp:-.TRUE.}          ! precipitation
  sed_precp%delay = ${Tspinup:-5400.}  
  sed_ice%switch = ${sed_ice:-.FALSE.}            ! ice particles
  sed_snow%switch = ${sed_snow:-.FALSE.}           ! snow flakes/precipitating ice
  bulk_autoc%switch = .TRUE.
  bulk_autoc%delay = ${Tspinup:-5400.}      ! Autoconversion switch for level = 1-3  
  
  itsflg = ${itsflg:-1} ! Flag for temperature type in input sounding
  
  lnudging = ${lnudging:-.TRUE.} ! Master switch for nudging scheme
  lemission = ${lemission:-.FALSE.}          ! Master switch for aerosol emissions   
  iradtyp = ${iradtyp:-3}                ! Radiation/large scale forcing
  strtim = ${strtim:-180.5}              ! Start time
  cntlat = ${cntlat:-60.}                 ! latitude
  case_name = ${case_name:-"'default'"}  ! Case name for large-scale forcing schemes
  div = ${div:-1.5e-6}                   ! Large-scale divergence
  dthcon = ${dthcon:-0.} ! heat flux 18.4613 ! Sensible heat flux
  drtcon = ${drtcon:-0.}  ! latent 84.8921   ! Latent heat flux
!  isfctyp = ${isfctyp:-2}
  sst = ${sst:-271.35}  ! Surface temperature
  zrough = ${zrough:-0.01} ! Roughness length
  ubmin  = ${ubmin:--0.25}
  th00 = ${th00:-289.} ! Reference temperature
  umean =  ${umean:-10.}
  vmean = ${vmean:-0.}

 /
 ! With iradtyp = 3
 &radiation
 
   radsounding = ${radsounding:-"'datafiles/kmls.lay'"} 
   RadPrecipBins = ${RadPrecipBins:-1}
   sfc_albedo = ${sfc_albedo:-0.05}
   zenithFlag = ${zenithFlag:-.TRUE.}
 /
 

 ! With lnudging = .TRUE.
 &nudge

  nudge_time = ${nudge_time:-12600.}           ! Overall time for nudging from the start of the simulation

  ndg_theta%nudgetype = 1
  ndg_theta%tau_type = 2      ! Type of relaxation time (0:constant, 1-3: increasing)
  ndg_theta%tau_min = 300.    ! Min relaxation time (with tau_type=1-3 and constant tau)
  ndg_theta%tau_max = 3600.   ! Max relaxation time (with tau_type=1-3)
  ndg_theta%tau_max_continue = .FALSE.

 /
 
 &salsa	
 
   lscoag%switch  = ${lscoag:-.TRUE.}       ! Master coagulation switch
   lscoag%delay   = ${Tspinup:-5400.}
   
   lscnd%switch   = ${lscnd:-.TRUE.}  ! Master condensation switch
   
   lsauto%switch  = ${lsauto:-.TRUE.}  ! Master autoconversion switch
   lsauto%delay   = ${Tspinup:-5400.}
   
   lsactiv%switch = ${lsactiv:-.TRUE.}  ! Master cloud activation switch
   
   lsicenucl%switch = ${lsicenucl:-.FALSE.}   ! Switch for ice nucleation
   lsicenucl%delay  = ${Tspinup:-5400.}
   
   lsautosnow%switch  = ${lsautosnow:-.FALSE.} ! Master snow autoconversion switch
   
   lsicemelt%switch    = ${lsicemelt:-.FALSE.}    ! Switch for ice'n' snow melting

   
   lscgcc = ${lscgcc:-.TRUE.}       ! Self-collection of cloud droplets
   lscgpp = ${lscgpp:-.TRUE.}       ! Self-collection of rain drops
   lscgpc = ${lscgpc:-.TRUE.}       ! Rain collection of cloud droplets
   lscgaa = ${lscgaa:-.FALSE.}      ! Aerosol coagulation
   lscgca = ${lscgca:-.TRUE.}       ! Cloud collection of aerosols
   lscgpa = ${lscgpa:-.TRUE.}       ! Rain collection of aerosols
   lscgia = ${lscgia:-.TRUE.}       ! Ice collection of aerosols
   lscgic = ${lscgic:-.TRUE.}       ! Ice collection of cloud droplets
   lscgii = ${lscgii:-.TRUE.}       ! Self-collection of ice
   lscgip = ${lscgip:-.TRUE.}       ! Ice collection of rain drops
   lscgsa = ${lscgsa:-.TRUE.}       ! Snow collection of aerosols
   lscgsc = ${lscgsc:-.TRUE.}       ! Snow collection of cloud droplets
   lscgsi = ${lscgsi:-.TRUE.}       ! Snow collection of ice particles
   lscgsp = ${lscgsp:-.TRUE.}       ! Snow collection of rain drops
   lscgss = ${lscgss:-.TRUE.}       ! Self-collection of snow

   
   lscndgas    = ${lscndgas:-.FALSE.}  ! --Aerosol precursor gas codensation
   lscndh2oae  = ${lscndh2oae:-.TRUE.}  ! --Condensation of water on aerosols (if FALSE, equilibrium assumed)
   lscndh2ocl  = ${lscndh2ocl:-.TRUE.}  ! --Condensation of water on cloud droplets (and drizzle)
   lscndh2oic  = ${lscndh2oic:-.TRUE.}  ! --Condensation of water on ice particles
   
   lsactbase   = ${lsactbase:-.FALSE.}  ! --Switch for parameterized cloud base activation
   lsactintst  = ${lsactintst:-.TRUE.}  ! --Switch for interstitial activation based on host model Smax

   lscheckarrays = ${lscheckarray:-.FALSE.}
   
   lsfreeRH%switch = .TRUE.
   lsfreeRH%delay = ${Tspinup:-5400.}
   rhlim = ${rhlim:-1.001}          ! RH limit for SALSA during initialization and spinup

   isdtyp = ${isdtyp:-0}
   nspec = ${nspec:-1}
   listspec = ${listspec:-"'SO4','','','','','',''"}            !!!! "'SO4','DU','OC','','','',''"
   volDistA = ${volDistA:-1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0}   
   volDistB = ${volDistB:-0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0}
   nf2a = ${nf2a:-1.0}

   sigmag = ${sigmag:-1.3, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0}  ! Stdev for initial aerosol size distribution for isdtyp == 0 (uniform)  
   dpg    = ${dpg:-0.1, 1.0, 0.2, 0.2, 0.2, 0.2, 0.2}     ! Mode mean diameters in micrometers
   n      = ${n:-46.2502241367474, 0. , 0., 0., 0., 0., 0.}  ! Mode number concentrations in #/mg
 /

EOF
 
exit
