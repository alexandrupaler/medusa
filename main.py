import cirq.circuits
from preparation import compiler, test_circuits
from evaluation import evaluate
import cirq
import numpy as np
import stimcirq
import matplotlib.pyplot as plt
from matplotlib import cm
import warnings
from multiprocessing import Pool
import itertools


if __name__ == '__main__':

    # bugs:
    # - map heuristic has a bug: doesn't work with the adder circuit

    c = compiler.FlagCompiler()

    icm_circuit: cirq.Circuit = c.decompose_to_ICM(test_circuits.test_circuit2())

    print("\n")
    print("Decompose done!")
    print("\n")

    print(icm_circuit)

    #f_cir_map = c.add_flag(icm_circuit, strategy="map")
    #f_cir_random = c.add_flag(icm_circuit,number_of_x_flag=3,number_of_z_flag=3)
    f_cir_heuristic = c.add_flag(icm_circuit, strategy="heuristic")

    print("\n")
    print("Flags inserted!")
    print("\n")

    flag_circuit = f_cir_heuristic

    print(flag_circuit)
    
    # plots the logical error rate of flagged and flagless circuit with different inpout states and error rates
    # the noise is randomized depolarising noise
    #
    number_of_runs = 10
    error_rates = np.linspace(0.001, 0.01, 10)
    evaluate.random_noise_benchmark(flag_circuit, icm_circuit, number_of_runs, error_rates, True, "heuristic_random_results.png")

    # calculates a error-propagation "failure" rate based on the weight of the errors for flagged and unflagged circuit
    # the errors are generated manually
    #
    #evaluate.evaluate_flag_circuit(flag_circuit, icm_circuit, 3, 100, True, "heuristic_propagation_results.png")


