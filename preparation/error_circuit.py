import cirq
import itertools
from typing import List
import cirq.circuits.circuit
import numpy as np


class XError(cirq.Gate):
    def __init__(self):
        super().__init__()

    def num_qubits(self) -> int:
        return 1

    def _circuit_diagram_info_(self, args):
        return "x_error"

    def _unitary_(self):
        return np.array([
            [0, 1],
            [1, 0]
        ])

    def validate_args(self, qubit):
        pass


class ZError(cirq.Gate):
    def __init__(self):
        super().__init__()

    def num_qubits(self) -> int:
        return 1

    def _circuit_diagram_info_(self, args):
        return "z_error"

    def _unitary_(self):
        return np.array([
            [1, 0],
            [0, -1]
        ])

    def validate_args(self, qubit):
        pass


# A class that represent error location and allows us to cancel out identical error
class ErrorLocation:
    def __init__(self, qubit: cirq.NamedQubit, moment: cirq.Moment):
        self.qubit = qubit
        self.moment = moment


# this is quite problem matric
def generate_error_string(number_of_error):
    errors = list(itertools.product('xz', repeat=number_of_error))
    return errors


# THis is a refactored function for create_error_moments:
def error_at_moments(errors_string, location: List[ErrorLocation]):
    def helper(error_char, qubit):
        if error_char == 'x':
            x_error_gate = XError()
            x_error_op = x_error_gate.on(qubit)
            moment = cirq.Moment(x_error_op)
            return moment
        elif error_char == 'z':
            z_error_gate = ZError()
            z_error_op = z_error_gate.on(qubit)
            moment = cirq.Moment(z_error_op)
            return moment

    def helper2(error_char, qubit):
        if error_char == 'x':
            x_error_gate = cirq.X
            x_error_op = x_error_gate.on(qubit)
            moment = cirq.Moment(x_error_op)
            return moment
        elif error_char == 'z':
            z_error_gate = cirq.Z
            z_error_op = z_error_gate.on(qubit)
            moment = cirq.Moment(z_error_op)
            return moment

    return [list(map(lambda a, b: helper(a, b.qubit), errors_string, location)),
            list(map(lambda a, b: helper2(a, b.qubit), errors_string, location))]


def generate_input_error_with_flags(circuit: cirq.Circuit, number_of_error: int, strategy="all"):
    result = []

    # NEW!: errors also on flags
    qubits = list(circuit.all_qubits())

    locations = list(map(lambda q: ErrorLocation(q, 0), qubits))
    # location should always be 4
    combination_of_locations = list(itertools.combinations_with_replacement(list(locations), number_of_error))
    error_string = generate_error_string(number_of_error)
    if strategy == "all":
        for e in error_string:
            for cl in combination_of_locations:
                # ERROR_CIR AND ERROR CI2 IS basically the same
                error_cir = cirq.Circuit()
                error_cir2 = cirq.Circuit()
                error1, error2 = error_at_moments(e, cl)
                for m in error1:
                    error_cir.append(m)
                for m in error2:
                    error_cir2.append(m)
                result.append([error_cir + circuit, error_cir2 + circuit])
    return result


def generate_input_error_without_flags(circuit: cirq.Circuit, number_of_error: int, strategy="all"):
    result = []

    def next_to_a_flag(cir: cirq.Circuit):
        helper = cir.moments[0].operations[0].qubits
        for q in helper:
            q: cirq.NamedQubit
            if 'f' in q.name:
                return True
        return False

    qubits = list(filter(lambda q: 'f' not in q.name, circuit.all_qubits()))
    if next_to_a_flag(circuit):
        qubits = []

    locations = list(map(lambda q: ErrorLocation(q, 0), qubits))
    # location should always be 4
    combination_of_locations = list(itertools.combinations_with_replacement(list(locations), number_of_error))
    error_string = generate_error_string(number_of_error)
    if strategy == "all":
        for e in error_string:
            for cl in combination_of_locations:
                # ERROR_CIR AND ERROR CI2 IS basically the same
                error_cir = cirq.Circuit()
                error_cir2 = cirq.Circuit()
                error1, error2 = error_at_moments(e, cl)
                for m in error1:
                    error_cir.append(m)
                for m in error2:
                    error_cir2.append(m)
                result.append([error_cir + circuit, error_cir2 + circuit])
    return result



