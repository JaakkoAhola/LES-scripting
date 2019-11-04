
# listaa plottaa kuvei:n avulla vain valmiit tapaukset
a="";for i in $(${SCRIPT}/check_emulaattorisetin_status.bash /lustre/tmp/aholaj/UCLALES-SALSA/case_emulator_DESIGN_v3.3.1_LES_ECLAIR_Jaakko.ECLAIRv2.0.cray.fast_LVL4 | grep VALMIS | cut -c1-7 ); do a="$a ${i}/${i}"; done; echo $a