import cirq
from flag_qubits import  ZFlagQubit,XFlagQubit

class FlagCircuit(cirq.Circuit):
    def __is_icm_circuit__(self):
        return True
    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls)
        self.number_of_flag = 0
        self.zf_qubit = []
        self.xf_qubit = []
        self.bad_cnot = self.find_bad_cnot()
        pass

    def add_x_flag(self, locations: dict[(cirq.Qid,cirq.Moment)], in_place=False) -> cirq.Circuit:
        pass

    def add_z_flag(self, locations: dict[(cirq.Qid,cirq.Moment)], in_place=False) -> cirq.Circuit:
        pass

    def find_bad_cnot(self):
        pass




