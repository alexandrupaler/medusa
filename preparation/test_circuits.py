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
        num = 0
        numstr = str(ord(name[0])) # + (10 * (int(name[1]) + 1))
        for i in range(1, len(name)):
            numstr += str(name[i])
        num = int(numstr)
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


# helpers for generating circuits:
#chance of removing/adding hadamard gate
def add_hadamard(remove_hadamards):
    return np.random.choice([False,True], 1, p=[remove_hadamards, 1 - remove_hadamards])

#chance of flipping cnot
def flip_cx(flip_cx_p = 0.5):
    return np.random.choice([False,True], 1, p=[1 - flip_cx_p, flip_cx_p])

# change CZ to H CX H and remove some H gates
def CZ_to_H_CNOT_H(circuit: cirq.Circuit, remove_hadamards):

    def map_cz(op: cirq.Operation) -> cirq.OP_TREE:
        if isinstance(op.gate, cirq.CZPowGate):

            c = 0
            t = 1
            if flip_cx():
                c = 1
                t = 0

            if add_hadamard(remove_hadamards):
                yield cirq.H(op.qubits[t])
            
            yield cirq.CX(op.qubits[c], op.qubits[t])

            if add_hadamard(remove_hadamards):
                yield cirq.H(op.qubits[t])

        else:
            yield op
    
    return circuit.map_operations(map_cz)

# remove double hadamards
def merge_func(op1: cirq.Operation, op2: cirq.Operation):
    if isinstance(op1.gate, cirq.HPowGate) and isinstance(op2.gate, cirq.HPowGate) and op1.qubits == op2.qubits:
        return cirq.I(*op1.qubits)
    else:
        return None

# generate graph state as a matrix based on the number of qubits and the density of edges
def graph_state(qubits: int, edge_probability: float):

    matrix_top = np.zeros((qubits,qubits))

    for q in range(qubits):
        edges_for_q = np.random.choice([0,1], qubits - 1 - q, p=[1 - edge_probability, edge_probability])
        matrix_top[q,(q+1):qubits] = edges_for_q

    # there is technically no need to obtain the full matrix ?
    #full_matrix = matrix_top + np.transpose(matrix_top)
    #print(full_matrix)

    print(matrix_top)
    return matrix_top

# create quantum circuit based on the graph state by substituting the edges with CZ gates
def edges_to_CZ(qubits: int, edge_probability: float):

    # get state
    matrix_top = graph_state(qubits, edge_probability)

    graph_circuit = cirq.Circuit()
    cirq_qubits = cirq.LineQubit.range(qubits)
    
    for q in range(qubits):
        for j in range(q+1,qubits):
            if matrix_top[q,j] == 1:
                graph_circuit.append(cirq.CZ(cirq_qubits[q], cirq_qubits[j]), strategy=cirq.InsertStrategy.NEW_THEN_INLINE)

    return graph_circuit


# cascading shape
def circuit_generator_1(qubits: int, edge_probability: float, remove_hadamards: float):

    graph_circuit = edges_to_CZ(qubits, edge_probability)

    # replace cz with h cx h
    graph_circuit = CZ_to_H_CNOT_H(graph_circuit, remove_hadamards)

    # remove double hadamards
    final_circuit = cirq.merge_operations(graph_circuit, merge_func)
    final_circuit = cirq.drop_negligible_operations(final_circuit)
    final_circuit = cirq.drop_empty_moments(final_circuit)

    return graph_circuit


# rough zig zag shape
def circuit_generator_2(qubits: int, edge_probability: float, remove_hadamards: float):

    graph_circuit = edges_to_CZ(qubits, edge_probability)

    moments = list(graph_circuit.moments)
    num_moments = len(list(graph_circuit.moments))
    
    moments_front = np.array(range(num_moments // 2))
    moments_back = np.array(range(num_moments // 2, num_moments))
    moments_back = np.flip(moments_back)

    final_circuit = cirq.Circuit()

    i = 0
    j = 0
    for m in range(num_moments):
        if m % 2 != 0:
            a = moments_front[i]
            final_circuit.append(moments[a])
            i += 1
        else:
            a = moments_back[j]
            final_circuit.append(moments[a])
            j += 1

    final_circuit = CZ_to_H_CNOT_H(final_circuit, remove_hadamards)

    # remove double hadamards
    final_circuit = cirq.merge_operations(final_circuit, merge_func)
    final_circuit = cirq.drop_negligible_operations(final_circuit)
    final_circuit = cirq.drop_empty_moments(final_circuit)

    return final_circuit    

# v shape
def circuit_generator_3(qubits: int, edge_probability: float, remove_hadamards: float):

    graph_circuit = edges_to_CZ(qubits, edge_probability)

    all_moments = list(graph_circuit.moments)
    all_qubits = list(graph_circuit.all_qubits())    

    def sortqubits(q: cirq.LineQubit):
        return q._comparison_key()
    
    all_qubits.sort(key=sortqubits)


    # assuming each moment has exactly 1 CZ
    def touches_q(q, moment: cirq.Moment):
        op = moment._operations
        op = op[0]
        return op.qubits[0] == q
    
    circuit_front = cirq.Circuit()
    circuit_back = cirq.Circuit()

    for q in all_qubits:
        moments_with_q = list(filter(lambda m: touches_q(q, m), all_moments))

        num_moments = len(moments_with_q)

        moments_front = moments_with_q[0:(num_moments // 2)]
        circuit_front.append(moments_front, strategy=cirq.InsertStrategy.NEW)

        moments_back = moments_with_q[(num_moments // 2):num_moments]
        circuit_back.append(moments_back, strategy=cirq.InsertStrategy.NEW)

    reversed_back = list(circuit_back.moments)[::-1]
    circuit_front.append(reversed_back,strategy=cirq.InsertStrategy.NEW)

    # from cz to h cx h
    final_circuit = CZ_to_H_CNOT_H(circuit_front, remove_hadamards)

    # remove double hadamards
    final_circuit = cirq.merge_operations(final_circuit, merge_func)
    final_circuit = cirq.drop_negligible_operations(final_circuit)
    final_circuit = cirq.drop_empty_moments(final_circuit)

    return final_circuit 


#transforms linequbits into namequbits
def line_to_named(circuit):

    def simple_map(q: cirq.Qid):
        return cirq.NamedQubit(str(q))

    return circuit.transform_qubits(qubit_map=simple_map)

