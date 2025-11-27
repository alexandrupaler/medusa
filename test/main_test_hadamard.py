import cirq.circuits
import cirq
import matplotlib.pyplot as plt
from preparation import compiler
from evaluation import evaluate


if __name__ == '__main__':

    def create_circuits(hadamards):

        icm_circuit = cirq.Circuit()
        flag_circuit = cirq.Circuit()

        f = cirq.NamedQubit("0xf")
        q = cirq.NamedQubit("1")


        flag_circuit.append(cirq.CNOT(q,f),strategy=cirq.InsertStrategy.NEW_THEN_INLINE)

        if hadamards:
            flag_circuit.append(cirq.H(q),strategy=cirq.InsertStrategy.NEW_THEN_INLINE)
            icm_circuit.append(cirq.H(q),strategy=cirq.InsertStrategy.NEW_THEN_INLINE)
        else:
            flag_circuit.append(cirq.I(q),strategy=cirq.InsertStrategy.NEW_THEN_INLINE)
            icm_circuit.append(cirq.I(q),strategy=cirq.InsertStrategy.NEW_THEN_INLINE)

        flag_circuit.append(cirq.CNOT(q,f),strategy=cirq.InsertStrategy.NEW_THEN_INLINE)
        flag_circuit.append(cirq.measure(f),strategy=cirq.InsertStrategy.NEW_THEN_INLINE)
        flag_circuit.append(cirq.reset(f),strategy=cirq.InsertStrategy.NEW_THEN_INLINE)

        return icm_circuit, flag_circuit


    c = compiler.FlagCompiler()

    hadamard_icm, hadamard_flag = create_circuits(hadamards=True)
    nohadamard_icm, nohadamard_flag = create_circuits(hadamards=True)
    
    number_of_runs = 1000
    error_rates = [0.0001, 0.0002, 0.0004, 0.0008, 0.001, 0.00125, 0.0025, 0.005, 0.01]

    had_res, had_res_icm, a, b, c = evaluate.stabilizers_robustness_and_logical_error(hadamard_icm, hadamard_flag, number_of_runs, error_rates, False, "", noise_type="perfect flags")
    nohad_res, nohad_res_icm, a, b, c = evaluate.stabilizers_robustness_and_logical_error(hadamard_icm, hadamard_flag, number_of_runs, error_rates, False, "", noise_type="perfect flags")

    plt.title("hadamard test")

    plt.loglog(error_rates, had_res, label="hadamard flag")
    plt.loglog(error_rates, had_res_icm, label="hadamard icm")

    plt.loglog(error_rates, nohad_res, label="no hadamard flag")
    plt.loglog(error_rates, nohad_res_icm, label="no hadamard icm")

    plt.xlabel('noise channel strength')
    plt.ylabel('logical error rate')
    plt.legend()
    filename = "hadamardtest.png"
    plt.savefig(filename)
    plt.close()


