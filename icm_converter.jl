using Jabalizer
using PythonCall

cirq = pyimport("cirq");
gates_to_decomp = ["T", "T^-1"];

icm_input = Jabalizer.load_circuit_from_cirq_json("input_cirq_circuit.json")
(icm_circuit,_) = Jabalizer.compile(icm_input, 10, gates_to_decomp)
Jabalizer.save_circuit_to_cirq_json(icm_circuit,"output_cirq_icm_circuit.json");

cirq_circuit = cirq.read_json("output_cirq_icm_circuit.json")
print(cirq_circuit)


