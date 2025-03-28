import re
import pickle
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys
import os
import math
from pathlib import Path
from datetime import datetime
import glob


#this script concatenates and plots U from pkl files

errFileNotExist=2

if len(sys.argv) != 3:
    print("wrong number of arguments")
    exit(1)


N = int(sys.argv[1])
TStr = sys.argv[2]

U_pkl_dir=f"./dataAll/N{N}/T{TStr}/U_dipole_dataFiles/U/"

flushEnd_vals_all=[]
file_names_all=[]
for file in glob.glob(U_pkl_dir+"/flushEnd*.pkl"):
    match_num=re.search(r"flushEnd(\d+).U",file)
    if match_num:
        file_names_all.append(file)
        flushEnd_vals_all.append(int(match_num.group(1)))

sortedInds=np.argsort(flushEnd_vals_all)

sorted_flushEnd_vals_all=[flushEnd_vals_all[ind] for ind in sortedInds]

sorted_file_names_all=[file_names_all[ind] for ind in sortedInds]

startingFileInd=0
startingFileName=sorted_file_names_all[startingFileInd]

with open(startingFileName,"rb") as fptr:
    inArrStart=pickle.load(fptr)

U_arr=inArrStart
for pkl_file in sorted_file_names_all[(startingFileInd+1):]:
    with open(pkl_file,"rb") as fptr:
        inArr=pickle.load(fptr)
    U_arr=np.append(U_arr,inArr)


plt.figure()
plt.plot(range(0,len(U_arr)),U_arr,color="black")
plt.title("U")
plt.savefig("U.png")
plt.close()
