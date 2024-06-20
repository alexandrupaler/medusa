import cirq.circuits
import cirq
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from multiprocessing import Pool
from preparation import compiler, test_circuits
from evaluation import evaluate



if __name__ == '__main__':

    # triton cpus:
    # - 4

    # Problem: preparing the circuit from string doesn't necessarily include all the qubuts in the circuit -> error

    error_rates = [0.0001, 0.0002, 0.0004, 0.0008, 0.001, 0.00125, 0.0025, 0.005, 0.01]
    number_of_runs = 100
    adder_size = 3
    number_of_flag_configurations = 10

    def parallel_simulation(i):
        c = compiler.FlagCompiler()

        # this can technically be set to some tiny circuit to improve execution time when runing the simulations,
        # since we are not really interested in the flagless error rate
        icm_circuit: cirq.Circuit = c.decompose_to_ICM(test_circuits.adder(adder_size), i=i)

        # split circuit into i partitions
        moments = list(icm_circuit.moments)
        number_of_moments = len(moments)
        split_size = number_of_moments // i

        main_circuit = []

        for s in range(1,i+1):
            start = (s-1) * split_size
            end = s * split_size

            # set the last endpoint to the last moment
            if s == i and end != number_of_moments:
                end = number_of_moments

            split_circuit = cirq.Circuit(moments[start:end])

            # find good flag configuration
            res = np.zeros((number_of_flag_configurations,))
            circuits = []
            for run in range(number_of_flag_configurations):
                flag_circuit_test = c.add_flag(split_circuit, number_of_x_flag=1, number_of_z_flag=1)
                circuits.append(flag_circuit_test)
                results, results_icm, results_rob, results_rob_icm, accept = evaluate.stabilizers_robustness_and_logical_error(flag_circuit_test, icm_circuit, number_of_runs, [error_rates[0]], False, "Adder ")
                res[run] = np.average(results)
            min_index = np.argmin(res)
            best_circuit = circuits[min_index]

            main_circuit.append(best_circuit._moments)
            flag_circuit = cirq.Circuit(main_circuit)

            if (s == 1):
                json_string = cirq.to_json(flag_circuit)
                with open("flag_circuit_adder3_flags" + str(i) + ".json", "w") as outfile:
                    outfile.write(json_string)

            results, results_icm, results_rob, results_rob_icm, acceptance = evaluate.stabilizers_robustness_and_logical_error(flag_circuit, icm_circuit, number_of_runs, error_rates, False, "Adder ")

            # save as csvs
            res_df = pd.DataFrame(results)
            res_df.to_csv("results_" + str(i) + "_" + str(s) + ".csv",index=False)

    paramlist = [1,2,3]
    pool = Pool()
    pool.map(parallel_simulation, paramlist)
    pool.close()
    pool.join()

    # plotting
    """
    plt.title("Logical Error Rate, Adder 3")
    for p in paramlist:
        results = pd.read_csv("results_" + str(p) + ".csv")
        flag_circuit_name = "Flags: " + str(p)
        plt.loglog(error_rates, results, label=flag_circuit_name)
    plt.xlabel('noise channel strength')
    plt.ylabel('logical error rate')
    plt.legend()
    filename = "logical_error_2_flags_split.png"
    plt.savefig(filename)
    plt.close()
    """