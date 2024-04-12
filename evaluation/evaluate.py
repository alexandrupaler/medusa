
import numpy as np
import cirq
import stim
import stimcirq
import itertools
from functools import reduce
from preparation import compiler, error_circuit
from . import state_vector_comparison

def evaluate_flag_circuit(flag_circuit, maximum_number_of_error):
    total_case = 0
    number_fail_case = 0
    number_success_case = 0
    number_of_fail_alarm = 0
    number_of_time_error_propagate = 0
    correct_state = state_vector_comparison.expected_state_vector(flag_circuit)
    #there could be an error in test kit
    test_kit = state_vector_comparison.possible_state_vector(flag_circuit, maximum_number_of_error)
    error_range=list(range(maximum_number_of_error+1))
    del error_range[0]
    print(error_range)
    for number_of_error in error_range:
        #error_circuits = error_circuit.generate_input_error(flag_circuit, number_of_error)
        error_circuits = error_circuit.generate_error_circuit(flag_circuit, number_of_error)
        total_case = total_case + len(error_circuits)
        #run this in parallel
        for cirq_circuit in error_circuits:
            print("\n")
            #print(cirq_circuit[0])
            #for some reason it alwasy return trivival measuament
            simulator = stim.TableauSimulator()
            stim_circuit = stimcirq.cirq_circuit_to_stim_circuit(cirq_circuit[1])
            simulator.do_circuit(stim_circuit)
            flag_measurement = simulator.current_measurement_record()
            final_state = simulator.state_vector()
            print(flag_measurement)

            if state_vector_comparison.have_error_propagated(final_state, test_kit):
                number_of_time_error_propagate += 1
                if True in flag_measurement:
                    number_success_case += 1
                    print("flags successfully catch error")
                else:
                    number_fail_case += 1
                    print("error propagated into higher weigh errors, but the flags fail to catch error")
            else:
                if True in flag_measurement:
                    number_of_fail_alarm += 1
                    print("Error propagated into same or smaller weight error , but the flag raise a fail alarm")
                else:
                    print("Error propagated into same or smaller weight error ")

    print("number of errors:" + str(number_of_error))
    print("total case:" + str(total_case))
    print("number of time error propagate into higher weigh error:"+str(number_of_time_error_propagate))
    print("number of time flag fail :(flags return trivial measurement, but error propagated into higher weight error)"+str(number_fail_case))
    print("number of time flag success:"+str(number_success_case))
    print("number of fail alarm (error propagated into error with lower or the same weight) :"+str(number_of_fail_alarm))



