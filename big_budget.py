import cirq.circuits
import cirq
import matplotlib.pyplot as plt
import warnings
import pandas as pd
import itertools
from multiprocessing import Pool
from preparation import compiler, test_circuits
from evaluation import evaluate
import numpy as np

from generator_utils import generate_circuits


if __name__ == '__main__':

    # triton cpus:
    # - lots :)

    number_of_runs = 10
    error_rate = 0.001
    epsilon_target = 0.005
    
    def run_simulation(icm_circuit, flag_circuit, error_mod, error_rate):
        results, results_icm, _, _, _ = evaluate.stabilizers_robustness_and_logical_error(flag_circuit, icm_circuit, number_of_runs, [error_rate], False, "", "budget" + str(error_mod))
        return results, results_icm

    def parallel_simulation(inp):

        circuit_type, circuit_size = inp

        # fetch circuit files
        # get icm i-1 logical error rate
        small_icm_fname = "circuits/icm_" + circuit_type + "_" + str(circuit_size-1) + ".json"
        small_icm = cirq.read_json(small_icm_fname)
        small_fc_fname = "circuits/fc_" + circuit_type + "_" + str(circuit_size-1) + ".json"
        small_fc = cirq.read_json(small_fc_fname)
        
        # get icm and flag i logical error rate
        large_icm_fname = "circuits/icm_" + circuit_type + "_" + str(circuit_size) + ".json"
        large_icm = cirq.read_json(large_icm_fname)
        large_fc_fname = "circuits/fc_" + circuit_type + "_" + str(circuit_size) + ".json"
        large_fc = cirq.read_json(large_fc_fname)


        # TODO: the i-1 could be done elsewhere
        _, small_icm_failure_rate = run_simulation(small_icm, small_fc, 1, error_rate)

        # expected range is [0.3, 1.0]
        er_a = 0.3
        er_b = 1.0

        done = False
        while not done:
            error_mod = (er_a + er_b) / 2
            large_fc_failure_rate, large_icm_failure_rate = run_simulation(large_icm, large_fc, error_mod, error_rate)

            diff = small_icm_failure_rate - large_fc_failure_rate
            warnings.warn(str(diff))

            if abs(diff) < epsilon_target: #abs(diff) / res_icm_small < goal:
                done = True
            elif diff < 0:
                er_b = error_mod
            else:
                er_a = error_mod
        
        # save as csvs
        res_df = pd.DataFrame(large_fc_failure_rate)
        res_icm_df = pd.DataFrame(large_icm_failure_rate)
        res_icm_small_df = pd.DataFrame(small_icm_failure_rate)
        res_df.to_csv("bigbudget/fc_" + circuit_type + "_" + str(circuit_size) + "_" + str(error_mod) + "_" + str(error_rate) + ".csv",index=False)
        res_icm_df.to_csv("bigbudget/icm_" + circuit_type + "_" + str(circuit_size) + "_" + str(error_mod) + "_" + str(error_rate) + ".csv",index=False)
        res_icm_small_df.to_csv("bigbudget/icm_small_" + circuit_type + "_" + str(circuit_size) + "_" + str(error_mod) + "_" + str(error_rate) + ".csv",index=False)


    # uncomment to generate circuit jsons
    generate_circuits(min_qubits=4, max_qubits=40, number_of_bench_samples=1)

    circuit_sizes = range(5, 40+1)
    #circuit_types = ["adder", "b1", "b2", "b3"]
    circuit_types = ["b1", "b2", "b3"]

    paramlist = list(itertools.product(circuit_types, circuit_sizes))

    procs = len(paramlist) + 1

    # max number of processes
    maxprocs = 4
    pool = Pool(processes=procs)
    pool.map(parallel_simulation, paramlist)
    pool.close()
    pool.join()
