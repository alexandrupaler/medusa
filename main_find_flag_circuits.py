import cirq.circuits
import cirq
import numpy as np
import warnings
from multiprocessing import Pool
from preparation import compiler, test_circuits
from evaluation import evaluate


if __name__ == '__main__':

    # triton cpus:
    # - 6

    def parallel_simulation(i):
        
        number_of_flag_configurations = 5
        number_of_runs = 100
        error_rate = 0.001

        res = np.zeros((number_of_flag_configurations,))
        circuits = []

        for run in range(number_of_flag_configurations):
            c = compiler.FlagCompiler()
            icm_circuit: cirq.Circuit = c.decompose_to_ICM(test_circuits.adder(i), i=i)
            flag_circuit = c.add_flag(icm_circuit, number_of_x_flag=1, number_of_z_flag=1)
            
            circuits.append(flag_circuit)

            results, results_icm, results_rob, results_rob_icm = evaluate.stabilizers_robustness_and_logical_error(flag_circuit, icm_circuit, number_of_runs, [error_rate], False, "Adder ")
            res[run] = np.average(results)

        # warning because triton
        warnings.warn("done: " + str(i))
        
        # find best flag configuration
        min_index = np.argmin(res)
        best_circuit = circuits[min_index]

        json_string = cirq.to_json(best_circuit)
        with open("flag_circuit_adder" + str(i) + ".json", "w") as outfile:
            outfile.write(json_string)

    paramlist = [3,4,5,6,7] #[2,3,4,5,6,7]
    pool = Pool()
    pool.map(parallel_simulation, paramlist)
    pool.close()
    pool.join()


