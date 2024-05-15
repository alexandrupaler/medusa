# Flag Qubits 

Install
Jabalizer https://github.com/QSI-BAQS/Jabalizer.jl
Stim https://github.com/quantumlib/Stim

Python version must be 3.8+ for multiprocessing.shared_memory to work

icm_converter:
- Julia version: 1.9.0
- Author: quan-hoang
- Date: 2023-05-25

run `main.py` for simple simulation with a test circuit
run `main_adders.py` for non-parallel simulation with different sized addition circuits
run `main_parallel.py` for parallelized simulation with different sized addition circuits
run `main._hadamard.py` for simulation with a logical hadamard on a surface code (WIP, no guarantee it will work)

