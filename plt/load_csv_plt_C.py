import numpy as np
import glob
import sys
import re
import matplotlib.pyplot as plt
from datetime import datetime
import json
import pandas as pd
import scipy.stats as stats

#This script loads avg C data, with confidence interval


if (len(sys.argv)!=2):
    print("wrong number of arguments")
    exit()

N=int(sys.argv[1])
csvDataFolderRoot=f"../dataAll/N{N}/csvOutAll/"

inCsvFile=csvDataFolderRoot+"/C_plot.csv"

df=pd.read_csv(inCsvFile)

TVec=np.array(df["T"])
CValsAll=np.array(df["C"])

interval_lowerValsAll=np.array(df["lower"])


interval_upperValsAll=np.array(df["upper"])

C_err_bar=CValsAll-interval_lowerValsAll

mask = (TVec>0.9)
TInds = np.where(mask)[0]
TInds=TInds[::1]
# print(f"TInds={TInds}")
TToPlt=TVec[TInds]

#plt C
fig,ax=plt.subplots()

ax.errorbar(TToPlt,CValsAll[TInds],
            yerr=C_err_bar[TInds],fmt='o',color="blue",
            ecolor='magenta', capsize=0.1,label='mc',
            markersize=1)

# ax.set_xscale("log")
ax.set_xlabel('$T$')
ax.set_ylabel("C")
ax.set_title("C per unit cell, unit cell number="+str(N**2))
plt.legend(loc="best")
# ax.set_xticks([1, 1.5,2,3, 4,5])

# ax.set_xticklabels(["1", "1.5", "2","3", "4","5"])
plt.savefig(csvDataFolderRoot+"/CPerUnitCell.png")
plt.close()