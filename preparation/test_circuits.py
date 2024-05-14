import cirq
import qualtran
import qualtran._infra
import qualtran._infra.gate_with_registers
import qualtran.bloqs
import qualtran.bloqs.arithmetic

# T dagger gate
TDag = cirq.ZPowGate(exponent=-0.25)

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


# taken from https://quantum-journal.org/papers/q-2019-05-20-143/

def logical_hadamard_1_noflags():
    q1, q2, q3, q4, q5, q6, q7 = [cirq.LineQubit(i) for i in range(7)]
    
    s1 = cirq.LineQubit(8888)
    f1 = cirq.LineQubit(7777)

    circuit = cirq.Circuit()

    # prepare state +
    circuit.append(cirq.H(s1))

    # logical hadamard(s)
    circuit.append(cirq.T(q7))
    circuit.append(cirq.H(q7))
    circuit.append(cirq.CNOT(s1,q7))
    circuit.append(cirq.H(q7))
    circuit.append(TDag(q7))

    # cnot to flag
    circuit.append(cirq.CNOT(s1, f1))

    # logical hadamard(s)

    circuit.append(cirq.T(q6))
    circuit.append(cirq.H(q6))
    circuit.append(cirq.CNOT(s1,q6))
    circuit.append(cirq.H(q6))
    circuit.append(TDag(q6))

    circuit.append(cirq.T(q5))
    circuit.append(cirq.H(q5))
    circuit.append(cirq.CNOT(s1,q5))
    circuit.append(cirq.H(q5))
    circuit.append(TDag(q5))

    circuit.append(cirq.T(q4))
    circuit.append(cirq.H(q4))
    circuit.append(cirq.CNOT(s1,q4))
    circuit.append(cirq.H(q4))
    circuit.append(TDag(q4))

    circuit.append(cirq.T(q3))
    circuit.append(cirq.H(q3))
    circuit.append(cirq.CNOT(s1,q3))
    circuit.append(cirq.H(q3))
    circuit.append(TDag(q3))

    circuit.append(cirq.T(q2))
    circuit.append(cirq.H(q2))
    circuit.append(cirq.CNOT(s1,q2))
    circuit.append(cirq.H(q2))
    circuit.append(TDag(q2))

    # cnot to flag
    circuit.append(cirq.CNOT(s1, f1))

    # logical hadamard(s)

    circuit.append(cirq.T(q1))
    circuit.append(cirq.H(q1))
    circuit.append(cirq.CNOT(s1,q1))
    circuit.append(cirq.H(q1))
    circuit.append(TDag(q1))

    # measure (we do this with the below function after the icm decomposition)
    #circuit.append(cirq.measure(f1))
    circuit.append(cirq.H(s1))
    #circuit.append(cirq.measure(s1))
   
    return circuit

def add_flags_to_test_hadamard(circuit: cirq.Circuit):

    def sortqubits(q):
        return q.name

    qubits = list(circuit.all_qubits())
    qubits.sort(key=sortqubits)

    # measure
    for q in qubits:
        # if flag
        #if "8888" in q.name or "7777" in q.name:
        #    circuit.append(cirq.measure(q))
        if "7777" in q.name:
            circuit.append(cirq.measure(q))

    return circuit


# adder, from: https://colab.research.google.com/drive/1ur7Y9e-QGEzQp634IIQGB-ssSd0ZzXdz?resourcekey=0-lhIK8QaBbngbogVWIohcqg#scrollTo=UVoF-PgwfmHW

clifford_plus_t_gateset = cirq.Gateset(
    cirq.X, cirq.Y, cirq.Z, cirq.S, cirq.T, cirq.H, cirq.T**-1,
    cirq.CX, cirq.CZ, cirq.MeasurementGate, cirq.ResetChannel
)

def keep(op: cirq.Operation):
    gate = op.without_classical_controls().gate
    ret = gate in clifford_plus_t_gateset
    if isinstance(gate, cirq.ops.raw_types._InverseCompositeGate):
        ret |= op.gate._original in clifford_plus_t_gateset
    return ret

def get_clifford_plus_t_cirq_circuit_for_bloq(bloq: qualtran.Bloq):
    circuit, _ = bloq.decompose_bloq().to_cirq_circuit(**qualtran._infra.gate_with_registers.get_named_qubits(bloq.signature.lefts()))
    context=cirq.DecompositionContext(qubit_manager=cirq.GreedyQubitManager(prefix='anc'))
    return cirq.Circuit(cirq.decompose(circuit, keep=keep, context=context))

# these map functions are needed so that jabalizer works as it doesn't support s, cz, measurement or reset gates
def map_func(op: cirq.Operation) -> cirq.OP_TREE:
    if isinstance(op.gate, cirq.CZPowGate):
        yield cirq.H(op.qubits[1])
        yield cirq.CNOT(op.qubits[0], op.qubits[1])
        yield cirq.H(op.qubits[1])
    elif isinstance(op.gate, cirq.ZPowGate) and op.gate.exponent == 0.5:
        yield cirq.T(op.qubits[0])
        yield cirq.T(op.qubits[0])
    elif not isinstance(op.gate, cirq.ResetChannel) and not isinstance(op.gate, cirq.MeasurementGate):
        yield op

def cla_map(op: cirq.Operation) -> cirq.OP_TREE:
    yield op.without_classical_controls()

def replace_t_with_Z_map(op: cirq.Operation) -> cirq.OP_TREE:
    if not isinstance(op.gate, cirq.ZPowGate) and not (op.gate.exponent == 0.25):
        yield op

def prepare_adder_for_jabalizer(circuit: cirq.Circuit):

    # no classical, cz -> h cx h, remove m & r
    circuit = circuit.map_operations(cla_map)
    circuit = circuit.map_operations(map_func)
    circuit = circuit.map_operations(replace_t_with_Z_map)

    # transforming cleanqubits to named qubits
    #name_map =  {cirq.ops.CleanQubit(0): cirq.NamedQubit("c0")}

    def name_map(q):
        if isinstance(q, cirq.ops.CleanQubit):
            num = q.id
            return cirq.NamedQubit("c" + str(num))
        else:
            return q

    def line_map(q: cirq.Qid):
        name = str(q)
        num = ord(name[0]) + (10 * (int(name[1]) + 1))
        return cirq.LineQubit(num)

    circuit = circuit.transform_qubits(qubit_map =name_map)
    # named qubits to linequbits
    circuit = circuit.transform_qubits(qubit_map =line_map)

    return circuit


def adder(size: int):

    bloq = qualtran.bloqs.arithmetic.Add(qualtran.QUInt(size))
    circuit = get_clifford_plus_t_cirq_circuit_for_bloq(bloq)
    circuit = prepare_adder_for_jabalizer(circuit)

    return circuit
