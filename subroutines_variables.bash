#!/bin/bash

# user parameters

# folders
export model=UCLALES-SALSA



export email='jaakko.ahola@fmi.fi'

export scriptname=combine.py

export ibrixrootfolder=/ibrix/arch/ClimRes/${USER}/
export eclairrootfolder=/arch/eclair/UCLALES-SALSA_training_simulations/
# subroutines

if [[ $jobflag == 'PBS' ]]; then
    export outputroot=/lustre/tmp/${USER}/${model}/
    export nodeNPU=28  # number of processing units in a node
    export submitCMD=qsub
    export PATH="${WRKDIR}/anaconda2/bin:$PATH"
    export WTMAX=24:00:00

elif [[ $jobflag == 'SBATCH' ]]; then ## CSC's Sisu machine values
    export outputroot=${WRKDIR}/${model}
    export nodeNPU=24 # number of processing units in a node
    export submitCMD=sbatch
    export WTMAX=72:00:00 #maximum value of wall time for small_long
    export outputPostfix=.out
    export PATH="${HOME}/miniconda3/bin:$PATH"
fi

export salsa=${LES}/src/src_salsa
export les=${LES}/src/src_LES
export bin=${LES}/bin


function odota {

    outputname=$1
    aika=$2
    aika=${aika:-30s}
    tulosta=${tulosta:-false}
    echo ' '
    echo 'Nyt odotetaan' $outputname $aika
    while [[ ! -z $( qstat -u $USER | grep $outputname ) ]]
    do
        if [[ $tulosta == 'true' ]]; then
            date +%Y-%m-%d-%H-%M
            qstat -u $USER | grep $outputname
        fi
        sleep $aika
    done

}

function kopioibrixille {

    echo ' '
    echo 'Kopioidaan ibrixille'
    simulation=$1
    outputname=$2

    # if outputname doesn't exist set it to be same as simulation
    if [[ -z $outputname ]]; then
        outputname=${simulation}
    fi

    mkdir -p ${ibrixrootfolder}/${outputname}/
    rsync -avz  ${outputroot}/${simulation}/ ${ibrixrootfolder}/${outputname}/ #--ignore-existing
    echo ' '

}

function kopioeclairille {

    echo ' '
    echo 'Kopioidaan eclairille'
    simulation=$1
    outputname=$2

    # if outputname doesn't exist set it to be same as simulation
    if [[ -z $outputname ]]; then
        outputname=${simulation}
    fi

    mkdir -p ${eclairrootfolder}/${outputname}/
    rsync -avz  $extra ${outputroot}/${simulation}/ ${eclairrootfolder}/${outputname}/ #--ignore-existing
    echo ' '

}

function copyToFolder {
    for item in ${list[@]}
    do
        echo $item
        cp ${originfolder}/${item} ${destfolder}/
    done
}

function postprosessoi {

    echo ' '
    simulation=$1
    outputname=$2
    jobnamepostfix=$3

    ncsub=${ncsub:-true}
    pssub=${pssub:-true}
    tssub=${tssub:-true}


    # if outputname doesn't exist set it to be same as simulation
    if [[ -z $outputname ]]; then
        outputname=${simulation}
    fi

    # if scriptfolder doesn't exist set it to be the default
    if [[ -z $scriptfolder ]]; then
        scriptfolder=${SCRIPT}
    fi

    # if jobnamepostfix doesn't exist set it to be the default
    if [[ -z $jobnamepostfix ]]; then
        jobnamepostfix=${outputname}
    fi

    if [[ $ncsub == "true" ]]; then
        echo ' '
        echo 'Nyt postprosessoidaan nc'
        # WT as walltime e.g. 01:00:00 hours
        WT=$WT ${scriptfolder}/submit_postpros.bash ${outputroot}/${simulation}/${outputname}    $scriptname $jobflag $jobnamepostfix
    fi

    if [[ $pssub == "true" ]]; then
        echo ' '
        echo 'Nyt postprosessoidaan ps'
        # WT as walltime e.g. 01:00:00 hours
        WT=$WT ${scriptfolder}/submit_postpros.bash ${outputroot}/${simulation}/${outputname}.ps $scriptname $jobflag $jobnamepostfix
    fi

    if [[ $tssub == "true" ]]; then
        echo ' '
        echo 'Nyt postprosessoidaan ts'
        # WT as walltime e.g. 01:00:00 hours
        WT=$WT ${scriptfolder}/submit_postpros.bash ${outputroot}/${simulation}/${outputname}.ts $scriptname $jobflag $jobnamepostfix
    fi

    echo ' '
    echo 'Submittoitu postprosessointiin'

}

