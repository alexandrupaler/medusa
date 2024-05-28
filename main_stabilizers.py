import cirq.circuits
from preparation import compiler, test_circuits, error_circuit
from evaluation import evaluate
import cirq
import numpy as np
import stimcirq
import matplotlib.pyplot as plt
from matplotlib import cm
import warnings
from multiprocessing import Pool
import itertools
from multiprocessing import Pool, shared_memory
import time
import pandas as pd



if __name__ == '__main__':

    c = compiler.FlagCompiler()

    icm_circuit: cirq.Circuit = c.decompose_to_ICM(test_circuits.test_circuit2())

    print("\n")
    print("Decompose done!")
    print("\n")

    print(icm_circuit)

    f_cir_heuristic = c.add_flag(icm_circuit, strategy="heuristic")

    print("\n")
    print("Flags inserted!")
    print("\n")

    flag_circuit = f_cir_heuristic

    print(flag_circuit)
    
    number_of_runs = 100
    error_rates = np.linspace(0.001, 0.01, 5)
    evaluate.stabilizers_benchmark_logical_error(flag_circuit, icm_circuit, number_of_runs, error_rates, True, "results_stabilizers_logical_error_testcircuit2.png")
    #evaluate.stabilizers_benchmark_robustness(flag_circuit, icm_circuit, number_of_runs, error_rates, True, "results_stabilizers_robustness_testcircuit2.png")
