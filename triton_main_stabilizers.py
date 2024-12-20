import cirq.circuits
import cirq
from preparation import compiler, test_circuits
from evaluation import evaluate


if __name__ == '__main__':

    c = compiler.FlagCompiler()

    icm_circuit: cirq.Circuit = c.decompose_to_ICM(test_circuits.test_circuit2())

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
    evaluate.stabilizers_robustness_and_logical_error(flag_circuit, icm_circuit, number_of_runs, error_rates, True, "testcircuit 2")

