#!/bin/bash

# Exit on error
set -e
shopt -s extglob
# import subroutines & variables 
if [[ -d ${SCRIPT} ]]; then
   scriptref=${SCRIPT}
else
   scriptref=.
fi
source ${scriptref}/subroutines_variables.bash

#
#
# EXAMPLE USAGE
# A=28 B=30 exe=les.mpi.v1.0.4 designV=v1.5.1 postfix=geggals ./submit_emulator_runs_parallel.bash 3
# where A is the case number that you want to start from
#       B is the case number that you want to end up
#       exe is the name of the LES executable (les.mpi)
#       designV is the design version
#    $1 = 3 is the number of how many runs you dare to submit at the same time
#    $2 = scriptname
#    $3 = job flag of the job scheduling system (OPTIONAL) default value: PBS
#
# if you want to run specific cases given them as list="01 02 09 25 63 82"


# essential input values
submit=${submit:-true}
restart=${restart:-false}

if [[ -z $designV ]]; then
    "You didn't give the version of design"
fi

designfilu=${designV:0:6}
curdir=${PWD}

if [ -z "$B" ] && [ -z "$list" ]; then # generate list of cases automatically
    automatic="true"
    
    echo "generate list of cases automatically"
else
    automatic="false"
fi


if [[ $automatic == "true" ]]; then
    cd ${IBRIX}/DESIGN
    tag=$(git describe --tags | tr -dc '[:alnum:].')

    if [[  ${tag} == ${designfilu} ]]; then
        echo "You are using proper git branch"
    else
        echo "Checkout to the same git branch as the training set should be"
        exit 1
    fi
    
    source activate py36
    
    DESIGNnetcdffile=${IBRIX}/DESIGNnetcdf/${designfilu}/design_${designfilu}.nc
    B=$(python -c "from netCDF4 import Dataset; ff='$DESIGNnetcdffile'; nc = Dataset(ff, 'r'); print(nc.dimensions['case'].size)")

fi

if [[ -z $A ]]
then
    A=1
fi

##apuetunolla=$( python -c "print max( ${#A}, ${#B} )" )

##if [[ -z $etunolla ]]
##then
##    etunolla=$apuetunolla
##fi
##echo "etunolla" $etunolla

etunolla=3 # huomhuom
if [[ -z $list ]]
then
    array=($(seq -f"%0${etunolla}g" $A $B  ))
