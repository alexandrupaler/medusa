import cirq.circuits
import cirq
import numpy as np

if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from preparation import compiler, test_circuits


if __name__ == '__main__':

    c = compiler.FlagCompiler()
    icm_circuit: cirq.Circuit = c.decompose_to_ICM(test_circuits.adder_only_cnots(3))

    # just checking this visually

    flag_circuit = c.add_flag(icm_circuit, strategy="heuristic")

    print(flag_circuit)

    n_of_flags = round(np.sqrt(len(list(icm_circuit.all_qubits()))))
    imp_flags = c.important_flags(flag_circuit, n_of_flags)

    print(imp_flags)
    print(icm_circuit)