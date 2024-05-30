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

    def parallel_simulation(i):
        c = compiler.FlagCompiler()

        icm_circuit: cirq.Circuit = c.decompose_to_ICM(test_circuits.adder(i), i=i)

        warnings.warn("decompose done for adder with " + str(len(list(icm_circuit.all_qubits()))) + " qubits")

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
        error_rates = [0.0001, 0.0002, 0.0004, 0.0008, 0.001, 0.00125, 0.0025, 0.005, 0.01]

        start = time.time()
        evaluate.stabilizers_robustness_and_logical_error(flag_circuit, icm_circuit, number_of_runs, error_rates, True, "Adder " + str(i))
        end = time.time()
        print("time it took: " + str(end - start))

    paramlist = [2,3,4,5,6,7]
    pool = Pool()
    pool.map(parallel_simulation, paramlist)
    pool.close()
    pool.join()

