#!/bin/bash

# Exit on error
set -e
# echo eka $1 toka $2 kolmas $3 neljas $4

# import subroutines & variables 
if [[ -d ${SCRIPT} ]]; then
   scriptref=${SCRIPT}
else
   scriptref=.
fi
source ${scriptref}/subroutines_variables.bash


function looppaatarkastapoista {

    for i in $(ls -d  case_isdac* )
    do
        simulation=$i
        
        status=$( tarkistastatus $simulation)
        
        echo -ne $simulation $status " "
        if [[ $status == '11' ]]
        then
            aika=$(date +%s)
            
            viimeks=$(find ${simulation}/ -printf "%T@\n" | sort | tail -1)
            #viimeks=$(find ${simulation}/ -type f -exec stat \{} --printf='%(%s)T\n' \; | sort -n -r | head -n 1)
            viimeksInt=$(python -c "print(str($viimeks).split('.')[0])")
            ika=$(( aika-viimeksInt ))
            if [[ $ika -gt 1200 ]];
            then
            
                echo -ne $ika "VALMIS, poistetaan"
                poistaturhat $simulation $outputname $folderROOT
            fi
        
        fi
        
        echo " "

        
    done

}


cd ${LUSTRE}
while [[ ! -z $( qstat -u $USER | grep -e "nc_" -e "ps_" -e "ts_" ) ]]    
do
    looppaatarkastapoista
    sleep 15s
done
sleep 1210s

looppaatarkastapoista
