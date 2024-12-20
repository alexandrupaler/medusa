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

    qubits = 10
    edge_probability = 0.5
    remove_hadamards = True

    icm_circuit = test_circuits.line_to_named(test_circuits.circuit_generator_1(qubits, edge_probability, remove_hadamards))

    print("\n")
    print("Decompose done!")
    print("\n")

    print(icm_circuit)

    flag_circuit = c.add_flag(icm_circuit, number_of_x_flag=1, number_of_z_flag=1)

    print("\n")
    print("Flags inserted!")
    print("\n")

    print(flag_circuit)
   
    number_of_runs = 100
    error_rates = np.linspace(0.001, 0.01, 10)
    evaluate.stabilizers_robustness_and_logical_error(flag_circuit, icm_circuit, number_of_runs, error_rates, False, "", "new noise model")
