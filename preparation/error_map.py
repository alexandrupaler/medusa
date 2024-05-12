import itertools

import cirq
from concurrent.futures import ThreadPoolExecutor
from functools import reduce


class Error_Map:
    def __is_moment_with_cnot__(self, momnet: cirq.Moment):
        for op in momnet.operations:
            if len(op.qubits) == 2:
                return True
        return False

    def __init__(self, circuit: cirq.Circuit):
        self.circuit = circuit
        self.moment_with_cnot = list(filter(lambda m: self.__is_moment_with_cnot__(m), list(circuit.moments)))
        self.qubits = list(circuit.all_qubits())
        self.map_size = len(self.moment_with_cnot)
        self.X_map = {}
        self.Z_map = {}

    def create_map(self):
        # THere is a problem with index
        self.moment_with_cnot.reverse()
        # take len(moment) step
        distinct_x_error = []
        distinct_z_error = []
        for i, moment in enumerate(self.moment_with_cnot):
            index = self.map_size - i - 1
            moment: cirq.Moment
            control, target = moment.operations[0].qubits
            # take w (w is width) step
            for qubit in self.qubits:
                qubit: cirq.NamedQubit
                control: cirq.NamedQubit
                target: cirq.NamedQubit
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
                        for e in self.X_map[tuple(error)]:
                            propagated_x_error.append(e)
                    for error in helper2:
                        for e in self.Z_map[tuple(error)]:
                            propagated_z_error.append(e)
                # this two line below is bad and could be removed
                propagated_x_error = [e for e in propagated_x_error if propagated_x_error.count(e) % 2 == 1]
                propagated_z_error = [e for e in propagated_z_error if propagated_z_error.count(e) % 2 == 1]

                self.X_map[tuple(original_error)] = propagated_x_error
                self.Z_map[tuple(original_error)] = propagated_z_error
            #print("")
            #print("map for 1 error:")

        for key, val in self.X_map.copy().items():
            if key not in distinct_x_error:
                del self.X_map[key]
        for key, val in self.Z_map.copy().items():
            if key not in distinct_z_error:
                del self.Z_map[key]

        #for key, val in self.X_map.items():
            #print("moments:", key[1], val)
        return [self.X_map, self.Z_map]

    def create_map_2(self, max_error):
        x_map = self.create_map()[0]
        result = {}
        for keys in list(itertools.combinations_with_replacement(x_map.keys(), max_error)):
            helper = []
            for k in keys:
                helper += x_map[k]
            value = []
            for e in helper:
                if helper.count(e) % 2 == 1 and e not in value:
                    value.append(e)

            if len(value) > max_error:
                result[tuple(keys)] = value
        #print("map for", max_error, " errors")

        for key, val in result.items():
            h = list(map(lambda m: m[1], key))
            #print("moments:", h, "   ", val)

        return result
