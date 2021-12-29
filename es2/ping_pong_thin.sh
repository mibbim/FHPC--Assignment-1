#!/bin/bash
 
#PBS -q dssc
#PBS -l nodes=ct1pt-tnode009:ppn=2+ct1pt-tnode010:ppn=2
#PBS -l walltime=1:00:00

# OpenMPI --------------------------------
cd /u/dssc/s239635/2021/Foundations_of_HPC_2021/mpi-benchmarks/src_c
make clean
module load openmpi/4.0.3/gnu/9.3.0
make
EXE="/u/dssc/s239635/2021/Foundations_of_HPC_2021/mpi-benchmarks/src_c/IMB-MPI1"
cd $PBS_O_WORKDIR

# by node 
for i in 1 2 3 4 5 6 7 8 9 10; do 
    echo ${EXE} 
    mpirun --map-by node -np 2 ${EXE} PingPong -msglog 28 | grep -v ^\# | grep -v '^$' | sed -r 's/^\s+//;s/\s+/,/g' >> node_ib.out 
    mpirun --map-by node --mca pml ucx -mca btl ^uct -x UCX_NET_DEVICES=ib0 -np 2 ${EXE} PingPong -msglog 28 | grep -v ^\# | grep -v '^$' | sed -r 's/^\s+//;s/\s+/,/g' >> node_ucx_ib0.out 
    mpirun --map-by node --mca pml ucx -mca btl ^uct -x UCX_NET_DEVICES=br0 -np 2 ${EXE} PingPong -msglog 28 | grep -v ^\# | grep -v '^$' | sed -r 's/^\s+//;s/\s+/,/g' >> node_ucx_br0.out 
    mpirun --map-by node --mca pml ucx -mca btl ^uct -x UCX_NET_DEVICES=mlx5_0:1 -np 2 ${EXE} PingPong -msglog 28 | grep -v ^\# | grep -v '^$' | sed -r 's/^\s+//;s/\s+/,/g' >> node_ucx_mlx5.out 
    mpirun --map-by node --mca pml ob1 --mca btl self,tcp -np 2 ${EXE} PingPong -msglog 28 | grep -v ^\# | grep -v '^$' | sed -r 's/^\s+//;s/\s+/,/g' >> node_ob1_selftcp.out 
done 

# bt socket

for i in 1 2 3 4 5 6 7 8 9 10; do 
    mpirun --map-by socket -np 2 ${EXE} PingPong -msglog 28 | grep -v ^\# | grep -v '^$' | sed -r 's/^\s+//;s/\s+/,/g' >> socket_ib.out 
    mpirun --map-by socket --mca pml ob1 --mca btl self,vader -np 2 ${EXE} PingPong -msglog 28 | grep -v ^\# | grep -v '^$' | sed -r 's/^\s+//;s/\s+/,/g' >> socket_ob1_selfvader.out 
    mpirun --map-by socket --mca pml ob1 --mca btl self,tcp -np 2 ${EXE} PingPong -msglog 28 | grep -v ^\# | grep -v '^$' | sed -r 's/^\s+//;s/\s+/,/g' >> socket_ob1_selftcp.out 
done 
 
for i in 1 2 3 4 5 6 7 8 9 10; do 
    mpirun --map-by core -np 2 ${EXE} PingPong -msglog 28 | grep -v ^\# | grep -v '^$' | sed -r 's/^\s+//;s/\s+/,/g' >> core_ib.out 
    mpirun --map-by core --mca pml ob1 --mca btl self,vader -np 2 ${EXE} PingPong -msglog 28 | grep -v ^\# | grep -v '^$' | sed -r 's/^\s+//;s/\s+/,/g' >> core_ob1_selfvader.out 
    mpirun --map-by core --mca pml ob1 --mca btl self,tcp -np 2 ${EXE} PingPong -msglog 28 | grep -v ^\# | grep -v '^$' | sed -r 's/^\s+//;s/\s+/,/g' >> core_ob1_selftcp.out 
done 

cat $PBS_NODEFILE >> thin_resources_used.out 

# Intel -----------------------------------------------
cd /u/dssc/s239635/2021/Foundations_of_HPC_2021/mpi-benchmarks/src_c
make clean
module unload openmpi/4.0.3/gnu/9.3.0
module load intel
make
EXE="/u/dssc/s239635/2021/Foundations_of_HPC_2021/mpi-benchmarks/src_c/IMB-MPI1"
cd $PBS_O_WORKDIR

for i in 1 2 3 4 5 6 7 8 9 10; do 
    mpirun -f $PBS_NODEFILE ${EXE} PingPong -msglog 28 | grep -v ^\# | grep -v '^$' | sed -r 's/^\s+//;s/\s+/,/g' >> node_ib_intel.out 
done 
 
for i in 1 2 3 4 5 6 7 8 9 10; do 
    mpirun -genv I_MPI_PIN_PROCESSOR_LIST 0,1 ${EXE} PingPong >> socket_ib_intel.out
done 
 
for i in 1 2 3 4 5 6 7 8 9 10; do 
    mpirun -genv I_MPI_PIN_PROCESSOR_LIST 0,2 ${EXE} PingPong >> core_ib_intel.out
done 

 
cat $PBS_NODEFILE >> thin_resources_used_intel.out 
 
rm task*