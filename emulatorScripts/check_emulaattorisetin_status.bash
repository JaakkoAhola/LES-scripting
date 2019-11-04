#!/bin/bash

# Exit on error
set -e
#shopt -s extglob
# import subroutines & variables 
if [[ -d ${SCRIPT} ]]; then
   scriptref=${SCRIPT}
else
   scriptref=.
fi
source ${scriptref}/subroutines_variables.bash
#######################

# input variables
#
# $1 = absolute path of emulator
# list= "list of simulations, generated if not given"

emulatorname=$(basename $1)
folderROOT=$(dirname $1)



#######################
A=${A:-1}
B=${B:-90}

echo " "
etunolla=3 # huomhuom
if [[ -z $list ]]
then
    list=$( for i in $(ls -d ${1}/emul*/); do python -c "print('$i'.split('/')[-2][4:])"; done) #| tail -c 4 | tr "/" " " | tr "\n" " "
    #array=($(seq -f"%0${etunolla}g" $A $B  ))
fi
u=0
for kk in ${list[@]}
do
    array[u]=$(printf %0${etunolla}d $(( 10#$kk )))
    u=$((u+1))
done    

    
for i in ${array[@]}
do

    echo ' '
	echo ' '
    	status=$( tarkistastatus ${emulatorname}/emul${i} emul${i}  $folderROOT)

    	echo "statuksen tarkistus" emul${i} $status
    	LS=${status:0:1}
    	PPS=${status:1:2}
    	
    	if [[ $status == '11' ]]
    	then
        	echo emul${i} "on VALMIS"
        	statusValmiit=$((statusValmiit+1))
    	elif [ $LS -eq 1 ] && [ $PPS -ne 1 ]; then
            statusVainLESValmis=$((statusVainLESValmis+1))
    	elif [ $LS -ne 1 ] && [ $PPS -ne 1 ]; then
            statusKesken=$((statusKesken+1))
    	fi
    
    
done

echo 'valmiit' $statusValmiit
echo 'vain les valmis' $statusVainLESValmis
echo 'kesken' $statusKesken
echo 'tarkistussumma kaikki' $((statusValmiit+statusVainLESValmis+statusKesken))
echo ' '
echo ' '
########################################
