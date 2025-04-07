import numpy as np
from datetime import datetime
import sys
import re
import glob
import os
import json
from pathlib import Path
import pandas as pd
import pickle
#this script extracts effective data from pkl files
# for dipole's different computation paths

#and saves each path (main and branch separately)

if (len(sys.argv)!=3):
    print("wrong number of arguments")
    exit()


N=int(sys.argv[1])
TStr=sys.argv[2]
summary_obs_name="dipole"
dataRoot=f"../dataAll/N{N}/T{TStr}/"
data_csv_root=f"../dataAll/N{N}/csvOutAll/T{TStr}/"

def parseSummary(summary_obs_name):
    startingFileInd=-1

    lag=-1
    sweep_to_write=-1
    smrFile=dataRoot+"/summary_"+summary_obs_name+".txt"
    summaryFileExists=os.path.isfile(smrFile)
    if summaryFileExists==False:
        return startingFileInd,-1,-1
    with open(smrFile,"r") as fptr:
        lines=fptr.readlines()

    for oneLine in lines:
        #match startingFileInd
        matchStartingFileInd=re.search(r"startingFileInd=(\d+)",oneLine)

        if matchStartingFileInd:
            startingFileInd=int(matchStartingFileInd.group(1))

        #match lag
        matchLag=re.search(r"lag=(\d+)",oneLine)
        if matchLag:
            lag=int(matchLag.group(1))

        #match sweep_to_write
        match_sweep_to_write=re.search(r"sweep_to_write=(\d+)",oneLine)


        if match_sweep_to_write:
            sweep_to_write=int(match_sweep_to_write.group(1))

    return startingFileInd,lag,sweep_to_write


def sort_main_path_data_files_by_flushEnd(varName):
    dataFolderName=dataRoot+"/U_dipole_dataFiles/"+varName+"/"
    dataFilesAll=[]
    flushEndAll=[]
    for oneDataFile in glob.glob(dataFolderName+"/flushEnd*.pkl"):
        dataFilesAll.append(oneDataFile)
        matchEnd=re.search(r"flushEnd(\d+)",oneDataFile)
        if matchEnd:
            flushEndAll.append(int(matchEnd.group(1)))
    endInds=np.argsort(flushEndAll)
    sortedDataFiles=[dataFilesAll[i] for i in endInds]
    return sortedDataFiles


def sort_branch_j_data_files_by_flushEnd(varName,j):
    dataFolderName=dataRoot+f"path_{j}_T{TStr}/U_dipole_dataFiles/{varName}/"
    dataFilesAll=[]
    flushEndAll=[]
    for oneDataFile in glob.glob(dataFolderName+"/flushEnd*.pkl"):
        dataFilesAll.append(oneDataFile)
        matchEnd=re.search(r"flushEnd(\d+)",oneDataFile)
        if matchEnd:
            flushEndAll.append(int(matchEnd.group(1)))
    endInds=np.argsort(flushEndAll)
    sortedDataFiles=[dataFilesAll[i] for i in endInds]
    return sortedDataFiles


def main_path_one_dipole_component_extract_ForOneT(startingFileInd,lag,component_name,sweep_to_write):

    sorted_main_path_one_component_DataFilesToRead=sort_main_path_data_files_by_flushEnd(component_name)


    one_component_StaringFileName=sorted_main_path_one_component_DataFilesToRead[startingFileInd]

    with open(one_component_StaringFileName,"rb") as fptr:
        one_component_inArrStart=np.array(pickle.load(fptr))

    one_component_Arr=one_component_inArrStart.reshape((sweep_to_write,-1))

    #read the rest of one_v pkl files
    for pkl_file in sorted_main_path_one_component_DataFilesToRead[(startingFileInd+1):]:
        with open(pkl_file,"rb") as fptr:
            one_component_inArr=np.array(pickle.load(fptr))
            one_component_inArr=one_component_inArr.reshape((sweep_to_write,-1))
            one_component_Arr=np.concatenate((one_component_Arr,one_component_inArr),axis=0)

    one_component_ArrSelected=one_component_Arr[::lag,:]
    return one_component_ArrSelected


def branch_path_j_one_dipole_component_extract_ForOneT(lag,component_name,sweep_to_write,j):
    sortedDataFiles_path_j=sort_branch_j_data_files_by_flushEnd(component_name,j)

    one_component_StaringFileName_path_j=sortedDataFiles_path_j[0]
    with open(one_component_StaringFileName_path_j,"rb") as fptr:
        one_component_inArrStart_path_j=np.array(pickle.load(fptr))

    one_component_Arr_path_j=one_component_inArrStart_path_j.reshape((sweep_to_write,-1))
    #read the rest of  pkl files
    for pkl_file in sortedDataFiles_path_j[1:]:
        with open(pkl_file,"rb") as fptr:
            one_component_inArr_path_j=np.array(pickle.load(fptr))
            one_component_inArr_path_j=one_component_inArr_path_j.reshape((sweep_to_write,-1))
            one_component_Arr_path_j=np.concatenate((one_component_Arr_path_j,one_component_inArr_path_j),axis=0)

    one_component_ArrSelected_path_j=one_component_Arr_path_j[lag::lag,:]#has at least distance lag with the data in main path
    return one_component_ArrSelected_path_j


def search_all_branch_paths_num():
    path_folder_name_vec=[]
    for folder in glob.glob(dataRoot+"/path*"):
        path_folder_name_vec.append(folder)
    return len(path_folder_name_vec)


def save_oneComponent_dipole_data(one_component_ArrSelected,component_name,path_name):
    """

    :param one_component_ArrSelected:
    :param component_name:
    :param path_name: main or path j
    :return:
    """
    outCsvFolder=data_csv_root+f"/separate_data/{path_name}/"
    Path(outCsvFolder).mkdir(exist_ok=True,parents=True)
    outFileName=f"{component_name}.csv"
    outCsvFile=outCsvFolder+outFileName
    df=pd.DataFrame(one_component_ArrSelected)
    # Save to CSV
    print(f"saving {outCsvFile}")
    df.to_csv(outCsvFile, index=False, header=False)

tStart=datetime.now()
#save data from main path
startingfileInd,lag,sweep_to_write=parseSummary(summary_obs_name)
if startingfileInd<0:
    print("summary file does not exist for "+TStr+" "+summary_obs_name)
    exit(1)

components_all=["Px","Py","Qx","Qy"]
path_name_main="path_main"

for component_name in components_all:
    one_component_ArrSelected_from_main= main_path_one_dipole_component_extract_ForOneT(startingfileInd,lag,component_name,sweep_to_write)
    save_oneComponent_dipole_data(one_component_ArrSelected_from_main,component_name,path_name_main)


branch_path_num=search_all_branch_paths_num()
for j in range(0,branch_path_num):
    path_j_name=f"path_{j}"
    for component_name in components_all:
        one_comp_arr_selected_from_path_j=branch_path_j_one_dipole_component_extract_ForOneT(lag,component_name,sweep_to_write,j)
        save_oneComponent_dipole_data(one_comp_arr_selected_from_path_j,component_name,path_j_name)



tEnd=datetime.now()

print(f"total time:", tEnd-tStart)