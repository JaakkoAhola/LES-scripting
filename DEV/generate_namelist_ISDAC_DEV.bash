#!/bin/bash

# Exit on error
set -e


##########################
###                    ###
### write the namelist ###
###                    ###
##########################

cat > ${dir}/NAMELIST <<EOF
 &version
  ver="${ver}"
 /

 &model
  nxp =   ${nxp:-68}
  nyp =   ${nyp:-68}
  nzp =   ${nzp:-140}
  deltax = ${deltax:-50.}
  deltay = ${deltay:-50.}
  deltaz = ${deltaz:-10.}
  nxpart = ${nxpart:-.false.}
  dzmax  = ${dzmax:-1200.}
  dzrat  = ${dzrat:-1.05}
  dtlong = ${dtlong:-1.}
  distim = ${distim:-100.}
  timmax = ${timmax:-28800.}
  Tspinup = ${Tspinup:-7200.}

${jaakkoNL}  minispinup01 = ${minispinup01:-0.}
${jaakkoNL}  minispinup02 = ${minispinup02:-0.}
${jaakkoNL}  minispinupCase01 = ${minispinupCase01:-3}
${jaakkoNL}  minispinupCase02 = ${minispinupCase02:-3}

  lnudging = ${lnudging:-.TRUE.}
  lemission = ${lemission:-.FALSE.}

  runtype = ${runtype:-'"INITIAL"'}
  level = ${level:-5}
  CCN = ${CCN:-30.e6}
  prndtl = ${prndtl:--0.3333333}
  filprf = ${filprf:-"'isdac'"}
  hfilin = ${hfilin:-"'isdac.rst'"}
  ssam_intvl = ${ssam_intvl:-120.}
  savg_intvl = ${savg_intvl:-120.}
  frqhis  = ${frqhis:-1800.}
  istpfl  = ${istpfl:-1}
  lbinanl = ${lbinanl:-.true.}
  frqanl = ${frqanl:-120.}
  corflg = ${corflg:-.false.}
  ipsflg = ${ipsflg:-1}
  itsflg = ${itsflg:-1}
  sed_aero = ${sed_aero:-.FALSE.}
  sed_cloud = ${sed_cloud:-.TRUE.}
  sed_precp = ${sed_precp:-.FALSE.}
  sed_ice = ${sed_ice:-.TRUE.}
  sed_snow = ${sed_snow:-.FALSE.}
  iradtyp = ${iradtyp:-5}                ! 1 = no radiation, only large-scale forcing, 3 = radiation + large-scale forcing 5
  case_name = ${case_name:-"'isdac'"}            ! Case-specific large-scale forcing: none = not used, 
                                      ! default = simple divergence forcing with specified div

  cntlat = ${cntlat:-71.32}
  strtim = ${strtim:-117.75}
  

  isfctyp = ${isfctyp:-0} ! surface fluxes
  sst = ${sst:-267.}

  dthcon = ${dthcon:-0.} ! heat flux
  drtcon = ${drtcon:-0.}  ! latent

  ubmin  = ${ubmin:-0.25}
  zrough = ${zrough:-4.E-4}
  th00 = ${th00:-263.}
  umean =  ${umean:--7.0}
  vmean = ${vmean:-0.}
  
  zrand = ${zrand:-825.}
  zrndamp = ${zrndamp:-0.1} ! the amplitude of pseudorandom fluctuations
 /

 ! With lnudging = .TRUE.
 &nudge
  
  nudge_time = ${nudge_time:-28800.}          ! Overall time for nudging from the start of the simulation

  ndg_theta%nudgetype = ${nudge_theta:-3}
  ndg_theta%tau_type  = ${tau_theta:-1.}      ! Type of relaxation time (0:constant, 1-3: increasing)
  
  ndg_rv%nudgetype = ${nudge_rv:-3}
  ndg_rv%tau_type = ${tau_rv:-1.}
  
  ndg_u%nudgetype = ${nudge_u:-3}
  ndg_u%tau_type = ${tau_u:-2.}
  
  ndg_v%nudgetype = ${nudge_v:-3}
  ndg_v%tau_type = ${tau_v:-2.}

  
  !ndg_theta%tau_min = 300.    ! Min relaxation time (with tau_type=1-3 and constant tau)
  !ndg_theta%tau_max = 900.   ! Max relaxation time (with tau_type=1-3)
  !ndg_theta%tau_max_continue = .TRUE.

 /

 &radiation
 
   RadPrecipBins = ${RadPrecipBins:-1}
 
 /
 
 &salsa	
   lscoag%switch  = ${lscoag:-.FALSE.}       ! Master coagulation switch
   lscoag%delay   = ${Tspinup}
   
   lscnd%switch   = ${lscnd:-.TRUE.}  ! Master condensation switch
   
   lsauto%switch  = ${lsauto:-.FALSE.}  ! Master autoconversion switch
   lsauto%delay   = ${Tspinup}
   
   lsactiv%switch = ${lsactiv:-.TRUE.}  ! Master cloud activation switch
   
   lsicenucl%switch = ${lsicenucl:-.TRUE.}   ! Switch for ice nucleation
   lsicenucl%delay  = ${Tspinup}
   
   lsautosnow%switch  = ${lsautosnow:-.FALSE.} ! Master snow autoconversion switch
   
   lsicemelt%switch    = ${lsicemelt:-.FALSE.}    ! Switch for ice'n' snow melting
   
   lscndgas    = ${lscndgas:-.FALSE.}  ! --Aerosol precursor gas codensation
   lscndh2oae  = ${lscndh2oae:-.TRUE.}  ! --Condensation of water on aerosols (if FALSE, equilibrium assumed)
   lscndh2ocl  = ${lscndh2ocl:-.TRUE.}  ! --Condensation of water on cloud droplets (and drizzle)
   lscndh2oic  = ${lscndh2oic:-.TRUE.}  ! --Condensation of water on ice particles
   
   lsactbase   = ${lsactbase:-.FALSE.}  ! --Switch for parameterized cloud base activation
   lsactintst  = ${lsactintst:-.TRUE.}  ! --Switch for interstitial activation based on host model Smax

   lscheckarrays = ${lscheckarray:-.TRUE.}
   
   
   fixINC      = ${fixINC:-1.0}         ! fixed ice number concentration #/L, lsfixinc should be set to true inorder to have this working

   rhlim       = ${rhlim:-1.2}          ! RH limit for SALSA during initialization and spinup

   isdtyp   = ${isdtyp:-0}
   nspec    = ${nspec:-1}
   listspec = ${listspec:-"'SO4','','','','','',''"}
   volDistA = ${volDistA:-1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0}   
   volDistB = ${volDistB:-0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0}
   nf2a     = ${nf2a:-1.0}

   sigmag = ${sigmag:- 1.5,    2.45, 2.0, 2.0, 2.0, 2.0, 2.0}  ! Stdev for initial aerosol size distribution for isdtyp == 0 (uniform)  
   dpg    = ${dpg:-    0.2,     0.7, 0.2, 0.2, 0.2, 0.2, 0.2}     ! Mode mean diameters in micrometers
   n      = ${n:-   155.24,    6.37,  0.,  0.,  0.,  0.,  0.}  ! Mode number concentrations in #/mg
 /

EOF
 
exit
