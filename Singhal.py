import mpi4py
mpi4py.rc.initialize = False  # do not initialize MPI automatically
mpi4py.rc.finalize = False    # do not finalize MPI automatically
from mpi4py import MPI # import the 'MPI' module
# Singhal-Kshemkalyani techniques for vector clock
# please run the command below
# mpiexec -n 4 python3 Singhal.py
def main() :
    MPI.Init()      # manual initialization of the MPI environment
    # number of events
    event = 5
    comm = mpi4py.MPI.COMM_WORLD
    rank =comm.Get_rank()
    size =comm.Get_size()

    # The vector to store both local and global time
    vector = [0 for i in range(size)]

    # This method need to remember the last vector send to another process
    memory_matrix = [[0 for j in range(size) ] for i in range(size)]
    # Loop through the events
    for i in range(event):

        communication(0,1,vector,1,1,rank,memory_matrix,comm)
        communication(2,1,vector,1,2,rank,memory_matrix,comm)
        communication(3,2,vector,1,3,rank,memory_matrix,comm)
        communication(2,1,vector,2,3,rank,memory_matrix,comm)
        communication(2,1,vector,4,4,rank,memory_matrix,comm)
        print("process " , rank , " : " , vector)
        vector[rank] += 1
    MPI.Finalize()  # manual finalization of the MPI environment

def update_timestamp(vector, data):
    """
    Updates the timestamp in the receiving event
    :param vector: current vector
    :param data: piggybacked data
    :return: new vector
    """
    for i in range (len(data)):
        vector[data[i][0]] = max(vector[data[i][0]],data[i][1])
    return vector
def communication(pid1, pid2,vec,event1,event2,rank,mem_matrix1,comm):
    """
    Simulates a communication between event1 process 1 with event 2 process 2
    :param pid1: process id 1 (the sending process)
    :param pid2: process id 2 (the receiving process)
    :param vec: the vector of current process
    :param event1: event in process 1 (the sending event)
    :param event2: event in process 2 (the receiving event)
    :param rank: current process
    :param mem_matrix1: the memory matrix of sending process
    :param comm: COMMUNICAUIN LINE
    :return: new vector
    """
    if rank == pid1 and vec[rank] == event1 :
        print("send Pid {", pid1 , "} ---> {" , pid2, "}" )
        data = []
        # checks the memory and compared it, only sent the data if the information
        # in the current vector have changed since the matrix
        for i in range(len(vec)):
            if vec[i] != mem_matrix1[pid2][i] :
                data.append((i,vec[i]))
        new_vec = [i for i in vec]
        mem_matrix1[pid2] = new_vec
        comm.send(data, dest=pid2, tag=0)
    elif rank == pid2 and vec[rank] == event2:
        data = comm.recv(source=pid1, tag=0)
        print("receive Pid {", pid1 , "} ---> {" , pid2, "} message :" , data )
        vec = update_timestamp(vec, data)
    return vec


main()

