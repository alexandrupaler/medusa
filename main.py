import cirq.circuits
from preparation import compiler, test_circuits
from evaluation import evaluate
import cirq
import numpy as np
import stimcirq

if __name__ == '__main__':

    # todo:
    # - run simulation
    # - check if there are any bugs
    # - prepare 3d plot: 
        # - error 1% and 10%
        # - set number of flags
        # - adder size, 2-5
    # - prepare & send off to triton

    # bugs:
    # - map heuristic has a bug: doesn't work with the adder circuit

    c = compiler.FlagCompiler()

    #icm_circuit: cirq.Circuit = c.decompose_to_ICM(test_circuits.test_circuit2())

    adder2 = test_circuits.adder(2)
    icm_circuit: cirq.Circuit = c.decompose_to_ICM(adder2)

    print(icm_circuit)

    #f_cir_map = c.add_flag(icm_circuit, strategy="map")
    f_cir_random = c.add_flag(icm_circuit,number_of_x_flag=3,number_of_z_flag=3)
    f_cir_heuristic = c.add_flag(icm_circuit, strategy="heuristic")

    print("\n")
    print("Flags inserted!")
    print("\n")

    flag_circuit = f_cir_heuristic
    
    # plots the logical error rate of flagged and flagless circuit with different inpout states and error rates
    # the noise is randomized depolarising noise
    #
    number_of_runs = 100
    error_rates = np.linspace(0.001, 0.01, 10) #0.001, 0.05, 20)
    evaluate.random_noise_benchmark(flag_circuit, icm_circuit, number_of_runs, error_rates)

    # calculates a error-propagation "failure" rate based on the weight of the errors for flagged and unflagged circuit
    # the errors are generated manually
    #
    # evaluate.evaluate_flag_circuit(flag_circuit, icm_circuit, 3, 100)
