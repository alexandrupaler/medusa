from preparation import test_circuits

if __name__ == '__main__':


    # example benchmark circuit

    qubits = 10
    edge_probability = 0.5
    remove_hadamards = True

    circuit1 = test_circuits.circuit_generator_1(qubits, edge_probability, remove_hadamards)
    circuit2 = test_circuits.circuit_generator_2(qubits, edge_probability, remove_hadamards)
    circuit3 = test_circuits.circuit_generator_3(qubits, edge_probability, remove_hadamards)

    with open('example_benchmark_circuits.txt', 'w') as outfile:    
        outfile.write("circuit generator 1:\n")
        outfile.write(circuit1.to_text_diagram(use_unicode_characters=False))
        outfile.write("\n\ncircuit generator 2:\n")
        outfile.write(circuit2.to_text_diagram(use_unicode_characters=False))
        outfile.write("\n\ncircuit generator 3:\n")
        outfile.write(circuit3.to_text_diagram(use_unicode_characters=False))


    
