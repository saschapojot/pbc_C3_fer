import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys
import os
import math
from pathlib import Path
from datetime import datetime
#this script plots all configurations for a given T
errFileNotExist=2

if len(sys.argv) != 3:
    print("wrong number of arguments")
    exit(1)


N = int(sys.argv[1])
TStr = sys.argv[2]
csvDataFolderRoot = f"../dataAll/N{N}/csvOutAll/T{TStr}"

Px_csv_file=csvDataFolderRoot+"/Px.csv"

Py_csv_file=csvDataFolderRoot+"/Py.csv"

Qx_csv_file=csvDataFolderRoot+"/Qx.csv"

Qy_csv_file=csvDataFolderRoot+"/Qy.csv"
if not os.path.exists(Px_csv_file):
    print(f"Px does not exist for {TStr}")
    exit(errFileNotExist)


if not os.path.exists(Py_csv_file):
    print(f"Py does not exist for {TStr}")
    exit(errFileNotExist)



if not os.path.exists(Qx_csv_file):
    print(f"Qx does not exist for {TStr}")
    exit(errFileNotExist)


if not os.path.exists(Qy_csv_file):
    print(f"Qy does not exist for {TStr}")
    exit(errFileNotExist)

Px_csv_arr=np.array(pd.read_csv(Px_csv_file,header=None))
Py_csv_arr=np.array(pd.read_csv(Py_csv_file,header=None))
Qx_csv_arr=np.array(pd.read_csv(Qx_csv_file,header=None))
Qy_csv_arr=np.array(pd.read_csv(Qy_csv_file,header=None))


# Define the lattice constant
a = 2
# Instead of a flat list followed by meshgrid, generate index grids first.
# Let n0 and n1 be the integer indices corresponding to the two lattice directions.
n0 = np.arange(N)
n1 = np.arange(N)

# Use index ordering consistent with how the CSV was written
# For a triangular (non-square) lattice:
i_grid, j_grid = np.meshgrid(n0, n1, indexing="ij")
# Compute positions for sublattice A:
# The formulas below are taken from your original code.
X_O = a * i_grid - 0.5 * a * j_grid
Y_O = (np.sqrt(3) / 2) * a * j_grid

# Define the displacement for sublattice B; adjust these as needed.
D = np.array([0, np.sqrt(3) / 3 * a])
X_D = X_O + D[0]
Y_D = Y_O + D[1]

all_conf_pic_path=csvDataFolderRoot+"/all_conf/"
Path(all_conf_pic_path).mkdir(exist_ok=True,parents=True)

def plot_one_configuration(rowNum):
    print(f"plotting conf{rowNum}")
    one_Px_row=Px_csv_arr[rowNum,:]
    one_Py_row=Py_csv_arr[rowNum,:]
    one_Qx_row=Qx_csv_arr[rowNum,:]
    one_Qy_row=Qy_csv_arr[rowNum,:]

    one_Px_arr=one_Px_row.reshape((N,N)).T
    one_Py_arr=one_Py_row.reshape((N,N)).T
    one_Qx_arr=one_Qx_row.reshape((N,N)).T
    one_Qy_arr=one_Qy_row.reshape((N,N)).T
    # Compute the magnitudes for each dipole vector for sublattice A and B
    mag_A = np.sqrt(one_Px_arr**2 + one_Py_arr**2)
    mag_B = np.sqrt(one_Qx_arr**2 + one_Qy_arr**2)
    mag_min = min(mag_A.min(), mag_B.min())
    mag_max = max(mag_A.max(), mag_B.max())
    # Plot using quiver; the 5th argument is the color array.
    plt.figure(figsize=(90, 60))
    scale=0.8
    # Plot dipoles for sublattice A with a colormap for the magnitude
    qA = plt.quiver(
        X_O, Y_O,
        one_Px_arr, one_Py_arr,
        mag_A,
        cmap='viridis',
        scale=scale,
        scale_units='xy',
        angles='xy'
    )
    # Plot dipoles for sublattice B with the same colormap
    qB = plt.quiver(
        X_D, Y_D,
        one_Qx_arr, one_Qy_arr,
        mag_B,
        cmap='viridis',
        scale=scale,
        scale_units='xy',
        angles='xy'
    )

    plt.xlabel("x", fontsize=100)
    plt.ylabel("y", fontsize=100)
    plt.title(f"Dipole on each site for T = {TStr}, configuration {rowNum}", fontsize=120)
    plt.axis("equal")
    # Add colorbar from one of the quiver plots and increase number size on the colorbar.
    cbar = plt.colorbar(qA, label="Dipole Magnitude", fraction=0.046, pad=0.04)
    cbar.ax.tick_params(labelsize=120)
    plt.savefig(all_conf_pic_path+f"conf{rowNum}.png")
    plt.close()



tStart=datetime.now()

rowTotNum,_=Px_csv_arr.shape
for j in range(0,rowTotNum):
    plot_one_configuration(j)

tEnd=datetime.now()

print(f"total time: {tEnd-tStart}")

