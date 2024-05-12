
import cirq.circuits.circuit
import numpy as np
import cirq
import stim
import stimcirq
from preparation import error_circuit
from . import state_vector_comparison
import random
import matplotlib.pyplot as plt


def evaluate_flag_circuit(flag_circuit, icm_circuit, maximum_number_of_error, number_of_input_states):
    
    input_state_strings = generate_input_strings(icm_circuit, number_of_input_states)
    error_range=list(range(1, maximum_number_of_error + 1))

    flagged_propagation_rate = np.empty(len(input_state_strings))
    unflagged_propagation_rate = np.empty(len(input_state_strings))

    for s in range(len(input_state_strings)):

        state = input_state_strings[s]
        statename = state.replace("1", "+")

        total_case_flagless = 0
        total_case_flagged = 0
        number_fail_case = 0
        number_success_case = 0
        number_of_fail_alarm = 0
        number_of_time_error_propagate = 0

        # there could be an error in test kit
        test_kit_with_flags = state_vector_comparison.possible_state_vector_with_flags(flag_circuit, maximum_number_of_error, state)
        test_kit_without_flags = state_vector_comparison.possible_state_vector_without_flags(icm_circuit, maximum_number_of_error, state)

        for number_of_error in error_range:
            error_circuits_without_flags = error_circuit.generate_error_circuit_without_flags(icm_circuit, number_of_error)
            error_circuits_with_flags = error_circuit.generate_error_circuit_with_flags(flag_circuit, number_of_error)
            total_case_flagged += len(error_circuits_with_flags)
            total_case_flagless += len(error_circuits_without_flags)

            #run this in parallel

            # for unflagged circuits
            for cirq_circuit in error_circuits_without_flags:

                cirq_circuit = cirq_circuit[1]

                # prepare input state with H gates
                prepared_circuit = prepare_circuit_from_string(cirq_circuit, state)
                stim_circuit = stimcirq.cirq_circuit_to_stim_circuit(prepared_circuit)

                # run simulation
                simulator = stim.TableauSimulator()
                simulator.do_circuit(stim_circuit)
                flag_measurement = simulator.current_measurement_record()
                final_state = simulator.state_vector()

                # if errors have propagated to a higher weight
                if state_vector_comparison.have_error_propagated(final_state, test_kit_without_flags):
                    number_of_time_error_propagate += 1

            # for flagged circuits
            for cirq_circuit in error_circuits_with_flags:

                cirq_circuit = cirq_circuit[1]

                # prepare input state with H gates
                prepared_circuit = prepare_circuit_from_string(cirq_circuit, state)
                stim_circuit = stimcirq.cirq_circuit_to_stim_circuit(prepared_circuit)

                # run simulation
                simulator = stim.TableauSimulator()
                simulator.do_circuit(stim_circuit)
                flag_measurement = simulator.current_measurement_record()
                final_state = simulator.state_vector()

                # if errors have propagated to a higher weight
                if state_vector_comparison.have_error_propagated(final_state, test_kit_with_flags):
                    # flags successfull
                    if True in flag_measurement:
                        number_success_case += 1
                    # flags not succesful
                    else:
                        number_fail_case += 1
                
                # error propagated into same or smaller weight
                else:
                    # flags raise false alarm
                    if True in flag_measurement:
                        number_of_fail_alarm += 1

        print("state: ", statename)
        #print("total cases: " + str(total_case))
        #print("good flags: " + str(number_success_case))
        #print("failed flags: " + str(number_fail_case))
        #print("false flags: " + str(number_of_fail_alarm))
        #print("accepted cases: " + str(total_case - number_of_fail_alarm - number_success_case))

        flagged_propagation_rate[s] = number_fail_case / (total_case_flagged - number_of_fail_alarm - number_success_case)
        unflagged_propagation_rate[s] = number_of_time_error_propagate / total_case_flagless

    x = np.arange(len(input_state_strings)) #range(len(input_state_strings))
    #plt.figure(figsize=(10,10))
    plt.style.use('tableau-colorblind10')
    width = 0.3
    plt.bar(x-(width/2), flagged_propagation_rate, width=width, align='center', label="with flags")
    plt.bar(x+(width/2), unflagged_propagation_rate, width=width, align='center', label="without flags")
    plt.xlabel("state number")
    plt.ylabel("percentage of propagated errors")
    plt.legend()
    plt.title("Percentage of Propagated Errors From All Errors")
    plt.show()
    #plt.savefig('results.png')





