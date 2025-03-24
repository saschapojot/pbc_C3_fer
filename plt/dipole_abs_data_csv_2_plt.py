import numpy as np
import glob
import sys
import re
import matplotlib.pyplot as plt
from datetime import datetime
import json
import pandas as pd
import scipy.stats as stats
import os

#This script loads csv data and plot P+Q, with confidence interval
if (len(sys.argv)!=2):
    print("wrong number of arguments")
    exit()

N=int(sys.argv[1])
csvDataFolderRoot=f"../dataAll/N{N}/csvOutAll/"

TVals=[]
TFileNames=[]
for TFile in glob.glob(csvDataFolderRoot+"/T*"):

    matchT=re.search(r"T([-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?)",TFile)
    # if float(matchT.group(1))<1:
    #     continue

    if matchT:
        TFileNames.append(TFile)
        TVals.append(float(matchT.group(1)))

sortedInds=np.argsort(TVals)
sortedTVals=[TVals[ind] for ind in sortedInds]
sortedTFiles=[TFileNames[ind] for ind in sortedInds]

TVals_to_csv=[]
def vec_estimator(vec):
    avg_vec=np.mean(vec)
    return avg_vec


def vec_jackknife(vec):
    n=len(vec)
    jackknife_samples = np.zeros(n)
    for i  in range(0,n):
        sample_vec=np.delete(vec,i)
        jackknife_samples[i]=vec_estimator(sample_vec)
    # Jackknife estimate of the statistic
    jackknife_estimate = np.mean(jackknife_samples)
    variance_estimate = (n - 1) / n * np.sum((jackknife_samples - jackknife_estimate) ** 2)

    return jackknife_estimate, variance_estimate


def vec_confidence_interval(vec,confidence_level=0.95):
    jackknife_estimate, jackknife_variance=vec_jackknife(vec)

    n=len(vec)
    alpha = 1 - confidence_level
    t_critical = stats.t.ppf(1 - alpha / 2, df=n-1)
    # Calculate the standard error
    standard_error = np.sqrt(jackknife_variance)
    # Calculate the confidence interval
    ci_lower = jackknife_estimate - t_critical * standard_error
    ci_upper = jackknife_estimate + t_critical * standard_error
    return jackknife_estimate,ci_lower, ci_upper

def generate_one_point_dipole_abs(oneTFile):
    matchT=re.search(r'T([-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?)',oneTFile)
    TVal=float(matchT.group(1))

    Px_path=oneTFile+"/Px.csv"
    Py_path=oneTFile+"/Py.csv"
    Qx_path=oneTFile+"/Qx.csv"
    Qy_path=oneTFile+"/Qy.csv"
    if not (os.path.exists(Px_path) and os.path.isfile(Px_path)):
        return [None,None,None]

    df_Qx=np.array(pd.read_csv(Qx_path,header=None))
    df_Qy=np.array(pd.read_csv(Qy_path,header=None))

    df_Px=np.array(pd.read_csv(Px_path,header=None))
    df_Py=np.array(pd.read_csv(Py_path,header=None))

    df_dipole_x=df_Px+df_Qx
    df_dipole_y=df_Py+df_Qy

    dipole_x_avg_vec=np.mean(df_dipole_x,axis=1)
    dipole_y_avg_vec=np.mean(df_dipole_y,axis=1)

    dipole_abs_vec=np.sqrt(dipole_x_avg_vec**2+dipole_y_avg_vec**2)
    print(f"T={TVal}, data num={len(dipole_abs_vec)}")
    jackknife_estimate,ci_lower, ci_upper=vec_confidence_interval(dipole_abs_vec)

    return [jackknife_estimate,ci_lower, ci_upper]
tStart=datetime.now()
dipole_abs_valsAll=[]
interval_lowerValsAll=[]
interval_upperValsAll=[]
for k in range(0,len(sortedTFiles)):
    oneTFile=sortedTFiles[k]

    jackknife_estimate,ci_lower, ci_upper=generate_one_point_dipole_abs(oneTFile)
    if jackknife_estimate==None:
        continue
    dipole_abs_valsAll.append(jackknife_estimate)
    interval_lowerValsAll.append(ci_lower)
    interval_upperValsAll.append(ci_upper)
    TVals_to_csv.append(sortedTVals[k])

df=pd.DataFrame(
    {
        "T":TVals_to_csv,
        "dipole_abs":np.array(dipole_abs_valsAll),
        "lower":interval_lowerValsAll,
        "upper":interval_upperValsAll
    }
)

csv_file_name=csvDataFolderRoot+"dipole_abs_plot.csv"

df.to_csv(csv_file_name,index=False)

tEnd=datetime.now()

print(f"time: {tEnd-tStart}")