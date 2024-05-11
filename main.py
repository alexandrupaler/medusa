import cirq.circuits
from preparation import compiler, test_circuits
from evaluation import evaluate
import cirq
import stimcirq

if __name__ == '__main__':

    c = compiler.FlagCompiler()

    icm_circuit: cirq.Circuit = c.decompose_to_ICM(test_circuits.test_circuit2())

    print(icm_circuit)

    f_cir_map = c.add_flag(icm_circuit, strategy="map")
    f_cir_random = c.add_flag(icm_circuit,number_of_x_flag=3,number_of_z_flag=3)
    f_cir_heuristic = c.add_flag(icm_circuit, strategy="heuristic")

    print("\n")
    print("Flags inserted!")
    print("\n")

    """
    test_circuit: cirq.Circuit = c.decompose_to_ICM(test_circuits.logical_hadamard_1_noflags())
    icm_circuit = test_circuit
    flag_circuit = test_circuits.add_flags_to_test_hadamard(test_circuit)

    stimc = stimcirq.cirq_circuit_to_stim_circuit(flag_circuit)
    print(stimc)
    """

    flag_circuit = f_cir_heuristic

    # print("\n")
    # print(f_cir)
    # print("\n")
    
    # plots the logical error rate of flagged and flagless circuit with different inpout states and error rates
    # the noise is randomized depolarising noise
    #
    evaluate.random_noise_benchmark(flag_circuit, icm_circuit)

    # calculates a error-propagation "failure" rate based on the weight of the errors for flagged and unflagged circuit
    # the errors are generated manually
    #
    # evaluate.evaluate_flag_circuit(flag_circuit, icm_circuit, 3, 100)
