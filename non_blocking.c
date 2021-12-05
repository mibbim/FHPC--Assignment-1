#include <stdio.h>
#include <mpi.h>

#define FALSE 0
#define TRUE 1
#define NLAP 100000

int main(int argc, char *argv[])
{
    double start_time, comp_time, end_time;
    int myid, numprocs, proc;
    MPI_Status status_left_recv;  // the status of a reception operation, returned by receive operations
    MPI_Status status_right_recv; // the status of a reception operation, returned by receive operations
    MPI_Status status_left_send;  // the status of a reception operation, returned by receive operations
    MPI_Status status_right_send; // the status of a reception operation, returned by receive operations
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
    MPI_Cart_create(MPI_COMM_WORLD, 1, &numprocs, true_arr, TRUE, &ring); // Makes a new communicator to which topology information has been attached

    MPI_Comm_rank(MPI_COMM_WORLD, &myid);

    MPI_Cart_shift(ring, 0, 1, &left_processor, &right_processor);

    MPI_Request request_right_send;
    MPI_Request request_right_recv;
    MPI_Request request_left_send;
    MPI_Request request_left_recv;

    int msg_from_left;
    int msg_from_right;

    int msg_tag_from_left = myid;
    int msg_tag_from_right = myid;
    // --------------------------------------------------------------------------------------

    tag = myid;

    int msg_counter = 0;
    int msg_to_left = myid;

    // printf("%d: sending %d to %d, tag: %d, \n", myid, msg_to_left, left_processor, tag);
    MPI_Isend(&msg_to_left, msg_size, MPI_INT, left_processor, myid, ring, &request_left_send);
    MPI_Irecv(&msg_from_right, msg_size, MPI_INT, right_processor, MPI_ANY_TAG, ring, &request_right_recv);
    ++msg_counter;

    MPI_Wait(&request_left_send, &status_left_send);
    MPI_Wait(&request_right_recv, &status_right_recv);
    // if (myid == numprocs - 1)
    // {
    //     printf("%d: recv %d from %d, tag: %d, from R\n", myid, msg_from_right, right_processor, status_left_recv.MPI_TAG);
    //     fflush(stdout);
    // }
    // printf("%d: recv %d from %d, tag: %d, from R\n", myid, msg_from_right, right_processor, status_right_recv.MPI_TAG);

    int msg_to_right = -myid;
    // printf("%d: sending %d to %d, tag: %d, \n", myid, msg_to_right, right_processor, tag);
    MPI_Isend(&msg_to_right, msg_size, MPI_INT, right_processor, tag, ring, &request_right_send);
    // MPI_Isend(&msg_to_right, msg_size, MPI_INT, right_processor, 100, ring, &request_right_send)
    MPI_Irecv(&msg_from_left, msg_size, MPI_INT, left_processor, MPI_ANY_TAG, ring, &request_left_recv);
    ++msg_counter;

    MPI_Wait(&request_right_send, &status_right_send);
    MPI_Wait(&request_left_recv, &status_left_recv);
    // if (myid == numprocs - 1)
    // {
    //     printf("%d: recv %d from %d, tag: %d, from L\n", myid, msg_from_left, left_processor, status_left_recv.MPI_TAG);
    //     fflush(stdout);
    // }

    // printf("%d: recv %d from %d, tag: %d, from L\n", myid, msg_from_left, left_processor, status_left_recv.MPI_TAG);
    // printf("I am process %d and i have received %d messages. My final messages have tag %d, %d and value %d, %d \n",
    // myid, msg_counter, status_left_recv.MPI_TAG,status_right_recv.MPI_TAG, msg_from_left, msg_from_right);
    // if (myid == numprocs - 1)
    // {
    //     printf("I'm proc %d and i'm entering for loop\n", myid);
    //     fflush(stdout);
    // }

    for (int i = 0; i < (numprocs * NLAP) - 1; ++i)
    {
        int watch = i;
        msg_to_left = msg_from_right + myid;
        // MPI_Send(&msg_to_left, msg_size, MPI_INT, left_processor, myid * i, ring);
        // MPI_Recv(&msg_tag_from_right, msg_size, MPI_INT, right_processor, MPI_ANY_TAG, ring, &status);
        tag = myid;
        // printf("%d: sending %d to %d, tag: %d, ", myid, msg_to_left, left_processor, tag);
        MPI_Isend(&msg_to_left, msg_size, MPI_INT, left_processor, tag, ring, &request_left_send);
        MPI_Irecv(&msg_from_right, msg_size, MPI_INT, right_processor, MPI_ANY_TAG, ring, &request_right_recv);

        MPI_Wait(&request_left_send, &status_left_send);
        MPI_Wait(&request_right_recv, &status_right_recv);
        ++msg_counter;
        // if (myid == watch)
        // {
        //     printf("%d: recv %d from %d, tag: %d, from R\n", myid, msg_tag_from_right, right_processor, status_right_recv.MPI_TAG);
        //     fflush(stdout);
        // }

        msg_to_right = msg_from_left - myid;
        MPI_Isend(&msg_to_right, msg_size, MPI_INT, right_processor, myid, ring, &request_right_send);
        MPI_Irecv(&msg_from_left, msg_size, MPI_INT, left_processor, MPI_ANY_TAG, ring, &request_left_recv);

        MPI_Wait(&request_right_send, &status_right_send);
        MPI_Wait(&request_left_recv, &status_left_recv);
        ++msg_counter;
        // if (myid == watch)
        // {
        //     // printf("%d: recv %d from %d, tag: %d, from L\n", myid, msg_from_left, left_processor, status_left_recv.MPI_TAG);
        //     // fflush(stdout);
        // }
    }

    MPI_Barrier(MPI_COMM_WORLD);

    if (myid == master)
    {
        end_time = MPI_Wtime();
        double time = end_time - start_time;
        printf("The duration of the process is %f \n", time);
        fflush(stdout);
    }
    printf("I am process %d and i have received %d messages. My final messages have tag %d and value %d \n", myid, msg_counter, status_right_recv.MPI_TAG, msg_from_right);
    printf("I am process %d and i have received %d messages. My final messages have tag %d and value %d \n", myid, msg_counter, status_left_recv.MPI_TAG, msg_from_left);

    MPI_Finalize();
    return 0;
}