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

    c = compiler.FlagCompiler()
    icm_circuit: cirq.Circuit = c.decompose_to_ICM(test_circuits.test_circuit2())

    number_of_runs = 100
    error_rates = [0.0001, 0.0002, 0.0004, 0.0008, 0.001, 0.00125, 0.0025, 0.005, 0.01]

    results = np.zeros((len(error_rates),))

    for e in range(len(error_rates)):
        error_rate = error_rates[e]
        print("error :" + str(e))

        comp = compiler.FlagCompiler()

        # add noise before flags
        noisy_circuit = icm_circuit.with_noise(cirq.depolarize(p=error_rate))

        # add flags
        flag_circuit = comp.add_flag(noisy_circuit, strategy="heuristic")

        # find inout states
        number_of_input_states = 100
        input_states = evaluate.generate_input_strings(icm_circuit, number_of_input_states)
        
        # find stabilizers
        stabilizers = []
        for s in range(len(input_states)):
            print("state :" + str(s))

            state = input_states[s]
            prepared_circuit = evaluate.prepare_circuit_from_string(flag_circuit, state)
            expected_stim = stimcirq.cirq_circuit_to_stim_circuit(prepared_circuit)
            simulator_expected = stim.TableauSimulator()
            simulator_expected.do_circuit(expected_stim)
            stabilizers.append(simulator_expected.canonical_stabilizers())
        
        # run simulation
        res, a, b = evaluate.stabilizers_perfect_flags(flag_circuit, icm_circuit, number_of_runs, stabilizers, input_states)
        results[e] = res

    # plotting

    plt.title("Logical Error Rate with Perfect Flags")
    plt.loglog(error_rates, results)
    plt.xlabel('noise channel strength')
    plt.ylabel('logical error rate')
    plt.legend()
    plt.show()
    #plt.savefig(filename)

