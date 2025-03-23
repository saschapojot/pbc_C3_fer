import numpy as np
import glob
import sys
import re
import matplotlib.pyplot as plt
from datetime import datetime
import json
import pandas as pd
import scipy.stats as stats

#This script loads avg U data, with confidence interval

if (len(sys.argv)!=2):
    print("wrong number of arguments")
    exit()

N=int(sys.argv[1])
csvDataFolderRoot=f"../dataAll/N{N}/csvOutAll/"

inCsvFile=csvDataFolderRoot+"/U_plot.csv"


df=pd.read_csv(inCsvFile)

TVec=np.array(df["T"])
UValsAll=np.array(df["U"])

interval_lowerValsAll=np.array(df["lower"])

interval_upperValsAll=np.array(df["upper"])


U_err_bar=UValsAll-interval_lowerValsAll
print(f"np.mean(U_err_bar)={np.mean(U_err_bar)}")
mask = (TVec <5)
TInds = np.where(mask)[0]
TInds=TInds[::1]
print(f"TInds={TInds}")
TToPlt=TVec[TInds]

# print(f"TToPlt={TToPlt}")

#plt U
fig,ax=plt.subplots()

ax.errorbar(TToPlt,UValsAll[TInds],
            yerr=U_err_bar[TInds],fmt='o',color="black",
            ecolor='r', capsize=0.1,label='mc',
            markersize=1)
# ax.scatter(TToPlt,UValsAll[TInds],marker="o",color="black",label='mc',s=1)
# ax.set_xscale("log")
ax.set_xlabel('$T$')
ax.set_ylabel("U")
ax.set_title("U per unit cell, unit cell number="+str(N**2))
plt.legend(loc="best")
# ax.set_xticks([1, 1.5,2,3, 4,5,6])

# ax.set_xticklabels(["1", "1.5", "2","3", "4","5","6"])
plt.savefig(csvDataFolderRoot+"/UPerUnitCell.png")
plt.close()