def generate_input_strings(icm_circuit: cirq.circuits.circuit.Circuit, states: int):

    icm_qubits = len(icm_circuit.all_qubits())
    limit = np.min([states, 2**icm_qubits])

    # generate random unique input strings
    numbers = np.random.choice(2**icm_qubits, limit, replace=False)

    # output array
    strings = np.empty(limit,dtype=np.dtypes.StrDType)

    for i in range(limit):
        number = numbers[i]
        #form = "0:0" + str(icm_qubits) + "b"
        input_string = bin(number)[2:].zfill(icm_qubits) #format(number, form)
        strings[i] = input_string

    strings.sort()

    return strings


def prepare_tableau_from_string(simulator: stim.TableauSimulator, input_string):

    # {0, +} basis
    for i in range(0,len(input_string)):
        if input_string[i] == '1':
            simulator.reset_x(i) # prepare +
        else:
            simulator.reset_z(i) # prepare 0

    return simulator


def prepare_circuit_from_string(circuit: cirq.circuits.circuit.Circuit, input_string): 

    def sortqubits(q):
        return q.name
    
    prepared_circuit = cirq.Circuit()
    # get all qubits which are not flags
    qubits = list(filter(lambda q: 'f' not in q.name, circuit.all_qubits()))
    # ensure consistent order
    qubits.sort(key=sortqubits)

    # {0, +} basis
    for i in range(0,len(input_string)): # 0 / + basis
        if input_string[i] == '1':
            prepared_circuit.append(cirq.H(qubits[i]))
        else:
            prepared_circuit.append(cirq.identity_each(qubits[i]))
    
    prepared_circuit.append(circuit)

    return prepared_circuit

       

def benchmark_run(flag_circuit: cirq.circuits.circuit.Circuit, error_rate, initial_state):

    # use cirq to generate errors and prepare state
    circuit_with_errors = flag_circuit.with_noise(cirq.depolarize(p=error_rate))
    circuit_with_errors = prepare_circuit_from_string(circuit_with_errors, initial_state)
    stim_circuit_errors = stimcirq.cirq_circuit_to_stim_circuit(circuit_with_errors)
    circuit_expected = prepare_circuit_from_string(flag_circuit, initial_state)
    stim_circuit_expected = stimcirq.cirq_circuit_to_stim_circuit(circuit_expected)
    
    simulator = stim.TableauSimulator()
    #simulator_expected = prepare_tableau_from_string(simulator, initial_state)
    simulator_expected = simulator.copy()
    simulator_error = simulator_expected.copy()

    # use stim to run simulation on expected circuit
    simulator_expected.do_circuit(stim_circuit_expected)
    flag_measurement_expected = simulator_expected.current_measurement_record()
    final_state_expected = simulator_expected.state_vector()


    # similarly for the error state
    simulator_error.do_circuit(stim_circuit_errors)
    flag_measurement_errors = simulator_error.current_measurement_record()
    final_state_errors = simulator_error.state_vector()

    # return values
    error_occured = 0
    correct_flag = 0
    missed_flag = 0
    correct_no_flag = 0
    false_flag = 0

    # if there was an error
    if not np.array_equal(final_state_errors, final_state_expected):
        error_occured = 1
        result_string = ""
        if True in flag_measurement_errors:
            correct_flag = 1
            result_string = "Flags succeeded"
        else:
            missed_flag = 1
            result_string = "Flags failed"
    #    print("Error(s) occured, " + result_string)
    # if there were no errors OR the errors cancelled each other out
    else:
        result_string = ""
        if True in flag_measurement_errors:
            false_flag = 1
            result_string = "Flags failed"
        else:
            correct_no_flag = 1
            result_string = "Flags succeeded"
    #    print("No errors/Errors cancelled out, " + result_string)
    
    return error_occured, correct_flag, missed_flag, correct_no_flag, false_flag

