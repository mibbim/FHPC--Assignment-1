#include <stdio.h>
#include <mpi.h>

#define FALSE 0
#define TRUE 1

int main(int argc, char *argv[])
{
    double start_time, comp_time, end_time;
    int myid, numprocs, proc;
    MPI_Status status; // the status of a reception operation, returned by receive operations
    // MPI_Request request;

    int master = 0;
    int tag;
    int right_processor, left_processor;

    const int msg_size = 1;
    const int true_arr[1] = {TRUE};
    // const int false_arr[1] = {FALSE};

    MPI_Init(&argc, &argv);

    MPI_Comm_rank(MPI_COMM_WORLD, &myid);
    MPI_Comm_size(MPI_COMM_WORLD, &numprocs);

    MPI_Comm ring;
    MPI_Cart_create(MPI_COMM_WORLD, 1, &numprocs, true_arr, TRUE, ring); //Makes a new communicator to which topology information has been attached

    MPI_Cart_shift(ring, 0, 1, &left_processor, &right_processor);

    start_time = MPI_Wtime();
    {
        int msg_from_left;
        int msg_from_right;

        int msg_to_left = myid;
        int msg_to_right = -myid;

        int msg_tag_from_left = myid;
        int msg_tag_from_right = myid;

        MPI_Isend(&msg_to_right, msg_size, MPI_INT, right_processor, msg_tag_to_left, MPI_COMM_WORLD);
        MPI_Isend(&msg_to_left, msg_size, MPI_INT, left_processor, msg_tag_to_right, MPI_COMM_WORLD);

        
        MPI_Irecv(&msg_from_left, msg_size, MPI_INT, left_processor, MPI_ANY_TAG, MPI_COMM_WORLD)
        MPI_Irecv(&msg_from_right, msg_size, MPI_INT, left_processor, MPI_ANY_TAG, MPI_COMM_WORLD)

        // for (int i = 0; i < 2 * (numprocs - 1); ++i)
        // {
        //     MPI_Send();

        //     MPI_Recv(msg_l, msg_dim, MPI_INT, MPI_ANY_SOURCE, MPI_ANY_TAG, ring, status);
        // }
    }
    end_time = MPI_Wtime();
    time = end_time - start_time;

    return 0;
}