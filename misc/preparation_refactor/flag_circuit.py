import cirq
from preparation.flag_qubits import ZFlagQubit,XFlagQubit
from preparation.error_map import Error_Map
from preparation.error_location import ErrorLocation

class FlagCircuit():
    def __is_icm_circuit__(self):
        return True

    # THIS might be wrong
    def __init__(self, original_circuit:cirq.Circuit,channel_strength, out_put=None):
        if out_put is None:
            out_put = []
        self.body = original_circuit.copy()
        self.number_of_flag = 0
        self.__zf_qubit = {}
        self.__xf_qubit = {}
        if out_put is None:
            self.out_put = self.body.all_qubits()
        self.map = Error_Map(self.body)
        self.map.create_map(channel_strength=channel_strength)
        self.error_locations = self.map.Error_Locations

    def get_x_flag_qubit(self, qubit):
        # Check if the qubit has an associated X flag qubit
        # Potential error: qubit isn't NamedQubits
        if qubit not in self.__xf_qubit:
            self.__xf_qubit[qubit] = cirq.NamedQubit(self.number_of_flag.__str__() + "_xf")
            self.number_of_flag += 1

        return self.__xf_qubit[qubit]

    def get_worst_location(self, number_of_locations):
        # Sort error_locations based on their objective_cost_1 in descending order
        sorted_locations = sorted(self.error_locations, key=lambda l: l.objective_cost_1(), reverse=True)
        # Return the top 'number_of_locations' from the sorted list
        return sorted_locations[:number_of_locations]

    def add_x_flag(self, locations, in_place=False):
        # modify the circuit: doable
        # todo: remove repetition
        for el in locations:
            el: ErrorLocation
            if in_place:
                start = self.body.moments.index(el.start_at())
                end = self.body.moments.index(el.end_at())
                flag_qubit = self.get_x_flag_qubit(el.get_qubit())
                self.body.batch_insert_into([(start, cirq.CNOT(el.get_qubit(), flag_qubit))
                                                ,(end, cirq.CNOT(el.get_qubit(), flag_qubit))
                                                ,(end+1, cirq.M(flag_qubit))
                                                ,(end+2,cirq.R(flag_qubit))])
                return self.body

            else:
                circuit = cirq.Circuit(self.body.moments)

                flag_qubit = self.get_x_flag_qubit(el.get_qubit())
                # a bug here???
                sub_circuit = cirq.Circuit()
                print(el.get_qubit())
                print(len(el.errors))
                for e in el.errors:
                    sub_circuit.append(e.m)
                print(sub_circuit)

                start = next(i for i, moment in enumerate(self.body.moments) if moment is el.start_at())
                end = next(i for i, moment in enumerate(self.body.moments) if moment is el.end_at())

                print(start,end)
                #don't use batch_insert
                circuit.batch_insert([(start, cirq.CNOT(el.get_qubit(), flag_qubit))
                                                , (end, cirq.M(flag_qubit))
                                                , (end, cirq.R(flag_qubit))
                                                , (end, cirq.CNOT(el.get_qubit(), flag_qubit))])
                return circuit



    def add_z_flag(self, locations: dict[(cirq.Qid,cirq.Moment)], in_place=False):
        pass


    def calculate_ler(self):
        # todo give the exact formular
        # should I regenerate the map
        pass






