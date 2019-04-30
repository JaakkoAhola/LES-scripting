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

loopFolders=${loopFolders:-case_isdac}
function looppaatarkastapoista {

    for i in $(ls -d  ${loopFolders}* )
    do

        echo $i
        jatkokasittelesimulaatio $i
        echo " "
        echo  " "
    done

}


cd ${LUSTRE}
while [[ ! -z $( qstat -u $USER  ) ]]    # | grep -e "nc_" -e "ps_" -e "ts_"
do
    looppaatarkastapoista
    echo " "
    echo " "
    echo "ODOTETAAN ennen seuraavaa loop-kierrosta"
    sleep 15s
done
sleep 3600s

looppaatarkastapoista
