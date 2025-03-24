import subprocess
import signal
import sys
import os
import re
import glob
from datetime import datetime
import numpy as np

#this script executes load_csv_oneT_dipole.py

if len(sys.argv) != 2:
    print("wrong number of arguments")
    sys.exit(1)

N = int(sys.argv[1])
dataRoot = f"../dataAll/N{N}/csvOutAll/"

avg_polarization_dir=dataRoot+"/avg_polarization/"
dipole_each_site_dir=dataRoot+"/dipole_each_site/"
# Create the directory if it doesn't exist
if not os.path.exists(avg_polarization_dir):
    try:
        os.makedirs(avg_polarization_dir)
        print(f"Directory '{avg_polarization_dir}' created successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")
else:
    print(f"Directory '{avg_polarization_dir}' already exists.")


# Create the directory if it doesn't exist
if not os.path.exists(dipole_each_site_dir):
    try:
        os.makedirs(dipole_each_site_dir)
        print(f"Directory '{dipole_each_site_dir}' created successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")
else:
    print(f"Directory '{dipole_each_site_dir}' already exists.")
# search directory
TVals = []
TFileNames = []
TStrings = []

for TFile in glob.glob(os.path.join(dataRoot, "T*")):
    matchT = re.search(r"T([-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?)", TFile)
    if matchT:
        TFileNames.append(TFile)
        TVals.append(float(matchT.group(1)))
        TStrings.append(matchT.group(1))

# sort T values
sortedInds = np.argsort(TVals)
sortedTVals = [TVals[ind] for ind in sortedInds]
sortedTFiles = [TFileNames[ind] for ind in sortedInds]
sortedTStrings = [TStrings[ind] for ind in sortedInds]
tStart = datetime.now()

# Function to terminate the subprocess
def terminate_process(proc):
    try:
        # Terminate the whole process group
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        print(f"Terminated subprocess with PID {proc.pid}")
    except Exception as e:
        print(f"Error terminating subprocess with PID {proc.pid}: {e}")


try:
    for k in range(len(sortedTFiles)):

        oneTStr = sortedTStrings[k]
        print(f"Running subprocess for {oneTStr}")

        # Start subprocess in a new session (process group)
        stats_process = subprocess.Popen(
            ["python3", "-u", "load_csv_oneT_dipole.py", f"{N}",oneTStr, str(k)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True  # This makes it easier to kill the process group
        )

        try:
            # Read standard output line by line
            while True:
                output = stats_process.stdout.readline()
                if output == '' and stats_process.poll() is not None:
                    break
                if output:
                    print(output.strip())

        except KeyboardInterrupt:
            print("KeyboardInterrupt detected. Terminating current subprocess...")
            terminate_process(stats_process)
            sys.exit(1)

        # Final communication in case there's remaining output
        stdout, stderr = stats_process.communicate()
        if stdout:
            print(stdout.strip())
        if stderr:
            print(stderr.strip())

except KeyboardInterrupt:
    # If a KeyboardInterrupt occurs outside of the inner loop, ensure all running subprocesses are terminated.
    print("KeyboardInterrupt detected in the main loop. Exiting.")
    sys.exit(1)

tEnd = datetime.now()
print(f"total time:{ tEnd-tStart}")