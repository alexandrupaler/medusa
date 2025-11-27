# Medusa: Lowering the Cost of Fault-Tolerance by Trading QECC for Flags

**Notes**:
- Python version must be 3.8+ for multiprocessing.shared_memory to work
- `Qualtran` https://github.com/quantumlib/Qualtran version must be 0.3.0
- `Jabalizer` https://github.com/QSI-BAQS/Jabalizer.jl
- `Stim` https://github.com/quantumlib/Stim
- icm_converter.jl may be incompatible with some versions of Jabalizer

**Files**:
- `triton_main_budget_again.py` 
- `triton_main_error_mod.py`
- `triton_main_history_again.py`

**Running on Triton**:
- create the environment found in `env.yml`
- install needed libraries with pip (list found in `env.yml`)
- edit the filename & number of CPUs in `script.sh` if needed
- run `script.sh`


**This research was performed in part with funding from the Defense Advanced Research Projects Agency [under the Quantum Benchmarking (QB) program under award no. HR00112230006 and HR001121S0026 contracts].**
