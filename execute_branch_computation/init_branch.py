import os.path
import sys
import glob
import re
import json
from decimal import Decimal, getcontext


import numpy as np
import pickle
from pathlib import Path
import subprocess

from sympy.integrals.risch import residue_reduce_to_basic

#this script initializes the branch computation j

#this script computes the directories for data for branch computation j
# this script creates the cppIn.txt
numArgErr=4
mcErrCode=3
file_not_exist_err=7
confErrCode=8
if (len(sys.argv)!=6):
    print("wrong number of arguments.")
    exit(numArgErr)

N=int(sys.argv[1])
TStr=sys.argv[2]

obs_name=sys.argv[3]

path_num=int(sys.argv[4])

total_path_num=int(sys.argv[5])
main_computation_root_dir=f"./dataAll/N{N}/T{TStr}/"
conf_file_name=main_computation_root_dir+f"/run_T{TStr}.mc.conf"

main_computation_U_dipole_dir=main_computation_root_dir+"/U_dipole_dataFiles/"

main_computation_summary_file=main_computation_root_dir+f"summary_{obs_name}.txt"

if not os.path.exists(main_computation_summary_file):
    print(f"{main_computation_summary_file} does not exist")
    exit(file_not_exist_err)

############################################
# parse summary
with open(main_computation_summary_file,"r") as fptr:
    linesInSummaryFile= fptr.readlines()

for oneLine in linesInSummaryFile:
    matchErr=re.search(r"error",oneLine)
    #if "error" is matched
    if matchErr:
        print("error in previous computation, please re-run.")
        exit(mcErrCode)
    #if "continue" is matched
    matchContinue=re.search(r"continue",oneLine)
    if matchContinue:
        print("continue main main computation")
        exit(0)
    #if "high" is matched
    matchHigh=re.search(r"high",oneLine)
    if matchHigh:
        print("high correlation")
        exit(0)
    #the rest of the cases is "equilibrium"
    matchEq=re.search(r"equilibrium",oneLine)
    if matchEq:
        continue
    #match lag
    matchLag=re.match(r"lag\s*=\s*(\d+)",oneLine)
    if matchLag:
        lag=int(matchLag.group(1))
    #match newDataPointNum
    matchNew=re.match(r"newDataPointNum\s*=\s*(\d+)",oneLine)
    if matchNew:
        newDataPointNum=int(matchNew.group(1))


############################################

############################################
# create directories for path j

path_j_root=main_computation_root_dir+\
    f"/path_{path_num}_T{TStr}/"

Path(path_j_root).mkdir(exist_ok=True,parents=True)

path_j_Px_dir=path_j_root+"/U_dipole_dataFiles/Px/"
path_j_Py_dir=path_j_root+"/U_dipole_dataFiles/Py/"
path_j_Qx_dir=path_j_root+"/U_dipole_dataFiles/Qx/"
path_j_Qy_dir=path_j_root+"/U_dipole_dataFiles/Qy/"

Path(path_j_Px_dir).mkdir(exist_ok=True,parents=True)
Path(path_j_Py_dir).mkdir(exist_ok=True,parents=True)
Path(path_j_Qx_dir).mkdir(exist_ok=True,parents=True)
Path(path_j_Qy_dir).mkdir(exist_ok=True,parents=True)

############################################

#################################################
#parse conf, get jsonDataFromConf
confResult=subprocess.run(["python3", "./init_run_scripts/parseConf.py", conf_file_name], capture_output=True, text=True)
confJsonStr2stdout=confResult.stdout
# print(confJsonStr2stdout)
if confResult.returncode !=0:
    print("Error running parseConf.py with code "+str(confResult.returncode))
    # print(confResult.stderr)
    exit(confErrCode)
match_confJson=re.match(r"jsonDataFromConf=(.+)$",confJsonStr2stdout)
if match_confJson:
    jsonDataFromConf=json.loads(match_confJson.group(1))
else:
    print("jsonDataFromConf missing.")
    exit(confErrCode)
# print(jsonDataFromConf)

##################################################

############################################
# extract necessary data from confResult

