import numpy as np
import cirq
import stim
import stimcirq
import itertools

from functools import reduce
from preparation import error_circuit
from evaluation import evaluate

def expected_state_vector(circuit: cirq.Circuit):
    stim_circuit = stimcirq.cirq_circuit_to_stim_circuit(circuit)
    simulator = stim.TableauSimulator()
    simulator.do_circuit(stim_circuit)
    return simulator.state_vector()


# should do st that help me visualize
def possible_state_vector_with_flags(circuit: cirq.Circuit, number_of_error: int, initial_state):
    result = []

    correct_state_vector = expected_state_vector(circuit)
    possible_error_string = []
    for n in range(number_of_error + 1):
        possible_error_string += error_circuit.generate_error_string(n)

    qubits = list(circuit.all_qubits())
    number_of_qubits = len(qubits)
    flag_qubits = list(filter(lambda q: 'f' in q.name, qubits))

    # new: now errors on flags are also considered
    original_qubits = qubits #list(filter(lambda q: 'f' not in q.name, qubits))

    locations = list(itertools.combinations_with_replacement(original_qubits, number_of_error))
    # can be changed
    for l in locations:
        for e in possible_error_string:

            helper = circuit.copy()
            for q, error_char in zip(l, e):
                q: cirq.NamedQubit
                if error_char == "x":
                    helper.append(cirq.X(q))
                else:
                    helper.append(cirq.Z(q))

            simulator = stim.TableauSimulator()

            # new: prepare input state with H gates
            helper = evaluate.prepare_circuit_from_string(helper, initial_state)
            #print(helper)

            stim_circuit = stimcirq.cirq_circuit_to_stim_circuit(helper)
            simulator.do_circuit(stim_circuit)
            final_state = simulator.state_vector()
            result.append(final_state)

    result.append(correct_state_vector)
    return result


def possible_state_vector_without_flags(circuit: cirq.Circuit, number_of_error: int, initial_state):
    result = []

    correct_state_vector = expected_state_vector(circuit)
    possible_error_string = []
    for n in range(number_of_error + 1):
        possible_error_string += error_circuit.generate_error_string(n)

    qubits = list(circuit.all_qubits())
    number_of_qubits = len(qubits)
    flag_qubits = list(filter(lambda q: 'f' in q.name, qubits))
    original_qubits = list(filter(lambda q: 'f' not in q.name, qubits))
    locations = list(itertools.combinations_with_replacement(original_qubits, number_of_error))
    # can be changed
    for l in locations:
        for e in possible_error_string:

            helper = circuit.copy()
            for q, error_char in zip(l, e):
                q: cirq.NamedQubit
                if error_char == "x":
                    helper.append(cirq.X(q))
                else:
                    helper.append(cirq.Z(q))

            simulator = stim.TableauSimulator()

            # new: prepare input state with H gates
            helper = evaluate.prepare_circuit_from_string(helper, initial_state)

            stim_circuit = stimcirq.cirq_circuit_to_stim_circuit(helper)
            simulator.do_circuit(stim_circuit)
            final_state = simulator.state_vector()
            result.append(final_state)

    result.append(correct_state_vector)
    return result


def have_error_propagated(state_vector, possible_state_vectors):
    return not any(np.array_equal(state_vector, possible_vector) for possible_vector in possible_state_vectors)

def possible_error_states(error_circuits, initial_state):
    final_states = []
    for c in range(len(error_circuits)):
        circuit: cirq.Circuit = error_circuits[c]
        circuit = evaluate.prepare_circuit_from_string(circuit, initial_state)
        stim_circuit = stimcirq.cirq_circuit_to_stim_circuit(circuit)
        simulator = stim.TableauSimulator()
        simulator.do_circuit(stim_circuit)
        final_state =  evaluate.measure_stabilizers(simulator)#simulator.state_vector()
        final_states.append(final_state)
    return final_states

def equal_stabilizers(state: list[stim.PauliString], possible_states: list[list[stim.PauliString]]):
    state_found_in_possible_states = np.full((len(possible_states),),True)
    for j in range(len(possible_states)):
        pstate = possible_states[j]
        stabilizer_is_equal = np.full((len(state),), True)
        for i in range(len(pstate)):
            stabilizer_is_equal[i] = (state[i] == pstate[i])
        state_found_in_possible_states[j] = False not in stabilizer_is_equal
    
    ret = True in state_found_in_possible_states
    return ret