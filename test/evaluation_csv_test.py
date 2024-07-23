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

    # obtain results from csvs
    results, results_icm = evaluate.calculate_logical_error_from_csv(len(error_rates), number_of_runs, input_states)
    
    # compare results
    print("results for flags:") # should be equal
    print(results)
    print(comp_results)
    print("results for icm:") # should be equal
    print(results_icm)
    print(comp_icm)
