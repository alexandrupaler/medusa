import cirq.circuits
import cirq
import stimcirq

if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from preparation import compiler, test_circuits
    from evaluation import evaluate, state_vector_comparison


if __name__ == '__main__':

    c = compiler.FlagCompiler()

    icm_circuit: cirq.Circuit = c.decompose_to_ICM(test_circuits.adder(7))

    flag_circuit = c.add_flag(icm_circuit, strategy="heuristic")

    initial_state = evaluate.generate_input_strings(icm_circuit, 1)

    prepared_circuit = evaluate.prepare_circuit_from_string(flag_circuit, initial_state[0])
    stim_circuit = stimcirq.cirq_circuit_to_stim_circuit(prepared_circuit)
    
    # print circuit to check if hadamards are on correct qubits
    print("cirq circuit:")
    print(prepared_circuit)
    print("stim circuit:")
    print(stim_circuit)
