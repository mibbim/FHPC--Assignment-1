#!/bin/bash 

n_iter = 10
for i in `seq 1 10`; do
    for procs in 6; do
        mpirun -np ${procs} non_blocking.x >> srsrww.out
        # echo ${i}
        # echo procs
    done
done 