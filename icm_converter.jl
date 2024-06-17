using Jabalizer
using PythonCall

cirq = pyimport("cirq");
gates_to_decomp = ["T", "T^-1"];

function icm_converter_ij(i, j)
    icm_input = Jabalizer.load_circuit_from_cirq_json("input_cirq_circuit" * string(i) * string(j) * ".json")
    (icm_circuit,_) = Jabalizer.compile(icm_input, 10, gates_to_decomp)
    Jabalizer.save_circuit_to_cirq_json(icm_circuit,"output_cirq_icm_circuit" * string(i) * string(j) * ".json");
end

a = parse(Int64, ARGS[1])
b = parse(Int64, ARGS[2])

icm_converter_ij(a, b)