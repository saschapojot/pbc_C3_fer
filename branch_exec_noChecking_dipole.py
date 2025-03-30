import subprocess
from decimal import Decimal, getcontext
import signal
import sys

#this script executes computation in a branch path,
#after the dipole reaches equilibrium
# without checking statistics

def format_using_decimal(value, precision=15):
    # Set the precision higher to ensure correct conversion
    getcontext().prec = precision + 2
    # Convert the float to a Decimal with exact precision
    decimal_value = Decimal(str(value))
    # Normalize to remove trailing zeros
    formatted_value = decimal_value.quantize(Decimal(1)) if decimal_value == decimal_value.to_integral() else decimal_value.normalize()
    return str(formatted_value)

if (len(sys.argv)!=5):
    print("wrong number of arguments")
    exit()

N=int(sys.argv[1])

T=float(sys.argv[2])
TStr=format_using_decimal(T)
branch_path_ind=int(sys.argv[3])

total_branch_num=int(sys.argv[4])

cppInPath=f"./dataAll/N{N}/T{TStr}/path_{branch_path_ind}_T{TStr}/cppIn.txt"

#############################################
#run executable
# Function to handle the termination of the subprocess on SIGINT
cppExecutable="./run_mc"
cpp_process = subprocess.Popen(
    [cppExecutable, cppInPath],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

def terminate_process(signal_number, frame):
    print("Terminating subprocess...")
    cpp_process.terminate()
    cpp_process.wait()  # Wait for the subprocess to properly terminate
    sys.exit(0)  # Exit the script

# Register the signal handler
signal.signal(signal.SIGINT, terminate_process)
# Read output line by line in real-time
try:
    for line in iter(cpp_process.stdout.readline, ''):
        print(line.strip())

    # Wait for the process to finish and get the final output
    stdout, stderr = cpp_process.communicate()

    # Print any remaining output
    if stdout:
        print(stdout.strip())
    if stderr:
        print(stderr.strip())
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # Ensure the subprocess is terminated if the script exits unexpectedly
    cpp_process.terminate()
    cpp_process.wait()

#############################################