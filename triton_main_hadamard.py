import cirq.circuits
from preparation import compiler, test_circuits
from evaluation import evaluate
import cirq
import numpy as np


if __name__ == '__main__':

    c = compiler.FlagCompiler()

    icm_circuit: cirq.Circuit = c.decompose_to_ICM(test_circuits.logical_hadamard_1_noflags())

    print(icm_circuit)

    flag_circuit = test_circuits.add_flags_to_test_hadamard(icm_circuit)
    
    # plots the logical error rate of flagged and flagless circuit with different inpout states and error rates
    # the noise is randomized depolarising noise
    #
    number_of_runs = 10
    error_rates = np.linspace(0.001, 0.01, 5) #0.001, 0.05, 20)
    evaluate.random_noise_benchmark(flag_circuit, icm_circuit, number_of_runs, error_rates, True, "results_random_hadamard.png")

    # calculates a error-propagation "failure" rate based on the weight of the errors for flagged and unflagged circuit
    # the errors are generated manually
    #
    #evaluate.evaluate_flag_circuit(flag_circuit, icm_circuit, 3, 100, True, "heuristic_propagation_results.png")


