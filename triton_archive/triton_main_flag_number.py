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
    # - 5

    error_rates = [0.0001, 0.0002, 0.0004, 0.0008, 0.001, 0.00125, 0.0025, 0.005, 0.01]

    adder_size = 7

    def parallel_simulation(i):

        number_of_flag_configurations = 50
        number_of_runs = 100

        xf = i
        zf = i

        warnings.warn("try out flags xf, zf: " + str(xf) + ", " + str(zf))

        # find good flag configuration
        res = np.zeros((number_of_flag_configurations,))
        circuits = []

        for run in range(number_of_flag_configurations):
            c = compiler.FlagCompiler()
            icm_circuit: cirq.Circuit = c.decompose_to_ICM(test_circuits.adder(adder_size), i=i)
            flag_circuit = c.add_flag(icm_circuit, number_of_x_flag=xf, number_of_z_flag=zf)
            
            circuits.append(flag_circuit)

            results, results_icm, results_rob, results_rob_icm, accept = evaluate.stabilizers_robustness_and_logical_error(flag_circuit, icm_circuit, number_of_runs, [error_rates[0]], False, "Adder ", noise_type="perfect flags")
            res[run] = np.average(results)
            
        min_index = np.argmin(res)
        best_circuit = circuits[min_index]

        json_string = cirq.to_json(best_circuit)
        with open("flag_circuit_adder_" + str(adder_size) + "_flags" + str(i) + ".json", "w") as outfile:
            outfile.write(json_string)
            
        # run simulation
        c = compiler.FlagCompiler()
        icm_circuit: cirq.Circuit = c.decompose_to_ICM(test_circuits.adder(adder_size), i=i)
        flag_circuit = best_circuit
        
        results, results_icm, results_rob, results_rob_icm, acceptance = evaluate.stabilizers_robustness_and_logical_error(flag_circuit, icm_circuit, number_of_runs, error_rates, True, "Adder " + str(i), noise_type="perfect flags")
        
        res_df = pd.DataFrame(results)
        res_df.to_csv("results_" + str(i) + ".csv",index=False)

        warnings.warn("run " + str(i) + " done")
        return

    # run only with one adder
    paramlist = [1, 2, 3]
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
    filename = "logical_error_flags_adder_" + str(adder_size) + ".png"
    plt.savefig(filename)
    plt.close()


