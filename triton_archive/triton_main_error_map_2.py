from preparation.error_map import  Error_Map
from preparation.test_circuits import adder
import cirq


if __name__ == '__main__':

    circuit = adder(9)

    error_map = Error_Map(circuit)
    error_map.create_error_map(0.1)
    error_map.plot_error_map()

