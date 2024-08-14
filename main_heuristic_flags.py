import cirq.circuits
import cirq
import numpy as np
import warnings
import pandas as pd
import matplotlib.pyplot as plt
from multiprocessing import Pool
from preparation import compiler, test_circuits
from evaluation import evaluate


if __name__ == '__main__':

    # triton cpus:
    # - depends on the size of the adder

    error_rates = [0.0001, 0.0002, 0.0004, 0.0008, 0.001, 0.00125, 0.0025, 0.005, 0.01]

    adder_size = 3

    number_of_runs = 100

    c = compiler.FlagCompiler()
    icm_circuit: cirq.Circuit = c.decompose_to_ICM(test_circuits.adder_only_cnots(adder_size))

    flag_circuit: cirq.Circuit = c.add_flag(icm_circuit, strategy="map")

    all_qubits = list(flag_circuit.all_qubits())
    x_flag_qubits = list(filter(lambda q: "xf" in q.name, all_qubits))
    z_flag_qubits = list(filter(lambda q: "zf" in q.name, all_qubits))
    num_of_x_flags = len(x_flag_qubits)
    num_of_z_flags = len(z_flag_qubits)
    print(num_of_x_flags)
    print(num_of_z_flags)

            
    def parallel_simulation(i):

        removed_x_flags = x_flag_qubits[0:(num_of_x_flags-i)]
        removed_z_flags = z_flag_qubits[0:(num_of_z_flags-i)]

        chosen_moments = []

        for m in flag_circuit.moments:
            keep = True
            for op in m._operations:
                for qx in removed_x_flags:
                    if str(qx) in str(op.qubits):
                        keep = False
                for qz in removed_z_flags:
                    if str(qz) in str(op.qubits):
                        keep = False
            if keep:
                chosen_moments.append(m)

        new_flag_circuit = cirq.Circuit(chosen_moments)

        print(new_flag_circuit)
                
        results, results_icm, results_rob, results_rob_icm, acceptance = evaluate.stabilizers_robustness_and_logical_error(new_flag_circuit, icm_circuit, number_of_runs, error_rates, False, "Adder", noise_type="perfect flags")
        
        res_df = pd.DataFrame(results)
        res_df.to_csv("results_" + str(i) + ".csv",index=False)

        warnings.warn("run " + str(i) + " done")
        return

    # run only with one adder
    paramlist = range(1, (np.min([num_of_x_flags,num_of_z_flags])+1))
    pool = Pool()
    pool.map(parallel_simulation, paramlist)
    pool.close()
    pool.join()

    plt.title("Logical Error Rate with Perfect Flags, Adder " + str(adder_size))
    for p in paramlist:
        results = pd.read_csv("results_" + str(p) + ".csv")
        flag_circuit_name = "flags: " + str(p)
        plt.loglog(error_rates, results, label=flag_circuit_name)
    plt.xlabel('noise channel strength')
    plt.ylabel('logical error rate')
    plt.legend()
    filename = "logical_error_heuristic_flags_adder_" + str(adder_size) + ".png"
    plt.savefig(filename)
    plt.close()


