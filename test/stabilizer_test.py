import cirq
import json
import numpy as np
import stim
import stimcirq
from evaluation import evaluate

if __name__ == '__main__':

    # assuming fq indices < dq indices

    circuits_path = "budget_5_log_not_unique/circuits"

    circuit_type = "adder"
    circuit_sample = 0
    
    for circuit_size in range(5,6):

        number_of_input_states = 1

        icm_file_name = f"icm_{circuit_type}_{circuit_size}_{circuit_sample}.json"
        flag_file_name = f"fc_{circuit_type}_{circuit_size}_{circuit_sample}.json"

        icm_circuit: cirq.Circuit = cirq.read_json(f"{circuits_path}/{icm_file_name}")
        flag_circuit: cirq.Circuit = cirq.read_json(f"{circuits_path}/{flag_file_name}")

        """
        qubit1 = cirq.NamedQubit("1")
        qubit0 = cirq.NamedQubit("0")

        moment1 = cirq.Moment([cirq.CNOT(qubit1, qubit0)])
        flag_circuit = cirq.Circuit((moment1))
        """

        #print(flag_circuit)

        input_state = evaluate.generate_input_strings(icm_circuit, number_of_input_states)
        print(input_state)

        icm_circuit = evaluate.prepare_circuit_from_string(icm_circuit, input_state[0])
        flag_circuit = evaluate.prepare_circuit_from_string(flag_circuit, input_state[0])
        
        # find stabilizer of icm & flag circuit circuit and compare
        stim_icm = stimcirq.cirq_circuit_to_stim_circuit(icm_circuit)
        stim_flag = stimcirq.cirq_circuit_to_stim_circuit(flag_circuit)

        # icm stabilizers
        simulator = stim.TableauSimulator()
        simulator.do_circuit(stim_icm)
        icm_stabilizers = simulator.canonical_stabilizers()

        # flag stabilizers
        simulator = stim.TableauSimulator()
        simulator.do_circuit(stim_flag)
        flag_stabilizers = simulator.canonical_stabilizers()

        print("icm")
        print(icm_stabilizers)
        print("flag")
        print(flag_stabilizers)    

        # test if shorter stabilizer is ok
        final_state = evaluate.measure_stabilizers(simulator, icm_stabilizers)
        print(final_state)

        # shorter is ok

        # stabilizers always of the form (for icm and flag respectively)
        # stim.PauliString("+Z_____________"), stim.PauliString("+Z_________________________")
        # the problem is the order of the qubits; assuming the qubit order is not revered in the string, 
        # the flag qubits come before the data qubits
        # -> need to add "___" to the beginning of the strings"

        flag_stabilizers_new = evaluate.get_flag_stabilizers_from_icm(flag_circuit, icm_stabilizers)
        print(flag_stabilizers_new[0])
        print(flag_stabilizers[0])
        print(icm_stabilizers[0])

        #print(flag_circuit)