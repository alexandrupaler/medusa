import cirq
import cirq.circuits
import qualtran
import qualtran._infra
import qualtran._infra.gate_with_registers
import qualtran.bloqs
import qualtran.bloqs.arithmetic
import numpy as np

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

def remove_t_gates(op: cirq.Operation) -> cirq.OP_TREE:
    if not isinstance(op.gate, cirq.ZPowGate):
        yield op
    elif not (op.gate.exponent == 0.25) and not op.gate.exponent == -0.25:
        yield op

def prepare_adder_for_jabalizer(circuit: cirq.Circuit, with_t_gates=False):

    # no classical, cz -> h cx h, remove m & r
    circuit = circuit.map_operations(cla_map)
    circuit = circuit.map_operations(map_func)

    if not with_t_gates:
        circuit = circuit.map_operations(remove_t_gates)

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


def adder(size: int, with_t_gates=False):

    bloq = qualtran.bloqs.arithmetic.Add(qualtran.QUInt(size))
    circuit = get_clifford_plus_t_cirq_circuit_for_bloq(bloq)
    circuit = prepare_adder_for_jabalizer(circuit,with_t_gates)

    return circuit

def adder_only_cnots(size: int,with_t_gates=False):
    circuit = adder(size,with_t_gates)

    def wihtout_H(op: cirq.Operation) -> cirq.OP_TREE:
        if not isinstance(op.gate, cirq.HPowGate):
            yield op

    circuit = circuit.map_operations(wihtout_H)

    return circuit

# for now let's assume max 1 edge between nodes
def graph_state(qubits: int, edge_probability: float, remove_hadamards: float):

    # generate graph state as a matrix based on the number of qubits and the density of edges
    matrix_top = np.zeros((qubits,qubits))

    for q in range(qubits):
        edges_for_q = np.random.choice([0,1], qubits - 1 - q, p=[1 - edge_probability, edge_probability])
        matrix_top[q,(q+1):qubits] = edges_for_q

    # there is technically no need to obtain the full matrix ?
    #full_matrix = matrix_top + np.transpose(matrix_top)
    #print(full_matrix)


    # create quantum circuit based on the graph state by substituting the edges with CZ gates
    graph_circuit = cirq.Circuit()
    cirq_qubits = cirq.LineQubit.range(qubits)

    # probability to flip snots
    flip_cx_p = 0.5

    def add_hadamard():
        return np.random.choice([False,True], 1, p=[remove_hadamards, 1 - remove_hadamards])
    
    def flip_cx():
        return np.random.choice([False,True], 1, p=[1 - flip_cx_p, flip_cx_p])
    
    for q in range(qubits):
        for j in range(q+1,qubits):
            if matrix_top[q,j] == 1:
                # add CZ gate as H CX H but don't add the hadamards based on the input probability
                # + flip the CX based on probability defined above
                if add_hadamard():
                    graph_circuit.append(cirq.H(cirq_qubits[q]))

                if flip_cx():
                    graph_circuit.append(cirq.CX(cirq_qubits[q], cirq_qubits[j]))
                else:
                    graph_circuit.append(cirq.CX(cirq_qubits[j], cirq_qubits[q]))
                    
                if add_hadamard():
                    graph_circuit.append(cirq.H(cirq_qubits[q]))

    return graph_circuit
    
    

