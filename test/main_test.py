import cirq.circuits
import cirq
import stim
import stimcirq
import numpy as np

if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from preparation import compiler, test_circuits
    from evaluation import evaluate, state_vector_comparison


if __name__ == '__main__':

    c = compiler.FlagCompiler()
    circuit: cirq.Circuit = c.decompose_to_ICM(test_circuits.adder(5))
    #print(circuit)

    stim_circuit = stimcirq.cirq_circuit_to_stim_circuit(circuit)
    qubit = list(circuit.all_qubits())[0]

    x_circuit = cirq.Circuit()
    x_circuit.append(cirq.X(qubit))
    x_circuit.append(circuit)
    #print(x_circuit)
    x_stim_circuit = stimcirq.cirq_circuit_to_stim_circuit(x_circuit)

    i_circuit = cirq.Circuit()
    i_circuit.append(cirq.I(qubit))
    i_circuit.append(circuit)
    #print(i_circuit)
    i_stim_circuit = stimcirq.cirq_circuit_to_stim_circuit(i_circuit)

    simulator = stim.TableauSimulator()
    x_simulator = simulator.copy()
    i_simulator = simulator.copy()

    simulator.do_circuit(stim_circuit)
    final_state = evaluate.measure_stabilizers(simulator) #simulator.state_vector()

    x_simulator.do_circuit(x_stim_circuit)
    x_final_state = evaluate.measure_stabilizers(x_simulator) #simulator.state_vector()

    i_simulator.do_circuit(i_stim_circuit)
    i_final_state = evaluate.measure_stabilizers(i_simulator) #simulator.state_vector()

    print("correct state:")
    print(final_state)

    print("equivalent state:")
    print(i_final_state)

    print("wrong state:")
    print(x_final_state)

    print("Test equal_stabilizer:")
    possible_states = [final_state]
    print("Should print true: ", state_vector_comparison.equal_stabilizers(i_final_state, possible_states))
    print("Should print false: ", state_vector_comparison.equal_stabilizers(x_final_state, possible_states))

    # try out how measuring the stabilizers works
    results = np.empty((len(final_state),))
    x_results = np.empty((len(final_state),))
    i_results = np.empty((len(final_state),))

    for i in range(len(final_state)):
        results[i] = simulator.measure_observable(final_state[i]) # equivalent to measure_pauli_string
        x_results[i] = x_simulator.measure_observable(final_state[i])
        i_results[i] = i_simulator.measure_observable(final_state[i])

    print("expected results:")
    print(results)
    print("equivalent results:")
    print(i_results)
    print("wrong results:")
    print(x_results)

    print("Should print true: ", np.all(np.equal(results, i_results)))
    print("Should print false: ", np.all(np.equal(results, x_results)))



