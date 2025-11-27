import cirq.circuits
import cirq
import matplotlib.pyplot as plt
import warnings
import time
import pandas as pd
import numpy as np
from multiprocessing import Pool
from preparation import compiler, test_circuits
from evaluation import evaluate



if __name__ == '__main__':

    # triton cpus:
    # - 6

    error_rates = [0.0001, 0.0002, 0.0004, 0.0008, 0.001, 0.00125, 0.0025, 0.005, 0.01]

    # only adds x flag
    def add_flag(chosen_xq, icm_circuit: cirq.Circuit):
        flag_circuit = cirq.Circuit()

        # add flag on qubit to the beginning and end
        xf = cirq.NamedQubit("0xf")

        first = cirq.Circuit(icm_circuit.moments[0:2])
        second = cirq.Circuit(icm_circuit.moments[2:])

        flag_circuit = first
        flag_circuit.append(cirq.CNOT(chosen_xq, xf),strategy=cirq.InsertStrategy.NEW_THEN_INLINE)
        flag_circuit.append(second)
        flag_circuit.append(cirq.CNOT(chosen_xq, xf),strategy=cirq.InsertStrategy.NEW_THEN_INLINE)
        flag_circuit.append(cirq.measure(xf))
        flag_circuit.append(cirq.reset(xf))

        return flag_circuit

    def parallel_simulation(i):
        c = compiler.FlagCompiler()

        icm_circuit: cirq.Circuit = c.decompose_to_ICM(test_circuits.adder_only_cnots(i), i=i)

        # choose qubits [xf, zf] and moments
        qubits = list(icm_circuit.all_qubits())
        # the below just happens to be the qid of the qubit we want
        chosen_xq =  list(filter(lambda q: "9999999109" == q.name, qubits))[0]

        flag_circuit = add_flag(chosen_xq, icm_circuit)

        # save circuit
        json_string = cirq.to_json(flag_circuit)
        with open("flag_circuit_adder" + str(i) + ".json", "w") as outfile:
            outfile.write(json_string)
        
        number_of_runs = 1000

        start = time.time()
        results, results_icm, results_rob, results_rob_icm, acceptance = evaluate.stabilizers_robustness_and_logical_error(flag_circuit, icm_circuit, number_of_runs, error_rates, True, "Adder " + str(i), noise_type="perfect flags")
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
        acceptance.to_csv("acceptance_" + str(i) + ".csv",index=False)
        

    paramlist = [3,4,5,6,7]
    pool = Pool()
    pool.map(parallel_simulation, paramlist)
    pool.close()
    pool.join()

    
    # plotting

    # alternative path for files (if using files from results_final/with_acceptance):
    # "results_final/with_acceptance/individual_runs/

    plt.title("Manual X Flag, No Hadamards")
    for p in paramlist:
        results = pd.read_csv("results_" + str(p) + ".csv")
        flag_circuit_name = "flag adder " + str(p)
        plt.loglog(error_rates, results, label=flag_circuit_name)

        results = pd.read_csv("results_icm_" + str(p) + ".csv")
        flag_circuit_name = "icm adder " + str(p)
        plt.loglog(error_rates, results, label=flag_circuit_name)

    plt.xlabel('noise channel strength')
    plt.ylabel('logical error rate')
    plt.legend()
    filename = "logical_error_2_flags_by_hand_compare.png"
    plt.savefig(filename)
    plt.close()
    
