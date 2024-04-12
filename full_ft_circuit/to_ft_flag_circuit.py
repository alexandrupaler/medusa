import cirq
class qubit_block:
    block_id = 0
    #TODO:move qubits to init
    def __init__(self, qubits, stab_code):
        self.qubits = qubits
        self.sydrome_ancilla = cirq.NamedQubit(str(self.block_id)+"a")
        self.stab_code = stab_code
        self.qubits = cirq.NamedQubit.range(len(stab_code[0]), prefix=str(self.block_id))
        self.number_of_flag_created = 0
        qubit_block.block_id += 1

    def create_flag(self,amount_of_flag):
        flags =cirq.NamedQubit.range(amount_of_flag, prefix=str(self.block_id-1) + "f")
        self.number_of_flag_created += 1
        return flags

#TODO:Need bariier
class ft_measurement:
    pass

def ft_gate(qubit_blocks:list[qubit_block], stab_code, gate:cirq.Gate):
    def tranversal_gate():
        gates = []
        if len(qubit_blocks) == 1:
            for qubit in qubit_blocks[0].qubits:
                gates.append(gate.on(qubit))
        elif len(qubit_blocks) == 2:
            print(gate.num_qubits())
            pairs = zip(qubit_blocks[0].qubits, qubit_blocks[1].qubits)
            for pair in pairs:
                print(pair[0], pair[1])
                gates.append(gate.on(pair[0], pair[1]))
        return gates

    def sydrome_measurements(add_flag= True):

        #TODO:Find a way to match in pyhthon
        def gate_matching(gate_name,qubit,block:qubit_block):
            if gate_name == 'X':
                return cirq.X.controlled(1).on(block.sydrome_ancilla,qubit)
            elif gate_name == 'Z':
                return cirq.Z.controlled(1).on(block.sydrome_ancilla,qubit)
            else:
                return None

        result = []
        for block in qubit_blocks:
            for stabilizer in stab_code:
                result.append(cirq.H.on(block.sydrome_ancilla))
                gates_name = list(stabilizer)
                gates_name_and_qubit = zip(gates_name,block.qubits)
                gates = list(map(lambda g: gate_matching(g[0], g[1], block), gates_name_and_qubit))
                flags_qubits = block.create_flag(2)
                for g in gates:
                    if g != None:
                        if add_flag:
                            #TODO:change amount of flag
                            for f in flags_qubits:
                                result.append(cirq.CNOT(block.sydrome_ancilla,f))
                            result.append(g)
                            for f in flags_qubits:
                                result.append(cirq.CNOT(block.sydrome_ancilla,f))
                                result.append(cirq.measure(f))
                        else:
                            result.append(g)

                result.append(cirq.H.on(block.sydrome_ancilla))
                result.append(cirq.measure(block.sydrome_ancilla))
                result.append(cirq.reset(block.sydrome_ancilla))
        return result


    return [tranversal_gate(), sydrome_measurements()]



def encode(circuit: cirq.Circuit, stab_code):
    qubit_blocks = []
    qubits = circuit.all_qubits()
    new_circuit =cirq.Circuit()
    for qubit in qubits:
        qubit_blocks.append(qubit_block(qubit, stab_code))
    qubit_blocks = list(zip(qubits, qubit_blocks))
    for q in qubit_blocks:
        print(q[0])



    for moment in circuit:
        moment: cirq.Moment
        for op in moment:
            op: cirq.Operation
            print(op.qubits)

            def is_op_target_to_encoded_qubit(q):
                if q in op.qubits:
                    return True
                else:
                    return False
            blocks = list( filter(lambda block:  is_op_target_to_encoded_qubit(block[0]), qubit_blocks))
            blocks = list(map(lambda item: item[1], blocks))
            ft_gates = ft_gate( blocks, stab_code,op.gate)
            print(ft_gates)
            for gate_block in ft_gates:
                print(gate_block)
                new_circuit.append(gate_block, strategy=cirq.InsertStrategy.NEW_THEN_INLINE)



    return  new_circuit

# TODO: Step2: Replace
