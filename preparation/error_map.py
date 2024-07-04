import itertools
import cirq
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


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
        self.num_moment_with_cnot = len(self.moment_with_cnot)
        self.num_qubits = len(self.qubits)
        self.map_size = len(self.moment_with_cnot)
        self.X_propagation_map = {}
        self.Z_propagation_map = {}
        self.X_error_map = np.zeros(shape=(self.num_qubits,self.num_moment_with_cnot))
        self.Z_error_map = np.zeros(shape=(self.num_qubits,self.num_moment_with_cnot))


    def create_map(self):
        #what does this line do what Tf have I done ?
        #self.moment_with_cnot.reverse()
        # take len(moment) step

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

        #for key, val in self.X_map.items():
            #print("moments:", key[1], val)
        return [self.X_propagation_map, self.Z_propagation_map]

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
    def create_error_map(self, p: float):
        qubits_with_index = dict(zip(self.qubits, range(self.num_qubits)))
        moments_with_index = dict(zip(self.moment_with_cnot, range(self.num_moment_with_cnot)))

        for m in self.moment_with_cnot:
            c = moments_with_index[m]
            print(c)
            m: cirq.Moment
            if c == 0:
                for r, q in enumerate(self.qubits):
                    q: cirq.NamedQubit
                    self.X_error_map[r] = [p]

            for q in self.qubits:
                q: cirq.NamedQubit
                r_q = qubits_with_index[q]
                control = None
                for op in m.operations:
                    if op.qubits[1] == q:
                        control = op.qubits[0]

                if control is None:
                    p_odd_q = self.X_error_map[r_q][c-1]
                    error_accumulated_prob = p_odd_q*(1-p) + (1-p_odd_q)*p
                    self.X_error_map[r_q][c] = error_accumulated_prob
                else:
                    r_c = qubits_with_index[control]
                    p_odd_q = self.X_error_map[r_q][c-1]
                    p_odd_c = self.X_error_map[r_c][c-1]
                    error_accumulated_prob = p_odd_q*p_odd_q*p + (1-p_odd_q)*p_odd_c*(1-p) + p_odd_q*(1-p_odd_c)*(1-p)+ (1-p_odd_q)*(1-p_odd_c)*p
                    self.X_error_map[r_q][c] = error_accumulated_prob

    def plot_error_map(self):
        plt.figure(figsize=(10, 8))
        plt.imshow(self.X_error_map, cmap='viridis', aspect='auto')
        plt.colorbar(label='Error Rate')
        plt.title('Error Map Heatmap')
        plt.xlabel('Moments with CNOT')
        plt.ylabel('Qubits')
        plt.xticks(ticks=np.arange(self.num_moment_with_cnot), labels=np.arange(1, self.num_moment_with_cnot + 1))
        plt.yticks(ticks=np.arange(self.num_qubits), labels=self.qubits)
        plt.show()








