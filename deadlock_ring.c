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

    if (myid == master)
    {
        printf("we use %d processors \n", numprocs);
        start_time = MPI_Wtime();
    }

    MPI_Comm ring;
    MPI_Cart_create(MPI_COMM_WORLD, 1, &numprocs, true_arr, TRUE, &ring); //Makes a new communicator to which topology information has been attached

    MPI_Cart_shift(ring, 0, 1, &left_processor, &right_processor);

    int msg_from_left;
    int msg_from_right;

    int msg_tag_from_left = myid;
    int msg_tag_from_right = myid;
    // --------------------------------------------------------------------------------------

    int msg_counter = 0;
    int msg_to_left = myid;

    MPI_Send(&msg_to_left, msg_size, MPI_INT, left_processor, myid, ring);
    MPI_Recv(&msg_tag_from_right, msg_size, MPI_INT, right_processor, MPI_ANY_TAG, ring, &status);
    ++msg_counter;

    int msg_to_right = -myid;
    MPI_Send(&msg_to_right, msg_size, MPI_INT, right_processor, myid, ring);
    MPI_Recv(&msg_tag_from_left, msg_size, MPI_INT, left_processor, MPI_ANY_TAG, ring, &status);
    ++msg_counter;

    printf("I'm proc %d and i'm entering for loop", myid);

    for (int i = 0; i < numprocs - 1; ++i)
    {
        msg_to_left = msg_from_right + myid;
        MPI_Send(&msg_to_left, msg_size, MPI_INT, left_processor, myid * i, ring);
        MPI_Recv(&msg_tag_from_right, msg_size, MPI_INT, right_processor, MPI_ANY_TAG, ring, &status);
        ++msg_counter;

        msg_to_right = msg_from_left - myid;
        MPI_Send(&msg_to_right, msg_size, MPI_INT, right_processor, myid * i, ring);
        MPI_Recv(&msg_tag_from_left, msg_size, MPI_INT, left_processor, MPI_ANY_TAG, MPI_COMM_WORLD, &status);
        ++msg_counter;
    }

    printf("I am process %d and i have received %d messages. My final messages have tag %d and value %d, %d \n", myid, msg_counter, status.MPI_TAG, msg_from_left, msg_from_right);

    MPI_Barrier(MPI_COMM_WORLD);

    if (myid == master)
    {
        end_time = MPI_Wtime();
        double time = end_time - start_time;
        printf("The duration o the process is %f \n", time);
    }

    MPI_Finalize();
    return 0;
}