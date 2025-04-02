from pathlib import Path
from decimal import Decimal, getcontext
import shutil
import numpy as np
import pandas as pd
import os

#this script generates slurm .sh files for init branch computations

def format_using_decimal(value, precision=4):
    # Set the precision higher to ensure correct conversion
    getcontext().prec = precision + 2
    # Convert the float to a Decimal with exact precision
    decimal_value = Decimal(str(value))
    # Normalize to remove trailing zeros
    formatted_value = decimal_value.quantize(Decimal(1)) if decimal_value == decimal_value.to_integral() else decimal_value.normalize()
    return str(formatted_value)

outPath="./bashFiles_init_branch_dipole/"

if os.path.isdir(outPath):
    shutil.rmtree(outPath)
Path(outPath).mkdir(exist_ok=True,parents=True)
N=10

TVals=[5.7,5.8,5.9]
obs_name="dipole"
path_tot_for_each_T=10
def init_for_one_T(T_ind,j):
    TStr=TVals[T_ind]

    out_sub_dir=outPath+f"/init_branch/T{TStr}/"
    Path(out_sub_dir).mkdir(exist_ok=True,parents=True)
    out_file=out_sub_dir+f"/init_branch_T{TStr}_path{j}.sh"
    contents=[
        "#!/bin/bash\n",
        "#SBATCH -n 2\n",
        "#SBATCH -N 1\n",
        "#SBATCH -t 0-6:00\n",
        "#SBATCH -p hebhcnormal01\n"
        "#SBATCH --mem=1GB\n",
        f"#SBATCH -o out_init_branch_T{TStr}_path{j}.out\n",
        f"#SBATCH -e out_init_branch_T{TStr}_path{j}.err\n",
        "cd /public/home/hkust_jwliu_1/liuxi/Document/cppCode/pbc_C3_fer\n",
        f"python -u execute_branch_computation/init_branch.py {N} {TStr} {obs_name} {j} {path_tot_for_each_T}\n"
        ]
    with open(out_file,"w+") as fptr:
        fptr.writelines(contents)


for k in range(0,len(TVals)):
    for j in range(0,path_tot_for_each_T):
        init_for_one_T(k,j)