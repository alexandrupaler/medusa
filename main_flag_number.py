import cirq.circuits
import cirq
import numpy as np
import warnings
import pandas as pd
from multiprocessing import Pool
from preparation import compiler, test_circuits
from evaluation import evaluate


if __name__ == '__main__':

    # triton cpus:
    # - 5

    # the following rough values are best on previous results:

    adder_3_error = 0.0209
    adder_4_error = 0.0398
    adder_5_error = 0.0707
    adder_6_error = 0.1082

    goal_errors = {
        3: adder_3_error,
        4: adder_4_error,
        5: adder_5_error,
        6: adder_6_error
    }

    def parallel_simulation(i):

        final_flags = (-1,-1)

        goal_error = goal_errors[i - 1]

        flag_amounts = [(0,1), (1,0), (1,1), (1,2), (2,1), (2,2), (0,3), (3,0), (1,3), (3,1), (2,3), (3,2), (3,3)]

        for flags in flag_amounts:

            xf = flags[0]
            zf = flags[1]

            warnings.warn("try out flags xf, zf: " + str(xf) + ", " + str(zf))

            
            # find good flag configuration
            number_of_flag_configurations = 5
            number_of_runs = 10
            error_rate = 0.0001

            res = np.zeros((number_of_flag_configurations,))
            circuits = []

            for run in range(number_of_flag_configurations):
                c = compiler.FlagCompiler()
                icm_circuit: cirq.Circuit = c.decompose_to_ICM(test_circuits.adder(i), i=i)
                flag_circuit = c.add_flag(icm_circuit, number_of_x_flag=xf, number_of_z_flag=zf)
                
                circuits.append(flag_circuit)

                results, results_icm, results_rob, results_rob_icm, accept = evaluate.stabilizers_robustness_and_logical_error(flag_circuit, icm_circuit, number_of_runs, [error_rate], False, "Adder ")
                res[run] = np.average(results)
            
            min_index = np.argmin(res)
            best_circuit = circuits[min_index]

            
            # run simulation
            c = compiler.FlagCompiler()
            icm_circuit: cirq.Circuit = c.decompose_to_ICM(test_circuits.adder(i), i=i)
            flag_circuit = best_circuit
            
            number_of_runs = 100
            error_rates = [error_rate]

            results, results_icm, results_rob, results_rob_icm, acceptance = evaluate.stabilizers_robustness_and_logical_error(flag_circuit, icm_circuit, number_of_runs, error_rates, True, "Adder " + str(i))

            # warning because triton
            warnings.warn("done: " + str(i))

            # compare
            if results[0] <= goal_error:
                print("error was small enough!")
                final_flags = (xf, zf)
                break

        warnings.warn("final flags xf, zf: " + str(final_flags[0]) + ", " + str(final_flags[1]))
        print("adder " + str(i) + " final flags: " + str(final_flags[0]) + ", " + str(final_flags[1]))
        return final_flags

    paramlist = [4,5,6,7]
    pool = Pool()
    pool.map(parallel_simulation, paramlist)
    pool.close()
    pool.join()


