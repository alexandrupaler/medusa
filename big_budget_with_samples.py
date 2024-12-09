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

    number_of_runs = 10000
    error_rate = 0.001
    goal = 0.005
    number_of_samples = 10 # i.e. circuit samples
    path = "bigbudget/"


    # use this to generate 10 x b1, b2 and b3 circuits

    

    def run_simulation(icm_circuit, flag_circuit, error_mod, error_rate):
        results, results_icm, _, _, _ = evaluate.stabilizers_robustness_and_logical_error(flag_circuit, icm_circuit, number_of_runs, [error_rate], False, "", "budget" + str(error_mod))
        return results, results_icm

    def parallel_simulation(inp):

        circuit_type, circuit_size = inp

        res = 0.0
        res_icm = 0.0
        res_icm_small = 0.0

        # since we multiple samples of each circuit type
        for j in range(number_of_samples):

            # fetch circuit files
            # get icm i-1 logical error rate
            icm_file_small = "circuits/icm_" + circuit_type + "_" + str(circuit_size-1) + "_" + str(j) + ".json"
            icm_circuit_small = cirq.read_json(icm_file_small)
            fc_file_small = "circuits/fc_" + circuit_type + "_" + str(circuit_size-1) + "_" + str(j) + ".json"
            flag_circuit_small = cirq.read_json(fc_file_small)
            
            # get icm and flag i logical error rate
            icm_file = "circuits/icm_" + circuit_type + "_" + str(circuit_size) + "_" + str(j) + ".json"
            icm_circuit = cirq.read_json(icm_file)
            fc_file = "circuits/fc_" + circuit_type + "_" + str(circuit_size) + "_" + str(j) + ".json"
            flag_circuit = cirq.read_json(fc_file)


            # TODO: the i-1 could be done elsewhere
            _, res_icm_small = run_simulation(icm_circuit_small, flag_circuit_small, 1, error_rate)

            # expected range is [0.0, 1.0]
            er_a = 0.0
            er_b = 1.0
            done = False
            while not done:
                error_mod = (er_a + er_b) / 2
                res, res_icm = run_simulation(icm_circuit, flag_circuit, error_mod, error_rate)
                diff = res_icm_small - res
                warnings.warn(str(diff))
                if abs(diff) < goal: #abs(diff) / res_icm_small < goal:
                    done = True
                elif diff < 0:
                    er_b = error_mod
                else:
                    er_a = error_mod

        res = res / number_of_samples
        res_icm = res_icm / number_of_samples
        res_icm_small = res_icm_small / number_of_samples
        
        # save as csvs
        res_df = pd.DataFrame(res)
        res_icm_df = pd.DataFrame(res_icm)
        res_icm_small_df = pd.DataFrame(res_icm_small)
        res_df.to_csv(path + "fc_" + circuit_type + "_" + str(circuit_size) + "_" + str(error_mod) + "_" + str(error_rate) + ".csv",index=False)
        res_icm_df.to_csv(path + "icm_" + circuit_type + "_" + str(circuit_size) + "_" + str(error_mod) + "_" + str(error_rate) + ".csv",index=False)
        res_icm_small_df.to_csv(path + "icm_small_" + circuit_type + "_" + str(circuit_size) + "_" + str(error_mod) + "_" + str(error_rate) + ".csv",index=False)

    # uncomment to generate circuit jsons
    generate_circuits(min_qubits=4, max_qubits=40, number_of_bench_samples=10)

    circuit_sizes = range(5, 40+1)
    circuit_types = ["b1", "b2", "b3"]

    paramlist = list(itertools.product(circuit_types, circuit_sizes))

    procs = len(paramlist) + 1
    pool = Pool(processes=procs)
    pool.map(parallel_simulation, paramlist)
    pool.close()
    pool.join()
