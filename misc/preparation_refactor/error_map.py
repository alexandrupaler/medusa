import itertools
import cirq
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from cirq import NamedQubit

from preparation.error_location import  Single_Error, ErrorLocation


class Error_Map:
    def __is_moment_with_cnot__(self, momnet: cirq.Moment):
        for op in momnet.operations:
            if len(op.qubits) == 2:
                return True
        return False

    def __init__(self, circuit: cirq.Circuit):
        self.circuit = circuit
        self.qubits = list(circuit.all_qubits())
        self.num_qubits = len(self.qubits)
        self.map_size = len(circuit.moments)
        #NOT ideal use
        self.X_propagation_map = {qubit: {} for qubit in self.qubits}
        self.Z_propagation_map = {qubit: {} for qubit in self.qubits}

        self.Error_Locations = []


    def create_map(self, channel_strength:float ):
        reversed_moments = list(reversed(self.circuit.moments))
        for i,moment in enumerate(reversed_moments):
            for qubit in self.qubits:
                index= len(reversed_moments)-1-i
                if moment.operates_on([qubit]):
                    self.X_propagation_map[qubit][id(moment)]= Single_Error(qubit, moment, index, channel_strength)
                else:
                    self.X_propagation_map[qubit][id(moment)]= Single_Error(qubit, moment, index, error_rate=0)
                if i > 0:
                    next_moment = reversed_moments[i - 1]
                    self.X_propagation_map[qubit][id(moment)].propagate(self.X_propagation_map[qubit][id(next_moment)])
                else:
                    self.X_propagation_map[qubit][id(moment)].propagated_to.append((qubit,id(moment)))


            for op in moment.operations:
                next_moment:cirq.Moment
                if i > 0:
                    next_moment = reversed_moments[i - 1]
                else:
                    continue
                if len(op.qubits) == 2:
                    control, target = op.qubits
                    self.X_propagation_map[control][id(moment)].propagate(self.X_propagation_map[target][id(next_moment)])

        for qubit in self.qubits:
            errors = []
            for moment in self.circuit.moments:
                op = moment.operation_at(qubit)
                if op is not None:
                    if len(op.qubits) == 1 or (len(op.qubits) == 2 and qubit == op.qubits[1]):
                        if len(errors) > 0:
                            self.Error_Locations.append(ErrorLocation(errors))
                        errors = []
                    else:
                        errors.append(self.X_propagation_map[qubit][id(moment)])
                else:
                    errors.append(self.X_propagation_map[qubit][id(moment)])

            if len(errors) > 0:
                self.Error_Locations.append(ErrorLocation(errors))

        return [self.X_propagation_map, self.Z_propagation_map]



    ##create map for combination of two error
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

    ## find the exact

class Error_Map_2:
    pass