############################################
sweep_to_write=int(jsonDataFromConf["sweep_to_write"])
# print(f"sweep_to_write={sweep_to_write}")
############################################
# copy last configurations of Px, Py, Qx, Qy
def sort_data_files_by_flushEnd(oneDir):
    dataFilesAll=[]
    flushEndAll=[]
    for oneDataFile in glob.glob(oneDir+"/flushEnd*.pkl"):
        dataFilesAll.append(oneDataFile)
        matchEnd=re.search(r"flushEnd(\d+)",oneDataFile)
        if matchEnd:
            indTmp=int(matchEnd.group(1))
            flushEndAll.append(indTmp)

    endInds=np.argsort(flushEndAll)
    sortedDataFiles=[dataFilesAll[i] for i in endInds]
    # sortedFlushEndAll=[flushEndAll[i] for i in endInds]
    return sortedDataFiles


def load_and_copy(sourceDir,destDir, component_name):
    sorted_pkl_files=sort_data_files_by_flushEnd(sourceDir)

    last_file_name=sorted_pkl_files[-1]

    with open(last_file_name,"rb") as fptr:
        last_pkl_data=np.array(pickle.load(fptr))

    last_arr=last_pkl_data.reshape((sweep_to_write,-1))

    last_row=last_arr[-1,:]

    out_file_name=destDir+f"/{component_name}_init.pkl"
    with open(out_file_name,"wb") as fptr:
        pickle.dump(last_row,fptr)





load_and_copy(main_computation_U_dipole_dir+"/Px",path_j_Px_dir,"Px")
load_and_copy(main_computation_U_dipole_dir+"/Py",path_j_Py_dir,"Py")
load_and_copy(main_computation_U_dipole_dir+"/Qx",path_j_Qx_dir,"Qx")
load_and_copy(main_computation_U_dipole_dir+"/Qy",path_j_Qy_dir,"Qy")




############################################

############################################
# create  cppIn.txt under directory Txxx/path_j_Txxx/
############################################
aStr=jsonDataFromConf["a"]
# print(f"a={aStr}")
JStr=jsonDataFromConf["J"]
# print(f"J={JStr}")
N_half_sideStr=jsonDataFromConf["N_half_side"]

# print(f"N_half_side={N_half_sideStr}")

qStr=jsonDataFromConf["q"]
# print(f"q={qStr}")
alpha1Str=jsonDataFromConf["alpha1"]
alpha2Str=jsonDataFromConf["alpha2"]
alpha3Str=jsonDataFromConf["alpha3"]
alpha4Str=jsonDataFromConf["alpha4"]
alpha5Str=jsonDataFromConf["alpha5"]
alpha6Str=jsonDataFromConf["alpha6"]
alpha7Str=jsonDataFromConf["alpha7"]
erase_data_if_exist=jsonDataFromConf["erase_data_if_exist"]
search_and_read_summary_file=jsonDataFromConf["search_and_read_summary_file"]
observable_name=obs_name
effective_data_num_required=jsonDataFromConf["effective_data_num_required"]

default_flush_num=jsonDataFromConf["default_flush_num"]
sweep_multipleStr=jsonDataFromConf["sweep_multiple"]





hStr=jsonDataFromConf["h"]

swp_multiplyStr=jsonDataFromConf["sweep_multiple"]
NStr=str(N)
newMcStepNum=lag*newDataPointNum
newFlushNum=int(np.ceil(newMcStepNum/(sweep_to_write*total_path_num)))
flushLastFile_for_branch="-1"
params2cppInFile=[
    TStr+"\n",
    aStr+"\n",
    JStr+"\n",
    NStr+"\n",
    qStr+"\n",
    alpha1Str+"\n",
    alpha2Str+"\n",
    alpha3Str+"\n",
    alpha4Str+"\n",
    alpha5Str+"\n",
    alpha6Str+"\n",
    alpha7Str+"\n",
    str(sweep_to_write)+"\n",
    str(newFlushNum)+"\n",
    flushLastFile_for_branch+"\n",
    path_j_root+"\n",
    path_j_root+"/U_dipole_dataFiles/\n",
    hStr+"\n",
    sweep_multipleStr+"\n",
    N_half_sideStr+"\n"


]

cppInParamsFileName=path_j_root+"/cppIn.txt"
with open(cppInParamsFileName,"w+") as fptr:
    fptr.writelines(params2cppInFile)