def generate_error_circuit_without_flags(circuit: cirq.Circuit, number_of_error: int):
    result = []
    moments = list(circuit.moments)

    def next_to_a_flag(cir):
        helper = cir.moments[0].operations[0].qubits
        for q in helper:
            q: cirq.NamedQubit
            if 'f' in q.name:
                return True
        return False

    for i in range(len(moments)):
        # we divide the moment into two part
        first_part = moments[:i]
        second_part = moments[-len(moments) + i:]

        circuit1 = cirq.Circuit()
        circuit1.append(first_part)

        circuit2 = cirq.Circuit()
        circuit2.append(second_part)

        # should I make some change so there will be more errors
        if not next_to_a_flag(circuit2):
            circuit2 = generate_input_error_without_flags(circuit2, number_of_error)
            for c in circuit2:
                result.append([circuit1 + c[0], circuit1 + c[1]])
            
    return result

# new! adds errors also on flags
def generate_error_circuit_with_flags(circuit: cirq.Circuit, number_of_error: int):
    result = []
    moments = list(circuit.moments)

    for i in range(len(moments)):
        # we divide the moment into two part
        first_part = moments[:i]
        second_part = moments[-len(moments) + i:]

        circuit1 = cirq.Circuit()
        circuit1.append(first_part)

        circuit2 = cirq.Circuit()
        circuit2.append(second_part)

        circuit2 = generate_input_error_with_flags(circuit2, number_of_error)
        for c in circuit2:
            result.append([circuit1 + c[0], circuit1 + c[1]])
            
    return result
    

def generate_handlable_error_circuits(circuit: cirq.Circuit):
    result = []
    moments = list(circuit.moments)
        
    # find flags' target qubits
    x_flag_targets = []
    z_flag_targets = []
    x_flag_cnots = []
    z_flag_cnots = []
    for i in range(len(moments)):
        m = moments[i]
        op = m.operations[0]
        if isinstance(op.gate, cirq.CXPowGate):
            qubit1 = op.qubits[0]
            qubit2 = op.qubits[1]
            if "xf" in qubit1.name:
                x_flag_targets.append(qubit2)
                tup = (qubit1, i, qubit2)
                x_flag_cnots.append(tup)

            elif "zf" in qubit1.name:
                z_flag_targets.append(qubit2)
                tup = (qubit1, i, qubit2)
                z_flag_cnots.append(tup)

            elif "xf" in qubit2.name:
                x_flag_targets.append(qubit1)
                tup = (qubit2, i, qubit1)
                x_flag_cnots.append(tup)

            elif "zf" in qubit2.name:
                z_flag_targets.append(qubit1)
                tup = (qubit2, i, qubit1)
                z_flag_cnots.append(tup)

    # group by flag qubit to get flag end and start moment
    x_flag_cnots.sort(key = lambda a: a[0])
    x_flag_grouped = itertools.groupby(x_flag_cnots, lambda a: a[0])

    z_flag_cnots.sort(key = lambda a: a[0])
    z_flag_grouped = itertools.groupby(z_flag_cnots, lambda a: a[0])

    # create all error circuits that the flags are able to handle:
    for k, g in x_flag_grouped:
        f = k
        indices = [item for item in g]
        i = indices[0][1]
        j = indices[1][1]
        ij = j - i # assuming j is bigger
        q = indices[0][2]

        # divide moments
        for s in range(ij):
            first_part = moments[:(i + s + 1)]
            second_part = moments[(j - (ij - s) + 1):]

            circuit1 = cirq.Circuit()
            circuit1.append(first_part)

            circuit2 = cirq.Circuit()
            circuit2.append(second_part)

            # insert error on target
            circuit1.append(cirq.X(q))

            circuit1.append(circuit2)
            result.append(circuit1)

    for k, g in z_flag_grouped:
        f = k
        indices = [item for item in g]
        i = indices[0][1]
        j = indices[1][1]
        ij = j - i # assuming j is bigger
        q = indices[0][2]

        # divide moments
        for s in range(ij):
            first_part = moments[:(i + s + 1)]
            second_part = moments[(j - (ij - s) + 1):]

            circuit1 = cirq.Circuit()
            circuit1.append(first_part)

            circuit2 = cirq.Circuit()
            circuit2.append(second_part)

            # insert error on target
            circuit1.append(cirq.Z(q))
            
            circuit1.append(circuit2)
            result.append(circuit1)

    return result