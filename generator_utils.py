import warnings

import cirq
import cirq.circuits

from preparation import compiler, test_circuits


def compile_circuits(orig_circuit, size, apply_jabalizer = False):
    c = compiler.FlagCompiler()

    if apply_jabalizer:
        orig_circuit = c.decompose_to_ICM(orig_circuit, i=size)
        named_icm_circuit = orig_circuit
    else:
        named_icm_circuit = test_circuits.line_to_named(orig_circuit)

    flag_circuit = c.add_flag(named_icm_circuit, strategy="heuristic")

    return named_icm_circuit, flag_circuit


def save_circuits(name, icm_circuit, flag_circuit, path):
    icm_json = cirq.to_json(icm_circuit)
    with open(f"{path}icm_{name}.json", "w") as outfile:
        outfile.write(icm_json)

    # circuits/fc_name_i_j.json
    fc_json = cirq.to_json(flag_circuit)
    with open(f"{path}fc_{name}.json", "w") as outfile:
        outfile.write(fc_json)


def generate_circuits(min_qubits, max_qubits, number_of_bench_samples, path):
    # save icm circuits and flag circuits as jsons

    edge_probability = 0.5
    remove_hadamards = 1.0

    for i in range(min_qubits, max_qubits + 1):  # the 4 is because we need i-1
        warnings.warn(str(i))

        # adder circuit
        adder = test_circuits.adder_only_cnots(i)
        icm_circ, flag_circ = compile_circuits(adder, size=i, apply_jabalizer=True)
        # for the adder there is a single sample circuit, because this one is not a random one
        save_circuits(f"adder_{i}_{0}", icm_circ, flag_circ, path)

        for j in range(number_of_bench_samples):

            # benchmark circuits
            b1 = test_circuits.circuit_generator_1(i, edge_probability, remove_hadamards)
            b2 = test_circuits.circuit_generator_2(i, edge_probability, remove_hadamards)
            b3 = test_circuits.circuit_generator_3(i, edge_probability, remove_hadamards)

            icm_circ, flag_circ = compile_circuits(b1, size=i, apply_jabalizer=False)
            save_circuits(f"b1_{i}_{j}", icm_circ, flag_circ, path)

            icm_circ, flag_circ = compile_circuits(b2, size=i, apply_jabalizer=False)
            save_circuits(f"b2_{i}_{j}", icm_circ, flag_circ, path)

            icm_circ, flag_circ = compile_circuits(b3, size=i, apply_jabalizer=False)
            save_circuits(f"b3_{i}_{j}", icm_circ, flag_circ, path)

