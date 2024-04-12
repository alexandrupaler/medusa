import cirq


def test_circuit():
    q0, q1, q2, q3 = [cirq.LineQubit(i) for i in range(4)]
    circuit = cirq.Circuit()
    circuit.append(cirq.T(q1))
    circuit.append(cirq.CNOT(q0, q2))
    circuit.append(cirq.CNOT(q0, q2))
    circuit.append(cirq.CNOT(q3, q1))
    return circuit


def toffoli():
    qubits = [cirq.LineQubit(i) for i in range(3)]
    cirq_circuit = cirq.Circuit()
    cirq_circuit.append(cirq.CCNOT(*qubits))
    ct_circuit = cirq.Circuit(cirq.decompose(cirq_circuit, keep=self.keep_clifford_plus_T))
    return ct_circuit


def powerpoint_circuit():
    circuit = cirq.Circuit()
    q0, q1 = [cirq.LineQubit(i) for i in range(2)]
    circuit.append(cirq.CNOT(q0, q1))
    return circuit


def test_circuit2():
    qf, q1, q2, q3 = [cirq.LineQubit(i) for i in range(4)]
    circuit = cirq.Circuit()
    circuit.append([cirq.T(q3), cirq.CNOT(q1, q2)])
    circuit.append(cirq.CNOT(q1, q3))
    circuit.append(cirq.CNOT(q1, q2))
    return circuit

