import cirq.circuits
import cirq
import matplotlib.pyplot as plt
import warnings
import time
import pandas as pd
from multiprocessing import Pool
from preparation import compiler, test_circuits
from evaluation import evaluate



if __name__ == '__main__':

    # triton cpus:
    # - 10

    i = 3

    c = compiler.FlagCompiler()

    icm_circuit: cirq.Circuit = c.decompose_to_ICM(test_circuits.adder(i), i=i)

    # warning because triton
    warnings.warn("decompose done for adder with " + str(len(list(icm_circuit.all_qubits()))) + " qubits")

    flag_circuit_file = "results_final/with_acceptance/circuit_jsons/flag_circuit_adder" + str(i) + ".json"
    flag_circuit = cirq.read_json(flag_circuit_file)

    def parallel_simulation(error_rate):
                
        number_of_runs = 20000

        results, results_icm, results_rob, results_rob_icm, acceptance = evaluate.stabilizers_robustness_and_logical_error(flag_circuit, icm_circuit, number_of_runs, [error_rate], True, "Adder " + str(i))

        # save as csvs
        res_df = pd.DataFrame(results)
        res_icm_df = pd.DataFrame(results_icm)
        res_rob_df = pd.DataFrame(results_rob)
        res_rob_icm_df = pd.DataFrame(results_rob_icm)
        acceptance = pd.DataFrame(acceptance)
        res_df.to_csv("results_" + str(error_rate) + ".csv",index=False)
        res_icm_df.to_csv("results_icm_" + str(error_rate) + ".csv",index=False)
        res_rob_df.to_csv("results_rob_" + str(error_rate) + ".csv",index=False)
        res_rob_icm_df.to_csv("results_rob_icm_" + str(error_rate) + ".csv",index=False)
        acceptance.to_csv("acceptance_" + str(error_rate) + ".csv",index=False)

    error_rates = [0.0001, 0.0002, 0.0004, 0.0008, 0.001, 0.00125, 0.0025, 0.005, 0.01]
    pool = Pool()
    pool.map(parallel_simulation, error_rates)
    pool.close()
    pool.join()

    # plotting
    
    plt.title("Logical Error Rate, Adder " + str(i))
    res = []
    res_icm = []
    for p in error_rates:
        results = pd.read_csv("results_" + str(p) + ".csv")
        result = results.to_numpy()
        res.append(result[0,0])
        
        results_icm = pd.read_csv("results_icm_" + str(p) + ".csv")
        result_icm = results_icm.to_numpy()
        res_icm.append(result_icm[0,0])
                
    plt.loglog(error_rates, res, label="flag circuit")
    plt.loglog(error_rates, res_icm, label="icm circuit")
    plt.xlabel('noise channel strength')
    plt.ylabel('logical error rate')
    plt.legend()
    filename = "logical_error_2_flags.png"
    plt.savefig(filename)
    plt.close()
    