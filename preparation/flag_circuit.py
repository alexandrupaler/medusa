import cirq
from flag_qubits import  ZFlagQubit,XFlagQubit

class FlagCircuit(cirq.Circuit):
    def __is_icm_circuit__(self):
        return True
    def __new__(cls, circuit):
        self = super().__new__(cls)
        self.original_circuit = circuit
        self.number_of_flag = 0
        self.zf_qubit = []
        self.xf_qubit = []
        self.bad_cnot = self.find_bad_cnot()
        pass

    def add_x_flag(self, locations: dict[(cirq.Qid,cirq.Moment)], in_place=False) -> cirq.Circuit:
        pass

    def add_z_flag(self, locations: dict[(cirq.Qid,cirq.Moment)], in_place=False) -> cirq.Circuit:
        pass

    def create_map(self):
        distinct_x_error = []
        distinct_z_error = []
        for i, moment in enumerate(self.moment_with_cnot):
            index = self.map_size - i - 1
            moment: cirq.Moment
            for op in moment.operations:
                control: cirq.NamedQubit
                target: cirq.NamedQubit
                control, target = op.qubits

                for qubit in self.qubits:
                    qubit: cirq.NamedQubit
                    original_error = (qubit, index)
                    propagated_x_error = [(qubit, index + 1)]
                    propagated_z_error = [(qubit, index + 1)]

                    if control == qubit:
                        distinct_x_error.append(tuple(original_error))
                        propagated_x_error.append((target, index + 1))
                    elif target == qubit:
                        distinct_z_error.append(tuple(original_error))
                        propagated_z_error.append((control, index + 1))

                    # we will query the dictionary to update the result
                    helper1 = propagated_x_error
                    helper2 = propagated_z_error

                    # this can be changed to take O(w^2) -maybe
                    if not index + 1 == self.map_size:
                        propagated_x_error = []
                        propagated_z_error = []
                        for error in helper1:
                            for e in self.X_propagation_map[tuple(error)]:
                                propagated_x_error.append(e)
                        for error in helper2:
                            for e in self.Z_propagation_map[tuple(error)]:
                                propagated_z_error.append(e)
                    # this two line below is bad and could be removed
                    propagated_x_error = [e for e in propagated_x_error if propagated_x_error.count(e) % 2 == 1]
                    propagated_z_error = [e for e in propagated_z_error if propagated_z_error.count(e) % 2 == 1]

                    self.X_propagation_map[tuple(original_error)] = propagated_x_error
                    self.Z_propagation_map[tuple(original_error)] = propagated_z_error
            #print("")
            #print("map for 1 error:")

        for key, val in self.X_propagation_map.copy().items():
            if key not in distinct_x_error:
                del self.X_propagation_map[key]
        for key, val in self.Z_propagation_map.copy().items():
            if key not in distinct_z_error:
                del self.Z_propagation_map[key]

        #for key, val in self.X_propagation_map.items():
        #    print("moments:", key[1], val)
        return [self.X_propagation_map, self.Z_propagation_map]




