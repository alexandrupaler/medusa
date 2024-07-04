import cirq
from dataclasses import dataclass

#TODO

class FlagQubit(cirq.NamedQubit):
    pass

@dataclass
class ZFlagQubit(FlagQubit):
    def __new__(cls,protected_qubit:cirq.NamedQubit):
        self = super().__new__(cls, protected_qubit.name + "zf")
        self.protected_qubit = protected_qubit


class XFlagQubit(FlagQubit):
    def __new__(cls,protected_qubit:cirq.NamedQubit):
        self = super().__new__(cls, protected_qubit.name + "xf")
        self.protected_qubit = protected_qubit
