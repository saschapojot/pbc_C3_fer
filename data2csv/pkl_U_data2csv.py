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
# for U

if (len(sys.argv)!=2):
    print("wrong number of arguments")
    exit()

N=int(sys.argv[1])
dataRoot=f"../dataAll/N{N}/"
summary_obs_name="U"

#search directory
TVals=[]
TFileNames=[]
TStrings=[]

for TFile in glob.glob(dataRoot+"/T*"):
    # print(TFile)
    matchT=re.search(r"T([-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?)",TFile)
    if matchT:
        TFileNames.append(TFile)
        TVals.append(float(matchT.group(1)))
        TStrings.append("T"+matchT.group(1))


#sort T values
sortedInds=np.argsort(TVals)
sortedTVals=[TVals[ind] for ind in sortedInds]
sortedTFiles=[TFileNames[ind] for ind in sortedInds]
sortedTStrings=[TStrings[ind] for ind in sortedInds]


def parseSummary(oneTFolder,summary_obs_name):
    startingFileInd=-1

    lag=-1
    sweep_to_write=-1

    smrFile=oneTFolder+"/summary_"+summary_obs_name+".txt"
    summaryFileExists=os.path.isfile(smrFile)
    if summaryFileExists==False:
        return startingFileInd,-1

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



def sort_data_files_by_flushEnd(oneTFolder,summary_obs_name,varName):

    dataFolderName=oneTFolder+"/U_dipole_dataFiles/"+varName+"/"

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

def U_extract_ForOneT(oneTFolder,oneTStr,startingFileInd,lag):
    TRoot=oneTFolder
    sortedUDataFilesToRead=sort_data_files_by_flushEnd(TRoot,summary_obs_name,"U")

    startingUFileName=sortedUDataFilesToRead[startingFileInd]
    with open(startingUFileName,"rb") as fptr:
        inUStart=pickle.load(fptr)

    UVec=inUStart
    for pkl_file in sortedUDataFilesToRead[(startingFileInd+1):]:
        with open(pkl_file,"rb") as fptr:
            in_UArr=pickle.load(fptr)
            UVec=np.append(UVec,in_UArr)
    UVecSelected=UVec[::lag]

    return UVecSelected


def save_U_data(UVecSelected,oneTStr):
    outCsvDataRoot=dataRoot+"/csvOutAll/"
    outCsvFolder=outCsvDataRoot+"/"+oneTStr+"/"
    Path(outCsvFolder).mkdir(exist_ok=True,parents=True)
    outFileName="U.csv"
    outCsvFile=outCsvFolder+outFileName
    df=pd.DataFrame(UVecSelected)
    # Save to CSV
    df.to_csv(outCsvFile, index=False, header=False)



for k in range(0,len(sortedTFiles)):
    tStart=datetime.now()
    oneTFolder=sortedTFiles[k]
    oneTStr=sortedTStrings[k]
    startingfileIndTmp,lagTmp,sweep_to_writeTmp=parseSummary(oneTFolder,summary_obs_name)
    if startingfileIndTmp<0:
        print("summary file does not exist for "+oneTStr+" "+summary_obs_name)
        continue
    UVecSelected=U_extract_ForOneT(oneTFolder,oneTStr,startingfileIndTmp,lagTmp)

    save_U_data(UVecSelected,oneTStr)
    tEnd=datetime.now()
    print("processed T="+str(sortedTVals[k])+": ",tEnd-tStart)