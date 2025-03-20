In the very beginning, initialize directories:
python mk_dir.py, to set coefficients, T, and directories
##########################################
#this project uses PBC
##########################################
To manually perform each step of computations
1. python launch_one_run.py ./path/to/mc.conf
2. make run_mc
3. ./run_mc ./path/to/cppIn.txt
4. python check_after_one_run.py ./path/to/mc.conf lastFileNum
5. go to 1, until no more data points are needed

#########################################
To run 1 pass of mc with checking statistics
1. cmake .
2. make run_mc
3. python exec_checking.py T N lastFileNum
4. run 3 until equilibrium
5. python exec_noChecking.py T N


#############################
after mc completes,
1. cd data2csv/
2. python pkl_U_dipole_data2csv.py N