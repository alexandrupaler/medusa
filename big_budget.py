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
    # - lots :)

    number_of_runs = 10000
    error_rate = 0.001
    goal = 0.05

    # save icm circuits and flag circuits as jsons
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

    edge_probability = 0.5
    remove_hadamards = 1.0
    for i in range(4, 7): #40+1): #the 4 is because we need i-1
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

        circuit_type, circuit_size = inp

        # fetch circuit files
        # get icm i-1 logical error rate
        icm_file_small = "circuits/icm_" + circuit_type + "_" + str(circuit_size) + ".json"
        icm_circuit_small = cirq.read_json(icm_file)
        fc_file_small = "circuits/fc_" + circuit_type + "_" + str(circuit_size) + ".json"
        flag_circuit_small = cirq.read_json(fc_file)
        # get icm and flag i logical error rate
        icm_file = "circuits/icm_" + circuit_type + "_" + str(circuit_size) + ".json"
        icm_circuit = cirq.read_json(icm_file)
        fc_file = "circuits/fc_" + circuit_type + "_" + str(circuit_size) + ".json"
        flag_circuit = cirq.read_json(fc_file)


        # TODO: the i-1 could be done elsewhere
        _, res_icm_small = run_simulation(icm_circuit_small, flag_circuit_small, error_mod, error_rate)

        res_icm = res_icm_small + 1
        # expected range is [0.4, 1.0]
        er_a = 0.4
        er_b = 1.0
        done = False
        while not done:
            error_mod = (er_a + er_b) / 2
            res, res_icm = run_simulation(icm_circuit, flag_circuit, error_mod, error_rate)
            diff = res_icm_small - res
            if abs(diff) < goal:
                done = True
            elif diff < 0:
                er_a = error_mod
            else:
                er_b = error_mod
        
        # save as csvs
        res_df = pd.DataFrame(res)
        res_icm_df = pd.DataFrame(res_icm)
        res_icm_small_df = pd.DataFrame(res_icm_small)
        res_df.to_csv("fc_" + circuit_type + "_" + circuit_size + "_" + error_mod + "_" + error_rate + ".csv",index=False)
        res_icm_df.to_csv("icm_" + circuit_type + "_" + circuit_size + "_" + error_mod + "_" + error_rate + ".csv",index=False)
        res_icm_small_df.to_csv("icm_small_" + circuit_type + "_" + circuit_size + "_" + error_mod + "_" + error_rate + ".csv",index=False)


    #circuit_sizes = range(5, 40+1)
    #circuit_types = ["adder", "b1", "b2", "b3"]

    circuit_sizes = [5, 6]
    circuit_types = ["b1"]

    paramlist = list(itertools.product(circuit_types, circuit_sizes))

    pool = Pool(processes=2)
    pool.map(parallel_simulation, paramlist)
    pool.close()
    pool.join()