function postprosessoiinteractive {

    echo ' '
    simulation=$1
    outputname=$2
    folderROOT=$3


    ncsub=${ncsub:-true}
    pssub=${pssub:-true}
    tssub=${tssub:-true}


    # if outputname doesn't exist set it to be same as simulation
    if [[ -z $outputname ]]; then
        outputname=${simulation}
    fi

    # if scriptfolder doesn't exist set it to be the default
    if [[ -z $scriptfolder ]]; then
        scriptfolder=${SCRIPT}
    fi


    if [[ -z $folderROOT ]]; then
        folderROOT=$outputroot
    fi


    if [[ $ncsub == "true" ]]; then
        echo ' '
        echo 'Nyt postprosessoidaan nc'
        python ${scriptfolder}/${scriptname} ${folderROOT}/${simulation}/${outputname}
    fi

    if [[ $pssub == "true" ]]; then
        echo ' '
        echo 'Nyt postprosessoidaan ps'
        python ${scriptfolder}/${scriptname} ${folderROOT}/${simulation}/${outputname}.ps
    fi

    if [[ $tssub == "true" ]]; then
        echo ' '
        echo 'Nyt postprosessoidaan ts'
        python ${scriptfolder}/${scriptname} ${folderROOT}/${simulation}/${outputname}.ts
    fi

    echo ' '
    echo 'Postprosessoitu'

}

function viimeksimuutettu {

    simulation=$1
    outputname=$2
    folderROOT=$3

    timeParam=${timeParam:-3600}

    aika=$(date +%s)

    viimeks=$(find ${simulation}/ -printf "%T@\n" | sort | tail -1)
    #viimeks=$(find ${simulation}/ -type f -exec stat \{} --printf='%(%s)T\n' \; | sort -n -r | head -n 1)
    viimeksInt=$(python -c "print(str($viimeks).split('.')[0])")
    ika=$(( aika-viimeksInt ))
    if [[ $ika -gt $timeParam ]];
    then

        echo 'true'
    else
        echo 'false'
    fi

}

function jatkokasittelesimulaatio {

    simulation=$1
    outputname=$2
    folderROOT=$3
    jobnamepostfix=$4

    if [[ -z $outputname ]]; then
        outputname=${simulation}
    fi

    if [[ -z $folderROOT ]]; then
        folderROOT=$outputroot
    fi


    status=$( tarkistastatus $simulation $outputname $folderROOT)
    LS=${status:0:1}
    PPS=${status:1:2}

#     if [[ $simulation == "case_isdac_LVL5_3D_ice1_v5.2_RadiationOn_aero1.5" ]]
#     then
#         echo "case_isdac_LVL5_3D_ice1_v5.2_RadiationOn_aero1.5 ei tätä" $status
#         exit 0
#     fi
    vanha=$( viimeksimuutettu $simulation $outputname $folderROOT)

    if [[ $vanha == "true" ]]
    then

        if [[ $status == '20' ]]
        then

            echo 'Status' $status 'simulaatio' $simulation  'on kesken, RESUBMIT'
            sed -i "/runtype\s\{0,\}=\s\{0,\}/c\  runtype  = '"HISTORY"'"  ${folderROOT}/${simulation}/NAMELIST
            qsub ${folderROOT}/${simulation}/runles.sh

        elif [[ $status == '13' ]]
        then

            echo 'Status' $status 'simulaatio' $simulation  'on valmis, postprosessointi puuttuu'
            WT=24:00:00 postprosessoi $simulation $outputname $jobnamepostfix

        elif [[ $status == '11' ]]
        then

            echo 'Simulaatio' $simulation  'valmis'
            poistaturhat $simulation $outputname $folderROOT
            #rsync -avz ${folderROOT}/${simulation}/ /ibrix/arch/ClimRes/aholaj/ISDAC/${simulation}/
            #rm -rf ${folderROOT}/${simulation}/


        elif [[ $status == '00' ]]
        then
            echo 'Simulaatio' $simulation  'alkutilassa'
        fi
    else
        echo "Simulaatio ei ole tarpeeksi vanha"
    fi


}

