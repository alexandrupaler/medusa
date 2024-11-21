import cirq
from preparation.error_map import Error_Map
from preparation.flag_circuit import FlagCircuit

class Flag:
    number_of_flag = 0

    def __init__(self):
        self.flag_qubitx = cirq.NamedQubit(str(self.number_of_flag) + "xf")
        self.flag_qubitz = cirq.NamedQubit(str(self.number_of_flag) + "zf")
        Flag.number_of_flag += 1

    def create_x_flag(self, control):
        x_flag = [[cirq.CNOT(control, self.flag_qubitx)],
                  [cirq.CNOT(control, self.flag_qubitx), cirq.measure(self.flag_qubitx),
                   cirq.ResetChannel().on(self.flag_qubitx)]
                  ]
        return x_flag


    def create_z_flag(self, target):
        z_flag = [[cirq.H(self.flag_qubitz), cirq.CNOT(self.flag_qubitz, target)],
                  [cirq.CNOT(self.flag_qubitz, target), cirq.H(self.flag_qubitz), cirq.measure(self.flag_qubitz),
                   cirq.ResetChannel().on(self.flag_qubitz)]]
        return z_flag



class FlagCompiler:
    def keep_clifford_plus_T(self, op) -> bool:
        if isinstance(op.gate, (cirq.XPowGate,
                                cirq.YPowGate,
                                cirq.ZPowGate,
                                cirq.HPowGate,
                                cirq.CNotPowGate,
                                cirq.SwapPowGate
                                )):
            return True

    #TODO: this don't work on my machine
    def decompose_to_ICM(self, circuit, i=0, j=0):
        json_string = cirq.to_json(cirq.Circuit(cirq.decompose(circuit, keep=self.keep_clifford_plus_T)))
        with open("input_cirq_circuit" + str(i) + str(j) + ".json", "w") as outfile:
            outfile.write(json_string)

        # here is a hacky way to convert using jabalizer
        import os
        os.system("julia icm_converter.jl " + str(i) + " " + str(j))

        cirq_circuit = cirq.read_json("output_cirq_icm_circuit" + str(i) + str(j) + ".json")
        return cirq_circuit

    @staticmethod
    def __is_moment_with_cnot__(moment: cirq.Moment):
        for op in moment.operations:
            if len(op.qubits) == 2:
                return True
        return False





    def add_flag(self, circuit: cirq.Circuit, number_of_x_flag=0, number_of_z_flag=0,
                 strategy="random") -> cirq.Circuit:
        # setup
        flag_circuit = cirq.Circuit()
        number_of_momnet = len(circuit.moments)
        moments_with_index = list(zip(list(circuit.moments), range(number_of_momnet)))
        moments_with_cnot_and_index = list(filter(lambda a: self.__is_moment_with_cnot__(a[0]), moments_with_index))
        control_qbits = []
        target_qbits = []
        x_start_moments = []
        z_start_moments = []
        x_end_moments = []
        z_end_moments = []

        if strategy == "random":
            import random
            def random_moments_with_cnot_and_index(number_of_flag):
                return list(
                    random.choices(list(filter(lambda a: self.__is_moment_with_cnot__(a[0]), moments_with_index)),
                                   k=number_of_flag))

            x_random_moments_with_cnot = random_moments_with_cnot_and_index(number_of_x_flag)
            z_random_moments_with_cnot = random_moments_with_cnot_and_index(number_of_z_flag)

            x_start_moments = list(map(lambda a: a[1], x_random_moments_with_cnot))
            z_start_moments = list(map(lambda a: a[1], z_random_moments_with_cnot))
            z_random_moments_with_cnot = list(map(lambda a: a[0], z_random_moments_with_cnot))
            x_random_moments_with_cnot = list(map(lambda a: a[0], x_random_moments_with_cnot))

            for x, mx in zip(x_start_moments, x_random_moments_with_cnot):
                m: cirq.Moment
                if x == number_of_momnet - 1:
                    x_end_moments.append(x)
                else:
                    x_end_moments.append(random.choice(range(x, number_of_momnet, 1)))

                for op in mx.operations:
                    if len(list(op.qubits)) == 2:
                        control_qbits.append(op.qubits[0])

            for z, mz in zip(z_start_moments, z_random_moments_with_cnot):
                m: cirq.Moment
                if z == number_of_momnet - 1:
                    z_end_moments.append(z)
                else:
                    z_end_moments.append(random.choice(range(z, number_of_momnet, 1)))
                for op in mz.operations:
                    if len(list(op.qubits)) == 2:
                        target_qbits.append(op.qubits[1])

        elif strategy == "heuristic":
            # Brute force:D
            for qubits in circuit.all_qubits():
                x_gatherer = []
                z_gatherer = []
                for moment, index in moments_with_cnot_and_index:
                    moment: cirq.Moment
                    if moment.operations[0].qubits[0] == qubits:
                        x_gatherer.append(index)
                        if len(z_gatherer) >= 2:
                            z_start_moments.append(z_gatherer[0])
                            z_end_moments.append(z_gatherer[-1])
                            target_qbits.append(qubits)
                        z_gatherer = []
                    elif moment.operations[0].qubits[1] == qubits:
                        z_gatherer.append(index)
                        if len(x_gatherer) >= 2:
                            x_start_moments.append(x_gatherer[0])
                            x_end_moments.append(x_gatherer[-1])
                            control_qbits.append(qubits)
                        x_gatherer = []
                if len(x_gatherer) >= 2:
                    x_start_moments.append(x_gatherer[0])
                    x_end_moments.append(x_gatherer[-1])
                    control_qbits.append(qubits)
                if len(z_gatherer) >= 2:
                    z_start_moments.append(z_gatherer[0])
                    z_end_moments.append(z_gatherer[-1])
                    target_qbits.append(qubits)

        elif strategy == "today_meeting":
            result = FlagCircuit(circuit,channel_strength=0.1)
            for l in  result.get_worst_location(number_of_locations=4):
                print("cost :", l.objective_cost_1())
                print(result.add_x_flag([l],in_place=False))

            return result.body

        return flag_circuit
