#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>
#include <unistd.h>

#define FALSE 0
#define TRUE 1

void print_3_D_matrix(double *m, size_t *sizes, size_t stop)
// Simple print of the first stop elements of the matrix
{
    for (int k = 0; k < sizes[2]; ++k)
    {
        size_t shift_k = k * sizes[0] * sizes[1];

        for (int j = 0; j < sizes[1]; ++j)
        {
            size_t shift = shift_k + j * sizes[0];
            for (int i = 0; i < sizes[0]; ++i)
            {
                if (shift + i == stop)
                {
                    return;
                }
                printf("%f ", m[shift + i]);
            }
            printf("\n");
        }
        printf("\n");
    }
}

int main(int argc, char **argv)
{
#ifdef DEBUG
    // for (int i = 0; i < argc; ++i)
    //     printf("%s \n", argv[i]);
#endif

    int myid, numprocs;
    int master = 0;
    MPI_Init(&argc, &argv);
    MPI_Comm_size(MPI_COMM_WORLD, &numprocs);
    MPI_Comm_rank(MPI_COMM_WORLD, &myid);

    if (argc != 4)
    {
        if (myid == master)
        {
            printf("Wrong numebr of command line argument\n");
            printf("Usage: \n mpirun -np n %s dim1 dim2 dim3 \n", argv[0]);
        }
        exit(1);
    }

    //  Parsing the inpunt value ------------------

    int matrix_dim = 3;       // _global_: dimesions of the matrix (3)
    size_t sizes[matrix_dim]; // _global_: sizes of the matrices to sum
    int topo_dim;             //_global_: dimensions of the virtual topology
    int *topo_sizes;
    for (int i = 0; i < matrix_dim; ++i)
    {
        sizes[i] = atoi(argv[i + 1]);
    }

    // if (argc == 4)
    // {
    topo_dim = 1;
    topo_sizes = malloc(topo_dim * sizeof(int));
    // if (myid == 0)
    //     printf("No indication on topology was given, running with a 1D Topology with the max number of processors\n");
    for (int i = 0; i < topo_dim; ++i)
        topo_sizes[i] = numprocs;
    // }

    // topo_sizes[i] = atoi(argv[1 + matrix_dim + i]);

    int reorder = FALSE; // no need to communicate -> no need of reordering
    MPI_Comm comm;       // communicator with virtual topology
    int pbc[topo_dim];
    for (int i = 0; i < topo_dim; ++i)
        pbc[i] = TRUE;

#ifdef DEBUG
// printf("topo_dim: %d", topo_dim);
// for (int i = 0; i < topo_dim; ++i)
// printf("pbc[%d]: %d", i, pbc[i]);
#endif

#ifdef DEBUG
// for (int i = 0; i < topo_dim; ++i)
// printf("pbc[%d]: %d, topo_sizes[%d]:%d \n", i, pbc[i], i, topo_sizes[i]);
// fflush(stdout);
#endif

    MPI_Cart_create(MPI_COMM_WORLD,
                    topo_dim,
                    topo_sizes,
                    pbc,
                    reorder,
                    &comm);
    MPI_Comm_rank(comm, &myid);

#ifdef DEBUG

    // for (int i = 0; i < 3; ++i)
    // {
    // printf("sizes[%d] %d \n", i, sizes[i]);
    // }
#endif

    double *matrix_A;
    double *matrix_B;
    double *matrix_C;

    size_t effective_size = sizes[0] * sizes[1] * sizes[2];
    if (myid == master)
    {
        matrix_A = (double *)malloc(sizeof(double) * effective_size);
        matrix_B = (double *)malloc(sizeof(double) * effective_size);
        matrix_C = (double *)malloc(sizeof(double) * effective_size);

        for (size_t i = 0; i < effective_size; ++i)
        {
            matrix_A[i] = drand48();
            matrix_B[i] = drand48();
        }
    }
    // ---- DEBUGGING ----
#ifdef DEBUG
    // printf("effective_size: %ld\n", efffective_size);
    // printf("initialized\n");
    // fflush(stdout);
#endif

#ifdef DEBUG
    if (myid == master)
    {
        printf("Here the generated 3D matrices \n");
        print_3_D_matrix(matrix_A, sizes, effective_size);
        printf("---------------------------\n");
        print_3_D_matrix(matrix_B, sizes, effective_size);
    }
#endif

    int *chunk_sizes = (int *)malloc(sizeof(int) * numprocs);
    int *displacements = (int *)malloc(sizeof(int) * numprocs);
    int base_chunk_size = effective_size / numprocs;
    int leftovers = effective_size - (base_chunk_size * numprocs);
    for (int i = 0; i < numprocs; ++i)
        chunk_sizes[i] = base_chunk_size;

    for (int i = 0; i < leftovers; ++i)
        chunk_sizes[i] += 1;

    size_t accumulator = 0;
    for (int i = 0; i < numprocs; ++i)
    {
        displacements[i] = accumulator;
        accumulator += chunk_sizes[i];
    }
    double *local_A = (double *)malloc(chunk_sizes[myid] * sizeof(double));
    double *local_B = (double *)malloc(chunk_sizes[myid] * sizeof(double));
    double *local_C = (double *)malloc(chunk_sizes[myid] * sizeof(double));

    MPI_Scatterv(matrix_A,
                 chunk_sizes,
                 displacements,
                 MPI_DOUBLE,
                 local_A,
                 chunk_sizes[myid],
                 MPI_DOUBLE,
                 master,
                 comm);

    MPI_Scatterv(matrix_B,
                 chunk_sizes,
                 displacements,
                 MPI_DOUBLE,
                 local_B,
                 chunk_sizes[myid],
                 MPI_DOUBLE,
                 master,
                 comm);

#ifdef DEBUG
// printf("I'm proc %d and I recieved the matrices \n", myid);
// fflush(stdout);
#endif

    for (size_t i = 0; i < chunk_sizes[myid]; ++i)
    {
        local_C[i] = local_A[i] + local_B[i];
    }

#ifdef DEBUG
    sleep(myid * 2);
    printf("I'm proc %d and I summed my chunk: \n", myid);
    int counter = 0;
    print_3_D_matrix(local_A, sizes, chunk_sizes[myid]);
    fflush(stdout);
#endif

    MPI_Gatherv(local_C,
                chunk_sizes[myid],
                MPI_DOUBLE,
                matrix_C,
                chunk_sizes,
                displacements,
                MPI_DOUBLE,
                master,
                comm);

    free(local_A);
    free(local_B);
    free(local_C);

#ifdef DEBUG
    printf("I'm proc %d and I ended the gathering: \n", myid);
    fflush(stdout);
    if (myid == master)
    {
        print_3_D_matrix(matrix_C, sizes, effective_size);
        // printf("Here the summed 3D matrix \n");
        // for (int k = 0; k < sizes[2]; ++k)
        // {
        //     int shift_k = k * sizes[0] * sizes[1];
        //     for (int j = 0; j < sizes[1]; ++j)
        //     {
        //         int shift = shift_k + j * sizes[0];
        //         for (int i = 0; i < sizes[0]; ++i)
        //             printf("%f ", matrix_C[shift + i]);

        //         printf("\n");
        //     }
        //     printf("\n");
        // }
        // printf("\n");
    }

#endif

    if (myid == master)
    {
        free(matrix_A);
        free(matrix_B);
        free(matrix_C);
    }

    MPI_Finalize();

    return 0;
}