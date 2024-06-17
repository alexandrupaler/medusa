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

    """

    # triton cpus:
    # - 5

    # the following rough values are best on previous results:

    adder_3_error = 0.00029 #0.00028861625100563154
    adder_4_error = 0.00054 #0.0005423694576305424
    adder_5_error = 0.00084 #0.0008370490474260235
    adder_6_error = 0.00125 #0.001249112845990064

    goal_errors = {
        3: adder_3_error,
        4: adder_4_error,
        5: adder_5_error,
        6: adder_6_error
    }

    def parallel_simulation(i):

        final_flags = (-1,-1)

        goal_error = goal_errors[i - 1]

        flag_amounts = [(1,1), (1,2), (2,1), (2,2), (1,3), (3,1), (2,3), (3,2), (3,3)]

        number_of_flag_configurations = 10
        number_of_runs = 100
        error_rate = 0.0001

        for flags in flag_amounts:

            xf = flags[0]
            zf = flags[1]

            warnings.warn("try out flags xf, zf: " + str(xf) + ", " + str(zf))

            # find good flag configuration
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
            
            error_rates = [error_rate]

            results, results_icm, results_rob, results_rob_icm, acceptance = evaluate.stabilizers_robustness_and_logical_error(flag_circuit, icm_circuit, number_of_runs, error_rates, True, "Adder " + str(i))

            # compare
            if results[0] <= goal_error:
                
                final_flags = (xf, zf)

                # warning because triton
                warnings.warn("error was small enough!" + str(i))

                break
        
        warnings.warn("final flags xf, zf: " + str(final_flags[0]) + ", " + str(final_flags[1]))
        print("adder " + str(i) + " final flags: " + str(final_flags[0]) + ", " + str(final_flags[1]))
        return final_flags

    paramlist = [4,5,6]
    pool = Pool()
    pool.map(parallel_simulation, paramlist)
    pool.close()
    pool.join()

    """

    error_rates = [0.0001, 0.0002, 0.0004, 0.0008, 0.001, 0.00125, 0.0025, 0.005, 0.01]

    adder_size = 3

    def parallel_simulation(i):

        number_of_flag_configurations = 30
        number_of_runs = 100


        xf = i #[0]
        zf = i# [1]

        warnings.warn("try out flags xf, zf: " + str(xf) + ", " + str(zf))

        # find good flag configuration
        res = np.zeros((number_of_flag_configurations,))
        circuits = []

        for run in range(number_of_flag_configurations):
            c = compiler.FlagCompiler()
            icm_circuit: cirq.Circuit = c.decompose_to_ICM(test_circuits.adder(adder_size), i=i)
            flag_circuit = c.add_flag(icm_circuit, number_of_x_flag=xf, number_of_z_flag=zf)
            
            circuits.append(flag_circuit)

            results, results_icm, results_rob, results_rob_icm, accept = evaluate.stabilizers_robustness_and_logical_error(flag_circuit, icm_circuit, number_of_runs, [error_rates[0]], False, "Adder ")
            res[run] = np.average(results)
            
        min_index = np.argmin(res)
        best_circuit = circuits[min_index]
            
        # run simulation
        c = compiler.FlagCompiler()
        icm_circuit: cirq.Circuit = c.decompose_to_ICM(test_circuits.adder(adder_size), i=i)
        flag_circuit = best_circuit
        
        results, results_icm, results_rob, results_rob_icm, acceptance = evaluate.stabilizers_robustness_and_logical_error(flag_circuit, icm_circuit, number_of_runs, error_rates, True, "Adder " + str(i))
        
        res_df = pd.DataFrame(results)
        res_df.to_csv("results_" + str(i) + ".csv",index=False)

        warnings.warn("run " + str(i) + " done")
        return

    # run only with adder 3
    paramlist = [1, 2, 3]
    pool = Pool()
    pool.map(parallel_simulation, paramlist)
    pool.close()
    pool.join()

    plt.title("Logical Error Rate, Adder 3")
    for p in paramlist:
        results = pd.read_csv("results_" + str(p) + ".csv")
        flag_circuit_name = "flags: " + str(p)
        plt.loglog(error_rates, results, label=flag_circuit_name)
    plt.xlabel('noise channel strength')
    plt.ylabel('logical error rate')
    plt.legend()
    filename = "logical_error_2_flags.png"
    plt.savefig(filename)
    plt.close()


