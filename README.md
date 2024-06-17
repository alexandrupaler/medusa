# Flag Qubits 

Install
Jabalizer https://github.com/QSI-BAQS/Jabalizer.jl
Stim https://github.com/quantumlib/Stim

Python version must be 3.8+ for multiprocessing.shared_memory to work

icm_converter:
- Julia version: 1.9.0
- Author: quan-hoang
- Date: 2023-05-25

! icm_converter.jl may be incompatible with Jabalizer

- run `main.py` for simple simulation with a test circuit
- run `main_adders.py` for non-parallel simulation with different sized addition circuits
- run `main_parallel.py` for parallelized simulation with different sized addition circuits
- run `main_hadamard.py` for simulation with a logical hadamard on a surface code (WIP, no guarantee it will work)
- run `main_stabilizers.py` for simple simulation with a test circuit using stabilizer measurements
- run `main_find_flag_circuits.py` for parallelized simulation used to find optimal flag configurations for adder circuits
- run `main_stab_par.py` for parallelized simulation of adder circuits with stabilizer measurements (assumes that main_find_flag_circuits.py has been run before)

Running on Triton:
- create the environment found in `env.yml`
- install needed libraries with pip (list found in `env.yml`)
- edit the filename & number of CPUs in `script.sh` if needed
- run `script.sh`


