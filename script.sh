#!/bin/bash
#SBATCH --cpus-per-task 6       # The number of CPUs your code can use. For non-parallel tasks set 1. For parallel tasks see the python file for details.
#SBATCH --mem 10G               # The amount of memory you expect your code to need. Format is 10G for 10 Gigabyte, 500M for 500 Megabyte etc
#SBATCH --output=output.out     # The output file for the job
#SBATCH --time=10:00:00         # Time in HH:MM:SS or DD-HH of your job. the maximum is 120 hours or 5 days. Time needed varies based on task.
module load mamba
module load julia
source activate medusa_flaq_qubit_compiler
python main_stab_par.py