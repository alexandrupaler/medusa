import cirq.circuits
import cirq
import numpy as np
import pandas as pd

if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from preparation import compiler, test_circuits
    from evaluation import evaluate, state_vector_comparison


if __name__ == '__main__':

    c = compiler.FlagCompiler()

    icm_circuit: cirq.Circuit = c.decompose_to_ICM(test_circuits.adder(3))

    flag_circuit = c.add_flag(icm_circuit, strategy="heuristic")

    error_rates = np.linspace(0.001, 0.01, 5)
    number_of_runs = 10
    # the number of input states is assumed to be 100
    input_states = 100

    comp_results, comp_icm, rob, rob_icm, accept = evaluate.stabilizers_robustness_and_logical_error(flag_circuit, icm_circuit, number_of_runs, error_rates, False, "title", perfect_flags = "perfect flags")

    # obtain same results from csvs
    results = np.zeros((len(error_rates,)))
    results_icm = np.zeros((len(error_rates,)))

    # this is pretty much copied from evaluate.stabilizers_robustness_and_logical_error
    for e in range(len(error_rates)):
        flag_measurements_df = pd.read_csv("flag_measurements_df_error_rate_" + str(e) + ".csv").to_numpy()
        stabilizer_measurements_df = pd.read_csv("stabilizer_measurements_df_error_rate_" + str(e) + ".csv").to_numpy()
        icm_measurements_df = pd.read_csv("icm_measurements_df_error_rate_" + str(e) + ".csv").to_numpy()

        error_occured = 0
        correct_flags = 0
        missed_flags = 0
        false_flags = 0
        no_flag = 0

        for s in range(input_states):
            for n in range(number_of_runs):

                flag_measurements = flag_measurements_df[s,n]
                stabilizer_measurements = stabilizer_measurements_df[s,n]
                stabilizer_measurements_icm = icm_measurements_df[s,n]

                # flag circuits
                if not np.any(stabilizer_measurements):
                    # if no error but flag went off
                    if np.any(flag_measurements):
                        false_flags += 1
                    else:
                        no_flag += 1
                else:
                    # if flags caught error
                    if np.any(flag_measurements):
                        correct_flags += 1
                    # if flags missed error
                    else:
                        missed_flags += 1

                # icm circuit
                if np.any(stabilizer_measurements_icm):
                    error_occured += 1


        results[e] = missed_flags / ((no_flag + missed_flags) * input_states)
        results_icm[e] = error_occured / (number_of_runs * input_states)
    
    # compare results
    print("results for flags:") # should be equal
    print(results)
    print(comp_results)
    print("results for icm:") # should be equal
    print(results_icm)
    print(comp_icm)
