import numpy as np 
from scipy.spatial import cKDTree
import arepo_utils as ar
import h5py 
import os 
from pathlib import Path
import sys

def nearest_part():
	#load low res particle and set up kdtree
	part_pos_low = read_snap(loc_snap,'/PartType2/Coordinates')
	part_pos_low = np.append(part_pos_low,read_snap(loc_snap,'/PartType3/Coordinates'),axis=0)
	kdtree_low = cKDTree(part_pos_low,boxsize = lbox)

	dist_low, _ = kdtree_low.query(cop_sample,k=1)

	return()

def create_hdf5(loc,loc_output,snap_num):
	#funciton to create file that coppies structure of subfind hdf5 files
	Path(loc_output+'groups_%03d'%snap_num).mkdir(parents=True, exist_ok=True)
	if os.path.isfile(loc_output+'groups_%03d/fof_subhalo_additional_%03d.0.hdf5'%(snap_num,snap_num)):
		print('File exists')
		return(1)

	#file to write additional data
	try:
		f = h5py.File(loc_output+'groups_%03d/fof_subhalo_additional_%03d.0.hdf5'%(snap_num,snap_num), 'a')
	except PermissionError:
		print('Cannot create hdf5 file')
		return(-1)

	#file to copy header
	f_head = h5py.File(loc+'groups_%03d/fof_subhalo_tab_%03d.0.hdf5'%(snap_num,snap_num), 'r')

	f.create_group("Config")
	f.create_group("Group")
	f.create_group("Header")
	f.create_group("IDs")
	f.create_group("Parameters")
	f.create_group("Subhalo")



	for j in f_head['Header'].attrs.keys():
		f['Header'].attrs[j] = f_head['Header'].attrs[j]
	for j in f_head['Parameters'].attrs.keys():
		f['Parameters'].attrs[j] = f_head['Parameters'].attrs[j]

	f['Header'].attrs['Ngroups_ThisFile'] = f['Header'].attrs['Ngroups_Total']
	f['Header'].attrs['Nsubgroups_ThisFile'] = f['Header'].attrs['Nsubgroups_Total']
	f['Header'].attrs['Nids_ThisFile'] = f['Header'].attrs['Nids_Total']
	f['Header'].attrs['NumFiles'] = 1

	return(0)

def rename_hdf5(loc, snap_num):
	#funciton to create file that coppies structure of subfind hdf5 files

	print(loc,snap_num)
	#file to write additional data
	f = h5py.File(loc+'groups_%03d/fof_subhalo_additional_%03d.0.hdf5'%(snap_num,snap_num), 'a')

	del f['Group/GroupContamination_radius']
	f['Group/GroupContamination_radius'] = f['Group/Contamination_radius']
	del f['Group/Contamination_radius']
	
	return()

def add_element(loc,name,data):
	f = h5py.File(loc, 'a')

	if name in f.keys():
		del f[name]
	f.create_dataset(name, data=data)
	f.close()


def process(loc, snap_num, check_ran=True):

	#skip if group folder not already there
	print(loc,snap_num)
	if os.path.isdir(loc+'groups_%03d'%snap_num) == False:
		return()

	file_hdf = loc+'groups_%03d/fof_subhalo_additional_%03d.0.hdf5'%(snap_num,snap_num)

	#create hdf5 file, if not there
	out = create_hdf5(loc, loc, snap_num)

	#skip if file already exists or unable to create file
	if out==-1:
		return()
	if out==1:
		return()

	#skip if contamination radius already calculated
	h = h5.File(file_hdf,'r')
	if ('GroupContamination_radius' in h['Group'].keys()) & (check_ran):
		print('Contaimation radius already calculated')
		h.close()
		return()
	h.close()

	#load fof group positions
	sf = ar.gadget_subfind.load_subfind(snap_num, dir=loc,loadonly=data_keys,cosmological=False)

	#skip if there are no groups
	if sf.totngroups==0:
		return()

	#load low res particles
	sim = ar.gadget_snap.gadget_snapshot(loc+'snapdir_%03d/snapshot_%03d'%(snap_num,snap_num),loadonly=['pos'],loadonlytype=[2,3],hdf5=True,applytransformationfacs=False)
	
	kdtree_low = cKDTree(sim.data['pos'])
	dist_low, _ = kdtree_low.query(sf.data['fpos'],k=1)
	
	add_element(file_hdf,'Group/GroupContamination_radius',dist_low)
	return()


if __name__== '__main__':

	loc = sys.argv[1] 
	snap_num = sys.argv[2]
	process(loc, snap_num)