function poistaturhat {


    simulation=$1
    outputname=$2
    folderROOT=$3

    override=${override:-false}



    if [[ -z $outputname ]]; then
        outputname=${simulation}
    fi

    if [[ -z $folderROOT ]]; then
        folderROOT=$outputroot
    fi

    echo 'Tarkastellaan statusta, kansio :' ${simulation}

    status=$( tarkistastatus $simulation $outputname $folderROOT)
    LS=${status:0:1}
    PPS=${status:1:2}

    if [[ $status == '11' ]]
    then
        echo 'Simulaatio' $simulation  'on valmis poistetaan turhat'
    fi

    if [[ $override == 'true' ]]
    then
        echo 'poistetaan turhat, koska override'
    fi

    if [ $status == '11'  ] || [ $override == 'true' ]; then
        echo 'DELETING'
#       rm -rf ${folderROOT}/${simulation}/datafiles
        rm -rf ${folderROOT}/${simulation}/*.*.sh
        rm -rf ${folderROOT}/${simulation}/*.py
        rm -rf ${folderROOT}/${simulation}/*.rst
        rm -rf ${folderROOT}/${simulation}/${outputname}.ts.0*0*.nc
        rm -rf ${folderROOT}/${simulation}/${outputname}.ps.0*0*.nc
        rm -rf ${folderROOT}/${simulation}/${outputname}.0*0*.nc
        rm -rf ${folderROOT}/${simulation}/0*_0*.${outputname}.*
        if [[  $override == 'true' ]]; then
            rm -rf ${folderROOT}/${simulation}/*.sdb.OU
            rm -rf ${folderROOT}/${simulation}/*.log
            rm -rf ${folderROOT}/${simulation}/core
            sed -i "/runtype\s\{0,\}=\s\{0,\}/c\  runtype  = '"INITIAL"'"  ${folderROOT}/${simulation}/NAMELIST
        fi
    elif [ $PPS -eq 2 ] || [ $LS -eq 2 ] && [ $override != 'true' ]
    then
        echo "Restartataan, koska jokin simulaation vaiheista on kesken, poistetaan mahdolliset postprosessoidut setit"
        rm -rf ${folderROOT}/${simulation}/${outputname}.nc ${folderROOT}/${simulation}/${outputname}.ts.nc  ${folderROOT}/${simulation}/${outputname}.ps.nc

    else
        echo 'Simulaatio' $simulation "on alkutilassa ei poisteta turhia"
    fi
    echo $outputname 'status' $status
}

# this function returns following values according to status of simulation and post-prosessing
#    00 (LES not ready  POSTPROS not ready )
#    11 (LES     ready  POSTPROS     ready )
#    22 (LES incomplete POSTPROS incomplete)
#    13 (LES complete   POSTPROS incomplete)
function tarkistastatus {
    simulation=$1
    outputname=$2
    folderROOT=$3

    if [[ -z $outputname ]]; then
        outputname=${simulation}
    fi

    if [[ -z $folderROOT ]]; then
        folderROOT=${outputroot}
    fi
    #################
    #### LESin STATUS
    #################
    for f in ${folderROOT}/${simulation}/NAMELIST; do
        [ -e "$f" ] && timmaxapu=$(cat ${folderROOT}/${simulation}/NAMELIST | grep timmax) && timmax=$(python -c "print('${timmaxapu}'.split('=')[1].split('.')[0].replace(' ', ''))") || timmax=100000000
        break
    done
    apulast=0
    last=0
    for f in ${folderROOT}/${simulation}/LES*${outputPostfix} ${folderROOT}/${simulation}/*.sdb.OU; do
        [ -e "$f" ] && apulast=$( cat $f | grep --ignore-case "model time" | tail -1 | cut -c40-46 ) || last=0
        if [[ $apulast -ge last ]]; then
            last=$apulast
        fi
    done

    if [[ $last -ge $((timmax-1)) ]]; then
        for f in ${folderROOT}/${simulation}/*.nc; do
            [ -e "$f" ] && les=1 || les=0
            break
        done
    else
        for f in ${folderROOT}/${simulation}/*.rst; do # les ei ole valmis, voidaan restartata jos tiedostot on olemassa
            [ -e "$f" ] && les=2 || les=0
            break
        done
    fi

    #touch ${folderROOT}/${simulation}/debug${outputname}.log #debugkebab
    #echo $simulation $outputname 'ollaan tarkistastatuksessa LESSIN STATUKSEN tarkastelun jalkeen LES status' $les >> ${folderROOT}/${simulation}/debug${outputname}.log   #debugkebab
    ############################
    #### postprosessointi STATUS
    ############################
    if [[ $les == 1 ]]; then
        if [ -f ${folderROOT}/${simulation}/${outputname}.nc ] && [ -f ${folderROOT}/${simulation}/${outputname}.ts.nc ] && [ -f ${folderROOT}/${simulation}/${outputname}.ps.nc ]; then
            #lasttimeNC=$( ncdump -v time -f fortran ${folderROOT}/${simulation}/${outputname}.nc    | tail -2 | head -1 | cut -f 1 --delimiter=/ |tr -dc '[:alnum:].' | cut -f 1 --delimiter=. )
	    lasttimeNC=$timmax
            lasttimePS=$( ncdump -v time -f fortran ${folderROOT}/${simulation}/${outputname}.ps.nc | tail -2 | head -1 | cut -f 1 --delimiter=/ | tr -dc '[:alnum:].' | cut -f 1 --delimiter=. )
            lasttimeTS=$( ncdump -v time -f fortran ${folderROOT}/${simulation}/${outputname}.ts.nc | tail -2 | head -1 | cut -f 1 --delimiter=/ | tr -dc '[:alnum:].' | cut -f 1 --delimiter=. )
	    PPtime=$( python -c "print(min( $lasttimeNC, $lasttimePS, $lasttimeTS ))" )

    	    if [[ $PPtime -ge $((timmax-1)) ]]; then
	        postpros=1
            else
                postpros=2
            fi
	    #for f in ${folderROOT}/${simulation}/${outputname}*.0*0*.nc; do # jos postprosessoituja filuja on, mutta prossufiluja on edelleen olemassa niin postprosessoidaan uusiks ja lessi on tosiaan valmis; muutoin ollaan valmiita
            #    [ -e "$f" ] && postpros=2 || postpros=1
            #    break
            #done

        else
            for f in ${folderROOT}/${simulation}/${outputname}*.0*0*.nc; do # jos postprosessoituja filuja ei ole,  mutta prossufiluja on, postprosessoidaan uusiks; jos mitään ei ole kaikki menee urhomatti
                if [ -e "$f" ]; then
                    postpros=3 #les is ready and pospros is ready to be postprocessed
                else
                    postpros=0
                    les=0
                fi
                break
            done
        fi
    else
        postpros=0
    fi

    #echo 'ollaan tarkistastatuksessa POSTPROS STATUKSEN tarkastelun jalkeen LES status' $les 'postpros status' $postpros  >> ${folderROOT}/${simulation}/debug${outputname}.log #debugkebab
    echo ${les}${postpros}

}
