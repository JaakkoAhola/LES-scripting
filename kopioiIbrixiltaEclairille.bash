#!/bin/bash
kohde=${ECLAIR}/UCLALES-SALSA_training_simulations/
echo $kohde
mkdir -p $kohde
rsync -avz --exclude="*datafiles*" ${IBRIX}/case_emulator_* ${kohde}/
printf "IBRIX COPY FINISHED TO $kohde \n\n -Jaakko- \n\n PS This was an automated message" | mail -s "IBRIX COPY FINISHED to $kohde" Jaakko.Ahola@fmi.fi #,Muzaffer.Ege.Alper@fmi.fi,Tomi.Raatikainen@fmi.fi -r jaakko.ahola@fmi.fi