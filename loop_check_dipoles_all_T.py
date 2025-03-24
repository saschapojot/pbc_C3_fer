import numpy as np
from datetime import datetime
import sys
import re
import subprocess
import glob
import os
import json
from pathlib import Path
import pandas as pd
import pickle


#this script checks dipoles for each T sequentially

if (len(sys.argv)!=3):
    print("wrong number of arguments")
    exit()

N=int(sys.argv[1])
dataRoot=f"./dataAll/N{N}/"
startingFileIndSuggest=int(sys.argv[2])
print(f"startingFileIndSuggest={startingFileIndSuggest}")
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
        TStrings.append( matchT.group(1))

#sort T values
sortedInds=np.argsort(TVals)
sortedTVals=[TVals[ind] for ind in sortedInds]
sortedTFiles=[TFileNames[ind] for ind in sortedInds]
sortedTStrings=[TStrings[ind] for ind in sortedInds]


##################################
#loop check
for k in range(0,len(sortedInds)):
    TStr=sortedTStrings[k]
    check_process=subprocess.run(["python3","check_after_one_run_dipole.py", \
                                  f"./dataAll/N{N}/T{TStr}/run_T{TStr}.mc.conf",str(startingFileIndSuggest)])

    # print(check_process.stdout)
    if check_process.returncode!=0:
        print(f"check_process error code: {check_process.returncode} for {TStr}")
