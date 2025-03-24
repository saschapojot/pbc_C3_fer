import numpy as np
import glob
import sys
import re
import matplotlib.pyplot as plt
from datetime import datetime
import json
import pandas as pd
import scipy.stats as stats

#This script loads avg dipole abs data, with confidence interval
if (len(sys.argv)!=2):
    print("wrong number of arguments")
    exit()

N=int(sys.argv[1])
csvDataFolderRoot=f"../dataAll/N{N}/csvOutAll/"

inCsvFile=csvDataFolderRoot+"/dipole_abs_plot.csv"

df=pd.read_csv(inCsvFile)

TVec=np.array(df["T"])

polarization_ValsAll=np.array(df["dipole_abs"])


interval_lowerValsAll=np.array(df["lower"])

interval_upperValsAll=np.array(df["upper"])

polarization_err_bar=polarization_ValsAll-interval_lowerValsAll

mask = (TVec >0)
TInds = np.where(mask)[0]
TInds=TInds[::1]

TToPlt=TVec[TInds]


#plt polarization
fig,ax=plt.subplots()
ax.errorbar(TToPlt,polarization_ValsAll[TInds],
            yerr=polarization_err_bar[TInds],fmt='o',color="black",
            ecolor='r', capsize=0.1,label='mc',
            markersize=1)

ax.set_xlabel('$T$')
ax.set_ylabel("polarization")
ax.set_title("polarization, unit cell number="+str(N**2))
plt.legend(loc="best")
# ax.set_xticks([1, 1.5,2,3, 4,5,6])

# ax.set_xticklabels(["1", "1.5", "2","3", "4","5","6"])
plt.savefig(csvDataFolderRoot+"/polarization_abs.png")
plt.close()