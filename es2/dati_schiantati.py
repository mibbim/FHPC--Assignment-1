colors = ['tab:blue',
          'tab:orange',
          'tab:green',
          'tab:red',
          'tab:purple',
          'tab:brown',
          'tab:pink',
          'tab:gray',
          'tab:olive',
          'tab:cyan']

metadata_key = ("map", "pml", "btl", "compiler")

info = {
    "core_ib.out": ["core", "ucx", "ib", "open"],
    "core_ib_intel.out": ["core", "ucx", "ib", "intel"],
    "core_ob1_selftcp.out": ["core", "ob1", "tcp", "open"],
    "core_ob1_selfvader.out": ["core", "ob1", "vader", "open"],
    "node_ib.out": ["node", "ucx", "ib", "open"],
    "node_ib_intel.out": ["node", "ucx", "ib", "intel"],
    "node_ob1_selftcp.out": ["node", "ob1", "tcp", "open"],
    "node_ucx_br0.out": ["node", "ucx", "br0", "open"],
    "node_ucx_ib0.out": ["node", "ucx", "ib0", "open"],
    # "node_ucx_mlx5.out": ["node", "ucx", "mlx5", "open"],
    "socket_ib.out": ["socket", "ucx", "ib", "open"],
    "socket_ib_intel.out": ["socket", "ucx", "ib", "intel"],
    "socket_ob1_selftcp.out": ["socket", "ob1", "tcp", "open"],
    "socket_ob1_selfvader.out": ["socket", "ob1", "vader", "open"],
}

labels = {
    "core_ib.out": "ib openMPI",
    "core_ib_intel.out": "ib intel",
    "core_ob1_selftcp.out": "ob1 Tcp",
    "core_ob1_selfvader.out": "ob1 Vader",
    "node_ib.out": "ib openMPI",
    "node_ib_intel.out": "ib itel",
    "node_ob1_selftcp.out": "ob1 Tcp",
    "node_ucx_br0.out": "ucx br0",
    "node_ucx_ib0.out": "ucx ib0",
    # "node_ucx_mlx5.out": ["node", "ucx", "mlx5", "open"],
    "socket_ib.out": "ib openMPI",
    "socket_ib_intel.out": "ib intel",
    "socket_ob1_selftcp.out": "ob1 Tcp",
    "socket_ob1_selfvader.out": "ob1 vader",

}
units = {
    "lambda": "us",
    "bw": "Mb/s"
}

commands = {
    "node_ib.out":
        "mpirun --map-by node -np 2 PingPong -msglog 28 | grep -v ^\# | grep -v '^$' | sed -r 's/^\s+//;s/\s+/,/g'",
    "node_ucx_ib0.out":
        "mpirun --map-by node --mca pml ucx -mca btl ^uct -x UCX_NET_DEVICES=ib0 -np 2 PingPong -msglog 28 | grep -v ^\# | grep -v '^$' | sed -r 's/^\s+//;s/\s+/,/g'",
    "node_ucx_br0.out":
        "mpirun --map-by node --mca pml ucx -mca btl ^uct -x UCX_NET_DEVICES=br0 -np 2 PingPong -msglog 28 | grep -v ^\# | grep -v '^$' | sed -r 's/^\s+//;s/\s+/,/g'",
    "node_ucx_mlx5.out":
        "mpirun --map-by node --mca pml ucx -mca btl ^uct -x UCX_NET_DEVICES=mlx5_0:1 -np 2 PingPong -msglog 28 | grep -v ^\# | grep -v '^$' | sed -r 's/^\s+//;s/\s+/,/g'",
    "node_ob1_selftcp.out":
        "mpirun --map-by node --mca pml ob1 --mca btl self,tcp -np 2 PingPong -msglog 28 | grep -v ^\# | grep -v '^$' | sed -r 's/^\s+//;s/\s+/,/g'",

    "socket_ib.out":
        "mpirun --map-by socket -np 2 PingPong -msglog 28 | grep -v ^\# | grep -v '^$' | sed -r 's/^\s+//;s/\s+/,/g'",
    "socket_ob1_selfvader.out":
        "mpirun --map-by socket --mca pml ob1 --mca btl self,vader -np 2 PingPong -msglog 28 | grep -v ^\# | grep -v '^$' | sed -r 's/^\s+//;s/\s+/,/g'",
    "socket_ob1_selftcp.out":
        "mpirun --map-by socket --mca pml ob1 --mca btl self,tcp -np 2 PingPong -msglog 28 | grep -v ^\# | grep -v '^$' | sed -r 's/^\s+//;s/\s+/,/g'",

    "core_ib.out":
        "mpirun --map-by core -np 2 PingPong -msglog 28 | grep -v ^\# | grep -v '^$' | sed -r 's/^\s+//;s/\s+/,/g'",
    "core_ob1_selfvader.out":
        "mpirun --map-by core --mca pml ob1 --mca btl self,vader -np 2 PingPong -msglog 28 | grep -v ^\# | grep -v '^$' | sed -r 's/^\s+//;s/\s+/,/g'",
    "core_ob1_selftcp.out":
        "mpirun --map-by core --mca pml ob1 --mca btl self,tcp -np 2 PingPong -msglog 28 | grep -v ^\# | grep -v '^$' | sed -r 's/^\s+//;s/\s+/,/g'",

    "node_ib_intel.out":
        "mpirun -f $PBS_NODEFILE ${EXE} PingPong -msglog 28 | grep -v ^\# | grep -v '^$' | sed -r 's/^\s+//;s/\s+/,/g' ",
    "socket_ib_intel.out":
        "mpirun -genv I_MPI_PIN_PROCESSOR_LIST 0,1 ${EXE} PingPong -msglog 28 | grep -v ^\# | grep -v '^$' | sed -r 's/^\s+//;s/\s+/,/g'",

    "core_ib_intel.out":
        "mpirun -genv I_MPI_PIN_PROCESSOR_LIST 0,2 ${EXE} PingPong -msglog 28 | grep -v ^\# | grep -v '^$' | sed -r 's/^\s+//;s/\s+/,/g'",

}
