#!/bin/bash 
 
#PBS -q dssc
#PBS -l nodes=2:ppn=24
#PBS -l walltime=0:30:00 

cd $PBS_O_WORKDIR 
module load openmpi/4.0.3/gnu/9.3.0 

format="user : %U system: %S elapsed: %e CPU: %P CMD: %C \n"
EXE=jacoby3D.x
data=input.dat
value_0=600


run_jacoby(){
    n1=$1
    n2=$2
    n3=$3


    echo $(( value_0 * n1 )), $n1, t > $data
    echo $(( value_0 * n2 )), $n2, t >> $data
    echo $(( value_0 * n3 )), $n3, t >> $data

    out_file=thin/${n1}_${n2}_${n3}.out
    time_file=thin/time_${n1}_${n2}_${n3}.out

    n=$((n1 * n2 * n3))

    /usr/bin/time -f $format mpirun --mca btl ^openib --map-by core -np $n $EXE < $data >> $out_file 2>>$time_file
}

run_jacoby 1 1 1
run_jacoby 2 1 1
run_jacoby 3 1 1
run_jacoby 4 1 1 
run_jacoby 2 2 1