def benchmark(flag_circuit: cirq.circuits.circuit.Circuit, error_rate, number_of_runs: int, states):

    number_of_qubits = len(flag_circuit.all_qubits())

    # each row represents the results for one binary input string 
    # the columns are: error rate is ciruit is flagged, error rate is circuit is unflagged
    results = np.zeros((len(states), 2))

    for k in range(len(states)):

        intial_state = states[k]
        total_cases = number_of_runs
        cases_with_error = 0
        correct_flagged_cases = 0
        missed_cases = 0
        false_cases = 0
        correct_noflag_cases = 0

        for n in range(0,number_of_runs):
            #print("run: ", n)
            res = benchmark_run(flag_circuit, error_rate, intial_state)
            error_occured, correct_flag, missed_flag, correct_no_flag, false_flag = res
            cases_with_error += error_occured
            correct_flagged_cases += correct_flag
            missed_cases += missed_flag
            false_cases += false_flag
            correct_noflag_cases += correct_no_flag

        # to ignore exceptions check: b and a / b or 0
        logical_error_rate_flag = (missed_cases + correct_noflag_cases) and missed_cases / (missed_cases + correct_noflag_cases) or None
        logical_error_rate_flagless = cases_with_error / total_cases

        """
        print("total number of cases: " + str(total_cases))
        print("number of cases with errors: " + str(cases_with_error))
        print("number of correct flags: " + str(correct_flagged_cases))
        print("number of missed flags: " + str(missed_cases))
        print("number of false flags: " + str(false_cases))
        print("number of correct unflagged cases: " + str(correct_noflag_cases))
        print("success rate: " +  str(success_rate))
        """

        results[k,:] = [logical_error_rate_flag, logical_error_rate_flagless]

    return results #logical_error_rate_flag, logical_error_rate_flagless

def random_noise_benchmark(flag_circuit, icm_circuit):

    number_of_states = 100
    number_of_runs = 100
    error_rates = np.linspace(0.001, 0.01, 10) #0.001, 0.05, 20)
    results = np.zeros((len(error_rates),1))
    flagless_results = np.copy(results)
    limit = np.min([2**(len(icm_circuit.all_qubits())), number_of_states])
    state_results = np.zeros((limit,len(error_rates)))
    state_flagless_results = np.copy(state_results)
    # flag_circuit = f_cir_random

    # this assumes that ancillas are always added "before" the main qubits of the circuit
    # thus we also assume that flag qubits always start out in state 0
    icm_states = generate_input_strings(icm_circuit, number_of_states)

    for e in range(0,len(error_rates)):
        print("error: " + str(error_rates[e]))
        error_rate = error_rates[e]

        # run sim with flagged-circuit
        results_array = benchmark(flag_circuit, error_rate, number_of_runs, icm_states)
        logical_error_rates = results_array[:,0]

        state_results[:,e] = logical_error_rates
        logical_error_rates = logical_error_rates[np.logical_not(np.isnan(logical_error_rates))]
        results[e,0] = np.average(logical_error_rates)

        # run sim with flagless-circuit
        results_array = benchmark(icm_circuit, error_rate, number_of_runs, icm_states)

        flagless_error_rates = results_array[:,1]
        state_flagless_results[:,e] = flagless_error_rates
        flagless_results[e,0] = np.average(flagless_error_rates)

        

    # plotting for each state
    #plt.figure(figsize=(15,20))
    #for k in range(limit):
    #    plt.subplot(limit//2, 2, k+1)
    #    plt.scatter(error_rates, state_results[k,:])
    #    plt.scatter(error_rates, state_flagless_results[k,:])
    #    statename = icm_states[k].replace("1", "+")
    #    plt.title("state: " + statename, fontsize = 10)
        #plt.xlabel('noise channel strength')
        #plt.ylabel('logical error rate')
        #plt.legend()
    #plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=3.5)
    #plt.show()
    
    # the simulation must be ran on the flagless circuit separately,
    # as otherwise we cannot distinguish when the error occurs on a flag:
    # when trying to determine the "flagless" error rate, 
    # those runs with errors only on the flags count as error-free cases

    # plotting
    plt.scatter(error_rates, results[:,0], label="flag circuit")
    plt.scatter(error_rates, flagless_results[:,0], label="flagless circuit")
    plt.xlabel('noise channel strength')
    plt.ylabel('logical error rate')
    plt.legend()
    plt.show()
    #plt.savefig('results.png')