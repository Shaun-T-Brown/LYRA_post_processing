import numpy as np 
import h5py as h5

def most_massive_branch(loc):

    h=h5.File(loc,'r')
    ID=np.array(h['haloTrees/nodeIndex'])
    Main_prog=np.array(h['haloTrees/mainProgenitorIndex'])
    desc_ind=np.array(h['haloTrees/descendantIndex'])
    mass=np.array(h['haloTrees/nodeMass'])
    snap_num = np.array(h['haloTrees/snapshotNumber'])

    ID_orig = np.copy(ID)
    sort = np.argsort(ID)
    ID = ID[sort]
    Main_prog = Main_prog[sort]
    desc_ind = desc_ind[sort]
    mass = mass[sort]
    snap_num = snap_num[sort]

  

    h.close()
    mass_branch = np.zeros(len(ID))
    ID_end_node = ID[Main_prog==-1]


    for i in tqdm(range(len(ID_end_node))):
        
        descendent=ID_end_node[i]
        mass_tally=0.0
        while descendent != 0:
            if descendent==-1:
                break

            ind = np.searchsorted(ID,descendent)

            mass_tally+=mass[ind]
            mass_branch[ind] +=mass_tally
            descendent = desc_ind[ind]
    


    #reverse sorting of array
    mass_branch_dummy = np.zeros(len(ID))
    mass_branch_dummy[sort] = mass_branch

    

    #append data to file
    try:
        g=h5.File(loc,'a')
        g.create_dataset('haloTrees/branchMass',data=mass_branch_dummy)
        g.close()
    except ValueError:
        g=h5.File(loc,'r+')
        del g['haloTrees/branchMass']
        g.create_dataset('haloTrees/branchMass',data=mass_branch_dummy)
        g.close()

    return


if __name__== '__main__':

	loc = sys.argv[1] 
	most_massive_branch(loc)