import cirq.circuits
import cirq
import matplotlib.pyplot as plt
import warnings
import pandas as pd
from multiprocessing import Pool
from preparation import compiler, test_circuits
from evaluation import evaluate
import numpy as np



if __name__ == '__main__':

    # triton cpus:
    # - 6

    error_rates = [0.0001, 0.0002, 0.0004, 0.0008, 0.001, 0.00125, 0.0025, 0.005, 0.01]
    number_of_runs = 10000

    def parallel_simulation(b):

        # fix adder size 
        i = 3

        c = compiler.FlagCompiler()

        icm_circuit: cirq.Circuit = c.decompose_to_ICM(test_circuits.adder_only_cnots(i), i=i)
        flag_circuit = c.add_flag(icm_circuit, strategy="heuristic")
        
        results, results_icm, _, _, _ = evaluate.stabilizers_robustness_and_logical_error(flag_circuit, icm_circuit, number_of_runs, error_rates, False, "", "budget" + str(b))

        # save as csvs
        res_df = pd.DataFrame(results)
        res_icm_df = pd.DataFrame(results_icm)
        res_df.to_csv("results_" + str(b) + ".csv",index=False)
        res_icm_df.to_csv("results_icm_" + str(b) + ".csv",index=False)

    paramlist = [0.01, 0.05, 0.1, 0.5, 1]
    pool = Pool()
    pool.map(parallel_simulation, paramlist)
    pool.close()
    pool.join()

    # plotting
    
    plt.title("Budget Behavior Test, Flag Adder 3")
    for p in paramlist:
        results = pd.read_csv("results_" + str(p) + ".csv")
        circuit_name = "mod value: " + str(p)
        plt.loglog(error_rates, results, label=circuit_name)

        #results = pd.read_csv("results_icm_" + str(p) + ".csv")
        #circuit_name = "Icm adder 5" + str(p)
        #plt.loglog(error_rates, results, label=circuit_name)

    plt.xlabel('noise channel strength')
    plt.ylabel('logical error rate')
    plt.legend()
    filename = "budgets.png"
    plt.savefig(filename)
    plt.close()