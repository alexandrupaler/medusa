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


    def parallel_simulation(i):
        c = compiler.FlagCompiler()

        icm_circuit: cirq.Circuit = c.decompose_to_ICM(test_circuits.adder_only_cnots(i), i=i)

        # choose random qubits [xf, zf]
        qubits = list(icm_circuit.all_qubits())
        chosen_qubits = np.random.choice(qubits, 2)
        chosen_xq = chosen_qubits[0]
        chosen_zq = chosen_qubits[1]

        # add flag on qubit to the beginning and end
        xf = cirq.NamedQubit("0xf")
        zf = cirq.NamedQubit("0zf")

        flag_circuit = cirq.Circuit()

        # xf has targets, zf has controls + hadmards
        flag_circuit.append(cirq.CNOT(chosen_xq, xf),strategy=cirq.InsertStrategy.NEW_THEN_INLINE)
        flag_circuit.append(cirq.H(zf),strategy=cirq.InsertStrategy.NEW_THEN_INLINE)
        flag_circuit.append(cirq.CNOT(zf, chosen_zq),strategy=cirq.InsertStrategy.NEW_THEN_INLINE)

        flag_circuit.append(icm_circuit)

        flag_circuit.append(cirq.CNOT(chosen_xq, xf),strategy=cirq.InsertStrategy.NEW_THEN_INLINE)
        flag_circuit.append(cirq.CNOT(zf, chosen_zq),strategy=cirq.InsertStrategy.NEW_THEN_INLINE)

        flag_circuit.append(cirq.measure(xf))
        flag_circuit.append(cirq.H(zf))
        flag_circuit.append(cirq.measure(zf))
        flag_circuit.append(cirq.reset(xf))
        flag_circuit.append(cirq.reset(zf))


        print(flag_circuit)

        # save circuit
        json_string = cirq.to_json(flag_circuit)
        with open("flag_circuit_adder" + str(i) + ".json", "w") as outfile:
            outfile.write(json_string)
        
        number_of_runs = 1000

        start = time.time()
        results, results_icm, results_rob, results_rob_icm, acceptance = evaluate.stabilizers_robustness_and_logical_error(flag_circuit, icm_circuit, number_of_runs, error_rates, True, "Adder " + str(i), perfect_flags="perfect flags")
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

    plt.title("Logical Error Rate, 2 Flags")
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
    filename = "logical_error_2_flags_compare.png"
    plt.savefig(filename)
    plt.close()

    """
    
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
        plt.loglog(error_rates, results_icm, label=icm_circuit_name)
    plt.xlabel('noise channel strength')
    plt.ylabel('acceptance rate')
    plt.legend()
    filename = "acceptance_rate.png"
    plt.savefig(filename)
    plt.close()

    """
    
