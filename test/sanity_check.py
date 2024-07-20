import cirq
from preparation.error_location import Single_Error, ErrorLocation
from preparation.error_map import Error_Map
from preparation.compiler import  FlagCompiler

if __name__ == '__main__':
    circuit:cirq.Circuit
    circuit = cirq.read_json("test/test_circuit/output_cirq_icm_circuit03.json")
    print(circuit)
    print(len(list(circuit.all_operations())))
    map =Error_Map(circuit)
    map.create_map(channel_strength=0.1)
    """
        for q in circuit.all_qubits():
        for m in circuit.moments:
            if map.X_propagation_map[q][m].objective_cost_1() > 0:
                print( map.X_propagation_map[q][m].objective_cost_1())
    """


    for l in map.Error_Locations:
        print(l.objective_cost_1())

    FlagCompiler().add_flag(circuit, number_of_x_flag=2, strategy="today_meeting")



