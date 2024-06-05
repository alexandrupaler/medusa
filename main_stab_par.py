import cirq.circuits
from preparation import compiler, test_circuits, error_circuit
from evaluation import evaluate
import cirq
import numpy as np
import stimcirq
import matplotlib.pyplot as plt
from matplotlib import cm
import warnings
from multiprocessing import Pool
import itertools
from multiprocessing import Pool, shared_memory
import time
import pandas as pd



if __name__ == '__main__':

    def parallel_simulation(i):
        c = compiler.FlagCompiler()

        icm_circuit: cirq.Circuit = c.decompose_to_ICM(test_circuits.adder(i), i=i)

        """
        warnings.warn("decompose done for adder with " + str(len(list(icm_circuit.all_qubits()))) + " qubits")

        print("\n")
        print("Decompose done!")
        print("\n")

        print(icm_circuit)

        flag_circuit = c.add_flag(icm_circuit, number_of_x_flag=1, number_of_z_flag=1)

        print("\n")
        print("Flags inserted!")
        print("\n")

        """
        # "flag_circuit_adder" + str(i) + ".json"
        flag_circuit_file = "flag_circuit_adder" + str(i) + ".json"
        flag_circuit = cirq.read_json(flag_circuit_file)

        print(flag_circuit)
        
        number_of_runs = 100
        error_rates = [0.0001, 0.0002, 0.0004, 0.0008, 0.001, 0.00125, 0.0025, 0.005, 0.01]

        start = time.time()
        results, results_icm, results_rob, results_rob_icm, acceptance = evaluate.stabilizers_robustness_and_logical_error(flag_circuit, icm_circuit, number_of_runs, error_rates, True, "Adder " + str(i))
        end = time.time()
        print("time it took: " + str(end - start))

        # save as csvs
        res_df = pd.DataFrame(results)
        res_icm_df = pd.DataFrame(results_icm)
        res_rob_df = pd.DataFrame(results_rob)
        res_rob_icm_df = pd.DataFrame(results_rob_icm)
        acceptance = pd.DataFrame(acceptance)
        res_df.to_csv("results_" + str(i) + ".csv",index=False)
        res_icm_df.to_csv("results_icm_" + str(i) + ".csv",index=False)
        res_rob_df.to_csv("results_rob_" + str(i) + ".csv",index=False)
        res_rob_icm_df.to_csv("results_rob_icm_" + str(i) + ".csv",index=False)
        acceptance.to_csv("acceptance_" + str(i) + ".csv")

    paramlist = [3,4,5,6,7] #[2,3,4,5,6,7]
    error_rates = [0.0001, 0.0002, 0.0004, 0.0008, 0.001, 0.00125, 0.0025, 0.005, 0.01]
    pool = Pool()
    pool.map(parallel_simulation, paramlist)
    pool.close()
    pool.join()

    # plotting
    plt.title("Logical Error Rate, 2 Flags")
    for p in paramlist:
        results = pd.read_csv("results_" + str(p) + ".csv")
        flag_circuit_name = "adder " + str(p)
        plt.loglog(error_rates, results, label=flag_circuit_name)
    plt.xlabel('noise channel strength')
    plt.ylabel('logical error rate')
    plt.legend()
    filename = "logical_error_2_flags.png"
    plt.savefig(filename)
    plt.close()
    
    plt.title("Logical Error Rate, No Flags")
    for p in paramlist:
        results_icm = pd.read_csv("results_icm_" + str(p) + ".csv")
        icm_circuit_name = "adder " + str(p)
        plt.loglog(error_rates, results_icm, label=icm_circuit_name)
    plt.xlabel('noise channel strength')
    plt.ylabel('logical error rate')
    plt.legend()
    filename = "logical_error_no_flags.png"
    plt.savefig(filename)
    plt.close()

    plt.title("Robustness, 2 Flags")
    for p in paramlist:
        results = pd.read_csv("results_rob_" + str(p) + ".csv")
        flag_circuit_name = "adder " + str(p)
        plt.loglog(error_rates, results, label=flag_circuit_name)
    plt.xlabel('noise channel strength')
    plt.ylabel('stabilizers with errors')
    plt.legend()
    filename = "robustness_2_flags.png"
    plt.savefig(filename)
    plt.close()
    
    plt.title("Robustness, No Flags")
    for p in paramlist:
        results_icm = pd.read_csv("results_rob_icm_" + str(p) + ".csv")
        icm_circuit_name = "adder " + str(p)
        plt.loglog(error_rates, results_icm, label=icm_circuit_name)
    plt.xlabel('noise channel strength')
    plt.ylabel('stabilizers with errors')
    plt.legend()
    filename = "robustness_no_flags.png"
    plt.savefig(filename)
    plt.close()

    plt.title("Acceptance Rate")
    for p in paramlist:
        results_icm = pd.read_csv("acceptance_" + str(p) + ".csv")
        icm_circuit_name = "adder " + str(p)
        plt.semilogx(error_rates, results_icm, label=icm_circuit_name)
    plt.xlabel('noise channel strength')
    plt.ylabel('acceptance rate')
    plt.legend()
    filename = "acceptance_rate.png"
    plt.savefig(filename)
    plt.close()

