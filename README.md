In the very beginning, initialize directories:
python mk_dir.py, to set coefficients, T, and directories
##########################################
#this project uses PBC
# in this project, random seeds are set in 1 place, in ./init_run_scripts/load_previous_data.py

#
##########################################
To manually perform each step of computations
1. python launch_one_run.py ./path/to/mc.conf
2. make run_mc
3. ./run_mc ./path/to/cppIn.txt
4. python check_after_one_run_U.py ./path/to/mc.conf  startingFileIndSuggest
5. go to 1, until no more data points are needed

#########################################
To run 1 pass of mc with checking statistics of U
1. cmake .
2. make run_mc
3. python exec_checking_U.py T N startingFileIndSuggest
4. run 3 until equilibrium
5. python exec_noChecking.py T N

After checking U, one may check statistics for dipole.
1. 
To check dipole for 1 temperature:
python check_after_one_run_dipole.py ./path/to/mc.conf  startingFileIndSuggest
to check all dipoles seqentially:
python loop_check_dipoles_all_T.py N startingFileIndSuggest


#############################
after mc completes,
1. cd data2csv/
2. python pkl_U_data2csv.py N
3. python pkl_dipole_data2csv.py N

#############################
#plots
for plotting physical quantities, cd ./plt/
1. python xxx_data_csv_2_plt.py N
2. python load_csv_plt_xxx.py N

for plotting lattices and dipoles cd ./pltLattice/
1. python batch_lattice_dipole.py N
2. python batch_plt_dipoles_all_T.py N