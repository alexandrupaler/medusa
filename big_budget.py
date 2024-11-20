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


if __name__ == '__main__':

    # triton cpus:
    # - 945 :)

    def save_circuit_info(name, icm_circuit, i):
        c = compiler.FlagCompiler()
        #icm_circuit: cirq.Circuit = c.decompose_to_ICM(icm_circuit, i=i)
        flag_circuit = c.add_flag(icm_circuit, strategy="heuristic")

        icm_json = cirq.to_json(icm_circuit)
        with open("circuits/icm_" + name + "_" + str(i) + ".json", "w") as outfile:
            outfile.write(icm_json)

        fc_json = cirq.to_json(flag_circuit)
        with open("circuits/fc_" + name + "_" + str(i) + ".json", "w") as outfile:
            outfile.write(fc_json)

    # first save icm circuits and flag circuits
    edge_probability = 0.5
    remove_hadamards = 1.0
    for i in range(5, 7): #40+1):
        print(i)
        adder = test_circuits.adder_only_cnots(i)
        b1 = test_circuits.circuit_generator_1(i, edge_probability, remove_hadamards)
        b2 = test_circuits.circuit_generator_2(i, edge_probability, remove_hadamards)
        b3 = test_circuits.circuit_generator_3(i, edge_probability, remove_hadamards)
        save_circuit_info("adder", adder, i)
        save_circuit_info("b1", b1, i)
        save_circuit_info("b2", b2, i)
        save_circuit_info("b3", b3, i)


    def run_simulation(icm_circuit, flag_circuit, error_mod, error_rate):
        c = compiler.FlagCompiler()
        results, results_icm, _, _, _ = evaluate.stabilizers_robustness_and_logical_error(flag_circuit, icm_circuit, number_of_runs, [error_rate], False, "", "budget" + str(error_mod))
        return results, results_icm

    def parallel_simulation(inp):

        a, error_rate = inp
        b, error_mod = a
        circuit_type, circuit_size = b

        # fetch circuits
        icm_file = "circuits/icm_" + circuit_type + "_" + str(circuit_size) + ".json"
        icm_circuit = cirq.read_json(icm_file)

        fc_file = "circuits/fc_" + circuit_type + "_" + str(circuit_size) + ".json"
        flag_circuit = cirq.read_json(fc_file)

        res, res_icm = run_simulation(icm_circuit, flag_circuit, error_mod, error_rate)
        
        # save as csvs
        res_df = pd.DataFrame(res)
        res_icm_df = pd.DataFrame(res_icm)
        res_df.to_csv("fc_" + circuit_type + "_" + circuit_size + "_" + error_mod + "_" + error_rate + ".csv",index=False)
        res_icm_df.to_csv("icm_" + circuit_type + "_" + circuit_size + "_" + error_mod + "_" + error_rate + ".csv",index=False)


    #circuit_sizes = range(5, 40+1)
    #circuit_types = ["adder", "b1", "b2", "b3"]
    #error_mods = [0.01, 0.05, 0.1, 0.5, 1]
    #error_rates = [0.0001, 0.0002, 0.0004, 0.0008, 0.001, 0.00125, 0.0025, 0.005, 0.01]

    circuit_sizes = [5]
    circuit_types = ["b1"]
    error_mods = [1]
    error_rates = [0.0001, 0.01]

    # circuit_type, circuit_size, error_mod, error_rate = inp
    paramlist = list(itertools.product(circuit_types, circuit_sizes))
    paramlist = list(itertools.product(paramlist, error_mods))
    paramlist = list(itertools.product(paramlist, error_rates))
    print(paramlist)

    number_of_runs = 10000
    pool = Pool(processes=2)
    pool.map(parallel_simulation, paramlist)
    pool.close()
    pool.join()
