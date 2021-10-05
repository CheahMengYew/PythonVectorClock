import mpi4py
mpi4py.rc.initialize = False  # do not initialize MPI automatically
mpi4py.rc.finalize = False    # do not finalize MPI automatically
from mpi4py import MPI # import the 'MPI' module
# Jard Jourdan techniques for vector clock
# please run the command below
# mpiexec -n 5 python3 jard_jourdan.py
def main() :
    MPI.Init()      # manual initialization of the MPI environment
    # number of events
    event = 3
    comm = mpi4py.MPI.COMM_WORLD
    rank =comm.Get_rank()
    size =comm.Get_size()

    # The vector to store both local and global time
    vector = [[rank,0]]

    for i in range(event):
        vector = communication(0,1,vector,0,0,rank,comm)
        vector = communication(1,2,vector,0,1,rank,comm)
        vector = communication(4,3,vector,1,0,rank,comm)
        vector = communication(3,4,vector,1,1,rank,comm)
        vector = communication(3,2,vector,1,2,rank,comm)
        print("v_pt" , rank , " = " , vector)
        print("e",vector[0][1] + 1, "pt",rank,"=",vector)

        # reset after observing event
        vector[0][1] += 1
        vector = [vector[0]]
    MPI.Finalize()

def update_timestamp(vector, data):
    """
    Updates the timestamp in the receiving event
    :param vector: current vector
    :param data: piggybacked data
    :return: new vector
    """
    vector = vector + data
    new_vector = []
    # loop through the vector and merged repeated timestamp for the same process by picking the higher value
    for i in range(len(vector)):
        if new_vector == [] :
            new_vector.append(vector[i])
        else:
            for j in range(len(new_vector)):
                if new_vector[j][0] == vector[i][0]:
                    new_vector[j][1] = max(new_vector[j][1], vector[i][1])
                    break
                elif j == len(new_vector) -1 :
                    new_vector.append(vector[i])
    return new_vector


def communication(pid1, pid2,vec,event1,event2,rank,comm):
    """
    Simulates a communication between event1 process 1 with event 2 process 2
    :param pid1: process id 1 (the sending process)
    :param pid2: process id 2 (the receiving process)
    :param vec: the vector of current process
    :param event1: event in process 1 (the sending event)
    :param event2: event in process 2 (the receiving event)
    :param rank: current process
    :param mem_matrix1: the memory matrix of sending process
    :param comm: COMMUNICAtIoN LINE
    :return: new vector
    """
    if rank == pid1 and vec[0][1] == event1 :
        print("send Pid {", pid1 , "} ---> {" , pid2, "}" )
        # sents the whole vector of process 1 in event 1
        data = vec
        comm.isend(data, dest=pid2, tag=0)
    elif rank == pid2 and vec[0][1] == event2:
        req = comm.irecv(source=pid1, tag=0)
        data = req.wait()
        print("receive Pid {", pid1 , "} ---> {" , pid2, "} message :" , data )
        vec = update_timestamp(vec, data)
    return vec


main()