else
    u=0
    for kk in ${list[@]}
    do
        array[u]=$(printf %0${etunolla}d ${kk##+(0)})
        u=$((u+1))
    done
fi
echo "submit array" ${array[@]}
k=0

exe=${exe:-les.mpi}
# supercomputer related variable settings
nproc=${nproc:-100}


bashfolder="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [[ -n $postfix ]]; then
    echo "postfix annettu" $postfix
    postfix=_${postfix}
fi



# LES version
nn=$(( ${#exe}- 8 ))
if [[ $nn -gt 0 ]]; then
    les=_${exe:$((${#exe}-$nn)):$nn}
fi

emulatorinput=case_emulator_DESIGN_${designV}
inputrootfolder=${bin}/${emulatorinput}


LVL=$(grep "level " ${inputrootfolder}/emul???/NAMELIST | head -1)
LVL=$( python -c "print('${LVL}'.split('=')[1].replace(' ', ''))")
echo "LVL" $LVL
echo 'keissien lkm' ${#array[@]}
if [[ $LVL -ge 4 ]]; then
    WT=${WTMAX} # walltime
else
    WT=48:00:00
    if [[ ${#array[@]} -gt 100 ]]; then
	WT=${WTMAX}
    fi
fi

emulatorname=${emulatorinput}_LES${les}_LVL${LVL}${postfix}

emulatoroutputroot=${outputroot}/${emulatorname}


if [[ $restart == 'false' ]]; then
    echo 'poista vanhat kansiot' $folder
    rm -rf  ${emulatoroutputroot} 
fi

if [[ ! -d ${emulatoroutputroot} ]]; then
    restart='false'
    echo ' ' 
    echo  "if emulatoroutputroot folder doesn't exist then restart value is always false"
    echo "restart -> $restart"
fi

if [[ -z $1 ]]; then
  echo "You didn't give the number of simultaneous submits of emulator runs  (= number of THREADS)"
  exit 1
fi
ThreadNro=$1


if [[ -n $2 ]]; then
  scriptname=$2
fi
echo "scriptname" ${scriptname}

if [[ -n $3 ]]; then
  jobflag=$3
fi
echo "job scheduling system" $jobflag


mkdir -p ${emulatoroutputroot}
echo 'LOG emulator begin' >> ${emulatoroutputroot}/log
echo -n "LOG " >> ${emulatoroutputroot}/log; date '+%T %d-%m-%Y'   >> ${emulatoroutputroot}/log
date '+%s'            >> ${emulatoroutputroot}/log
echo ' '              >> ${emulatoroutputroot}/log
##########################################
###                                    ###
### copy all necessary files to lustre ###
###                                    ###
##########################################

cp ${SCRIPT}/subroutines_variables.bash ${emulatoroutputroot}/
cp ${SCRIPT}/emulator_runs_parallel.bash ${emulatoroutputroot}/
cp ${SCRIPT}/submit_uclales-salsa.bash   ${emulatoroutputroot}/
cp ${SCRIPT}/submit_postpros.bash        ${emulatoroutputroot}/
cp ${SCRIPT}/nodestats.py                ${emulatoroutputroot}/
cp ${SCRIPT}/emulator_inputs.py          ${emulatoroutputroot}/
cp ${SCRIPT}/generate_namelist.py        ${emulatoroutputroot}/
cp ${SCRIPT}/ECLAIR_calcs.py             ${emulatoroutputroot}/
cp ${SCRIPT}/FindCloudBase.py            ${emulatoroutputroot}/

cp ${SCRIPT}/${scriptname}               ${emulatoroutputroot}/

cp ${IBRIX}/DESIGN/design.csv            ${emulatoroutputroot}/

if [[ $automatic == "true" ]]; then
    cp $DESIGNnetcdffile                     ${emulatoroutputroot}/
fi


statusValmiit=0
statusVainLESValmis=0
statusKesken=0


for i in ${array[@]}
do

    if [[ $restart == 'true' ]]; then
	echo ' '
	echo ' '
    	status=$( tarkistastatus ${emulatorname}/emul${i} emul${i} )

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

 

        echo emul${i} "poistetaan turhat statuksen mukaan"
        poistaturhat ${emulatorname}/emul${i} emul${i}
    else
	echo ' '
        echo 'uudelta pohjalta'
	echo "kopioidaan input tiedostot emul${i}"
    	mkdir -p ${emulatoroutputroot}/emul${i}/datafiles
        cp ${inputrootfolder}/emul${i}/* ${emulatoroutputroot}/emul${i}/
        cp ${bin}/${exe} ${emulatoroutputroot}/emul${i}/
        cp ${bin}/datafiles/* ${emulatoroutputroot}/emul${i}/datafiles
        
    fi
    
    
done

echo 'valmiit' $statusValmiit
echo 'vain les valmis' $statusVainLESValmis
echo 'kesken' $statusKesken
echo 'tarkistussumma kaikki' $((statusValmiit+statusVainLESValmis+statusKesken))
echo ' '
echo ' '
########################################


if [ $jobflag == 'PBS' ] ; then

cat > ${emulatoroutputroot}/control_multiple_emulator_run.sh <<FINALPBS
#!/bin/sh
#PBS -N EMULATOR
#PBS -l mppwidth=1
#PBS -l mppnppn=1
#PBS -l mppdepth=${nodeNPU}
#PBS -l walltime=${WT}
#PBS -j oe
#PBS -M ${email}
#PBS -m ae

cd ${emulatoroutputroot}

source /etc/profile
export PATH="${LUSTRE}/anaconda2/bin:$PATH"
python ${emulatoroutputroot}/nodestats.py ${emulatoroutputroot}/ False &

FINALPBS

elif [ $jobflag == 'SBATCH' ] ; then

cp ${SCRIPT}/taito_env_uclales-salsa.bash            ${emulatoroutputroot}/

cat > ${emulatoroutputroot}/control_multiple_emulator_run.sh <<FINALSBATCH
#!/bin/sh
#SBATCH -J EMULATOR
#SBATCH -n 1
#SBATCH -t 336:00:00 # longrun limit = 14 days
#SBATCH --output=emulator_${1}-%j.out
#SBATCH --error=emulator_${1}-%j.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=${email}
#SBATCH -p longrun

cd ${emulatoroutputroot}

export PATH="${USERAPPL}/miniconda2/bin:$PATH"
#python ${emulatoroutputroot}/nodestats.py ${emulatoroutputroot}/ False &

FINALSBATCH

fi

# echo ' '
aloitusindeksi=0
nroJobs=0
for n in $( seq 0 $((ThreadNro-1)) )
do
nroJobs=$(python -c "from math import ceil; print(int( ceil( ( ${#array[@]}-$aloitusindeksi  )/float( $ThreadNro-$n ) ) ))")
echo "submit->parallel" ${array[@]:$aloitusindeksi:$nroJobs}
echo "emulatorname=${emulatorname} list='"${array[@]:$aloitusindeksi:$nroJobs}"' threadNro=$n nproc=${nproc} jobflag=$jobflag exe=${exe} etunolla=$etunolla  scriptname=$scriptname ${emulatoroutputroot}/emulator_runs_parallel.bash | tee ${emulatoroutputroot}/emulatoroutput$(printf %0${etunolla}d ${n##+(0)}) &" >> ${emulatoroutputroot}/control_multiple_emulator_run.sh
aloitusindeksi=$((aloitusindeksi+nroJobs))
done

cat >> ${emulatoroutputroot}/control_multiple_emulator_run.sh <<EOF
wait
printf "Training simulations are ready in ${emulatoroutputroot} \n\n -Jaakko- \n\n PS This was an automated message" | mail -s "EMULATOR ready $emulatorname" Jaakko.Ahola@fmi.fi -r jaakko.ahola@fmi.fi
exit

EOF

cd ${emulatoroutputroot}

# Make initial submit
chmod +x  control_multiple_emulator_run.sh

if [ $submit == 'true' ]; then

    echo 'Submit emulator controller to job scheduler'
    ${submitCMD} ${emulatoroutputroot}/control_multiple_emulator_run.sh

else
    echo "NOT submitting"
fi

exit
