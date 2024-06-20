import cirq.circuits
from preparation import compiler, test_circuits
from evaluation import evaluate
import cirq
import numpy as np
import stimcirq
import matplotlib.pyplot as plt
from matplotlib import cm
import warnings
import stim
from multiprocessing import Pool
import itertools


if __name__ == '__main__':

    # ONLY FOR TESTING PURPOSES ATM

    number_of_runs = 100
    error_rates = [0.0001, 0.0002, 0.0004, 0.0008, 0.001, 0.00125, 0.0025, 0.005, 0.01]
    c = compiler.FlagCompiler()
    circ = test_circuits.adder(5)

    # decompose
    icm_circuit: cirq.Circuit = c.decompose_to_ICM(circ)

    # add flags
    flag_circuit = c.add_flag(icm_circuit, number_of_x_flag=1, number_of_z_flag=1)

    # run simulation
    results, a, b, c, d = evaluate.stabilizers_robustness_and_logical_error(flag_circuit, icm_circuit, number_of_runs, error_rates, False, "title", True)

    # plotting
    plt.title("Logical Error Rate with Perfect Flags, Adder 5")
    plt.loglog(error_rates, results)
    plt.xlabel('noise channel strength')
    plt.ylabel('logical error rate')
    plt.show()
    #plt.savefig(filename)

