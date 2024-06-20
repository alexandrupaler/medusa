
import cirq.circuits.circuit
import warnings
import cirq
import stim
import stimcirq
import random
import matplotlib.pyplot as plt
import numpy as np
from preparation import error_circuit
from . import state_vector_comparison

# how do the error weights change & propagate
def evaluate_flag_circuit(flag_circuit, icm_circuit, maximum_number_of_error, number_of_input_states, plotting, output_file="results.png"):
    
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

        #print("state: ", statename)
        #print("total cases: " + str(total_case))
        #print("good flags: " + str(number_success_case))
        #print("failed flags: " + str(number_fail_case))
        #print("false flags: " + str(number_of_fail_alarm))
        #print("accepted cases: " + str(total_case - number_of_fail_alarm - number_success_case))

        flagged_propagation_rate[s] = number_fail_case / (total_case_flagged - number_of_fail_alarm - number_success_case)
        unflagged_propagation_rate[s] = number_of_time_error_propagate / total_case_flagless


    if plotting:
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
        #plt.show()
        plt.savefig(output_file)

    return flagged_propagation_rate, unflagged_propagation_rate




# helper used to prepare different states
def generate_input_strings(icm_circuit: cirq.circuits.circuit.Circuit, states: int):

    icm_qubits = len(icm_circuit.all_qubits())
    limit = np.min([states, 2**icm_qubits])
    largest_state = (1 << (icm_qubits)) - 1

    def random_number():
        # generate random input strings
        number = random.randint(0,largest_state)
        return number

    # output array
    strings = np.empty(limit,dtype=np.dtypes.StrDType)

    for i in range(limit):
        while True:
            number = random_number()
            #input_string = bin(number)[2:].zfill(icm_qubits)
            form = "0" + str(icm_qubits) + "b"
            input_string = format(number, form)
            if input_string in strings:
                continue
            else:
                strings[i] = input_string
                break

    strings.sort()

    return strings

# another helper that could be used to prepare different states
def prepare_tableau_from_string(simulator: stim.TableauSimulator, input_string):

    # {0, +} basis
    for i in range(0,len(input_string)):
        if input_string[i] == '1':
            simulator.reset_x(i) # prepare +
        else:
            simulator.reset_z(i) # prepare 0

    return simulator

# another helper used to prepare different states
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

       
def random_noise_benchmark(flag_circuit, icm_circuit, number_of_runs, error_rates, plotting, output_file="results.png",perfect_flags=False):

    # helper
    def benchmark_run(flag_circuit: cirq.circuits.circuit.Circuit, error_rate, initial_state):

        # use cirq to generate errors and prepare state
        circuit_with_errors = add_random_noise(flag_circuit, error_rate, perfect_flags) #flag_circuit.with_noise(cirq.depolarize(p=error_rate))
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

    # another helper
    def benchmark(flag_circuit: cirq.circuits.circuit.Circuit, error_rate, number_of_runs: int, states):

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


    number_of_states = 100
    results = np.zeros((len(error_rates),1))
    flagless_results = np.copy(results)
    limit = np.min([2**(len(icm_circuit.all_qubits())), number_of_states])
    state_results = np.zeros((limit,len(error_rates)))
    state_flagless_results = np.copy(state_results)

    # generate input states as bitstrings
    icm_states = generate_input_strings(icm_circuit, number_of_states)

    for e in range(0,len(error_rates)):
        
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

    if plotting:
        # plotting
        plt.scatter(error_rates, results[:,0], label="flag circuit")
        plt.scatter(error_rates, flagless_results[:,0], label="flagless circuit")
        plt.xlabel('noise channel strength')
        plt.ylabel('logical error rate')
        plt.legend()
        #plt.show()
        plt.savefig(output_file)

    return results, flagless_results

def random_noise_on_error_circuit(flag_circuit, icm_circuit, number_of_runs, error_rates, plotting, output_file="results.png",perfect_flags=False):

    # generate input states as bitstrings
    number_of_states = 100
    icm_states = generate_input_strings(icm_circuit, number_of_states)

    # circuits with individual errors + error-free circuit
    error_circuits = error_circuit.generate_handlable_error_circuits(flag_circuit)
    error_circuits.append(flag_circuit)

    results = np.zeros((len(error_rates), len(icm_states)))
    flagless_results = np.zeros((len(error_rates),))


    for s in range(len(icm_states)):
        initial_state = icm_states[s]

        # prep icm circuit for comparison with flagless circuit
        flagless_expected_circuit = prepare_circuit_from_string(icm_circuit, initial_state)
        stim_circuit_flagless_expected = stimcirq.cirq_circuit_to_stim_circuit(flagless_expected_circuit)

        # flagless stabilizers
        simulator = stim.TableauSimulator()
        simulator.do_circuit(stim_circuit_flagless_expected)
        flagless_stabilizers = simulator.canonical_stabilizers()

        # stabilizers
        flag_expected_circuit = prepare_circuit_from_string(icm_circuit, initial_state)
        stim_circuit_flag_expected = stimcirq.cirq_circuit_to_stim_circuit(flag_expected_circuit)

        # flagless stabilizers
        simulator = stim.TableauSimulator()
        simulator.do_circuit(stim_circuit_flag_expected)
        stabilizers = simulator.canonical_stabilizers()

        # all possible final states
        possible_states = state_vector_comparison.possible_error_states(error_circuits, initial_state, stabilizers)

        for e in range(len(error_rates)):
            error_rate = error_rates[e]

            # flagless circuit
            flagless_circuit = add_random_noise(icm_circuit, error_rate, perfect_flags) #icm_circuit.with_noise(cirq.depolarize(p=error_rate))
            flagless_circuit = prepare_circuit_from_string(flagless_circuit, initial_state)
            flagless_stim_circuit = stimcirq.cirq_circuit_to_stim_circuit(flagless_circuit)

            # use cirq to generate errors and prepare state
            circuit_with_errors = add_random_noise(flag_circuit, error_rate, perfect_flags) #flag_circuit.with_noise(cirq.depolarize(p=error_rate))
            circuit_with_errors = prepare_circuit_from_string(circuit_with_errors, initial_state)
            stim_circuit_errors = stimcirq.cirq_circuit_to_stim_circuit(circuit_with_errors)

            total_cases = number_of_runs
            total_cases_flagless = number_of_runs
            error_occured = 0
            correct_flag = 0
            missed_flag = 0
            false_flag = 0
            correct_no_flag = 0

            for n in range(number_of_runs):

                # use stim to run simulation
                simulator = stim.TableauSimulator()
                simulator.do_circuit(stim_circuit_errors)

                # it is important that the following are done in this specific order!
                flag_measurement = simulator.current_measurement_record()
                final_state =  measure_stabilizers(simulator, stabilizers) #simulator.state_vector()

                if not state_vector_comparison.equal_stabilizer_measurements(final_state, possible_states):
                    if True in flag_measurement:
                        correct_flag += 1
                    else:
                        missed_flag += 1
                else:
                    if True in flag_measurement:
                        false_flag += 1
                    else:
                        correct_no_flag += 1    

                # same for the flagless circuit
                simulator = stim.TableauSimulator()
                simulator_expected = simulator.copy()

                simulator.do_circuit(flagless_stim_circuit)
                final_state = measure_stabilizers(simulator, flagless_stabilizers) #simulator.state_vector()
                
                simulator_expected.do_circuit(stim_circuit_flagless_expected)
                final_state_expected =  measure_stabilizers(simulator_expected, flagless_stabilizers) #simulator_expected.state_vector()

                if not state_vector_comparison.equal_stabilizer_measurements(final_state, [final_state_expected]):
                    error_occured += 1
                    
            log_error = (correct_no_flag + missed_flag) and missed_flag / (correct_no_flag + missed_flag) or None
            results[e,s] = log_error
            flagless_log_error = error_occured / total_cases_flagless 
            flagless_results[e] += flagless_log_error

    # normalize
    results = np.nanmean(results, axis=(1)) 
    flagless_results = flagless_results / len(icm_states)

    if plotting:
        # plotting
        plt.scatter(error_rates, results, label="flag circuit")
        plt.scatter(error_rates, flagless_results, label="flagless circuit")
        plt.xlabel('noise channel strength')
        plt.ylabel('logical error rate')
        plt.legend()
        #plt.show()
        plt.savefig(output_file)

    return results, flagless_results

# helper used to measure all the stabilizers of a circuit
def measure_stabilizers(simulator: stim.TableauSimulator, stabilizers: list[stim.PauliString]):
    res = np.full((len(stabilizers),),True)

    for i in range(len(stabilizers)):
        simulator_copy = simulator.copy()
        pstring = stabilizers[i]
        res[i] = simulator_copy.measure_observable(pstring)

    return res

# simulation which uses stabilizer measurements, calculates both robustness and logical error
def stabilizers_robustness_and_logical_error(flag_circuit: cirq.Circuit, icm_circuit: cirq.Circuit, number_of_runs, error_rates, plotting, plot_title, perfect_flags=False):
    results = np.zeros((len(error_rates),))
    results_icm = np.zeros((len(error_rates),))
    results_rob = np.zeros((len(error_rates),))
    results_rob_icm = np.zeros((len(error_rates),))
    acceptance = np.zeros((len(error_rates),))

    number_of_input_states = 100
    input_states = generate_input_strings(icm_circuit, number_of_input_states)

    for e in range(len(error_rates)):

        warnings.warn("error rate number: " + str(e))

        error_rate = error_rates[e]

        error_occured = 0
        correct_flags = 0
        missed_flags = 0
        false_flags = 0
        no_flag = 0

        faulty_stabilizers = 0
        faulty_stabilizers_icm = 0

        for s in range(len(input_states)):

            state = input_states[s]

            # the expected results 
            # for flag circuit
            prepared_circuit = prepare_circuit_from_string(flag_circuit, state)
            expected_stim = stimcirq.cirq_circuit_to_stim_circuit(prepared_circuit)
            simulator_expected = stim.TableauSimulator()
            simulator_expected.do_circuit(expected_stim)
            stabilizers = simulator_expected.canonical_stabilizers()
            # for icm circuit
            prepared_circuit_icm = prepare_circuit_from_string(icm_circuit, state)
            expected_stim_icm = stimcirq.cirq_circuit_to_stim_circuit(prepared_circuit_icm)
            simulator_expected_icm = stim.TableauSimulator()
            simulator_expected_icm.do_circuit(expected_stim_icm)
            stabilizers_icm = simulator_expected_icm.canonical_stabilizers()


            for n in range(number_of_runs):

                # add noise to circuits
                # for flag circuit
                noisy_circuit = add_random_noise(flag_circuit, error_rate, perfect_flags) #flag_circuit.with_noise(cirq.depolarize(p=error_rate))
                # for icm circuit
                noisy_circuit_icm = add_random_noise(icm_circuit, error_rate, perfect_flags) #icm_circuit.with_noise(cirq.depolarize(p=error_rate))

                # run simulations
                # for flag circuit
                prepared_circuit = prepare_circuit_from_string(noisy_circuit, state)
                noisy_stim = stimcirq.cirq_circuit_to_stim_circuit(prepared_circuit)
                simulator = stim.TableauSimulator()
                simulator.do_circuit(noisy_stim)
                flag_measurements = simulator.current_measurement_record()
                stabilizer_measurements = measure_stabilizers(simulator, stabilizers)

                if not np.any(stabilizer_measurements):
                    # if no error but flag went off
                    if True in flag_measurements:
                        false_flags += 1
                    else:
                        no_flag += 1
                else:
                    # if flags caught error
                    if True in flag_measurements:
                        correct_flags += 1
                    # if flags missed error
                    else:
                        faulty_stabilizers += stabilizer_measurements.sum()
                        missed_flags += 1

                # for icm circuit
                prepared_circuit_icm = prepare_circuit_from_string(noisy_circuit_icm, state)
                noisy_stim_icm = stimcirq.cirq_circuit_to_stim_circuit(prepared_circuit_icm)
                simulator_icm = stim.TableauSimulator()
                simulator_icm.do_circuit(noisy_stim_icm)
                stabilizer_measurements_icm = measure_stabilizers(simulator_icm, stabilizers_icm)
            
                if np.any(stabilizer_measurements_icm):
                    error_occured += 1
                    faulty_stabilizers_icm += stabilizer_measurements.sum()


        # update results
        results[e] = missed_flags / ((no_flag + missed_flags) * len(input_states))
        results_icm[e] = error_occured / (number_of_runs * len(input_states))
        results_rob[e] = faulty_stabilizers / (len(stabilizers) * (no_flag + missed_flags) * len(input_states))
        results_rob_icm[e] = faulty_stabilizers_icm / (len(stabilizers_icm) * (number_of_runs) * len(input_states))
        acceptance[e] = (no_flag + missed_flags) / (number_of_runs * len(input_states))


    if plotting:
        # plotting
        plt.title(plot_title)
        plt.loglog(error_rates, results, '.', label="flag circuit")
        plt.loglog(error_rates, results_icm, '.', label="flagless circuit")
        plt.xlabel('noise channel strength')
        plt.ylabel('logical error rate')
        plt.legend()
        #plt.show()
        filename = "res_logical_error_" + plot_title.replace(" ", "") + ".png"
        plt.savefig(filename)
        plt.close()

        plt.title(plot_title)
        plt.loglog(error_rates, results_rob, '.', label="flag circuit")
        plt.loglog(error_rates, results_rob_icm, '.', label="flagless circuit")
        plt.xlabel('noise channel strength')
        plt.ylabel('stabilizers with errors, %')
        plt.legend()
        #plt.show()
        filename = "res_results_robustness_" + plot_title.replace(" ", "") + ".png"
        plt.savefig(filename)
        plt.close()
    return results, results_icm, results_rob, results_rob_icm, acceptance

# calculated error at different moments using stabilizer measurements
def stabilizers_benchmark_with_timesteps(flag_circuit: cirq.Circuit, icm_circuit: cirq.Circuit, number_of_runs, error_rate, plotting, output_file="results.png",perfect_flags=False):
    number_of_input_states = 100
    input_states = generate_input_strings(icm_circuit, number_of_input_states)

    def run_time_steps_flag(circuit: cirq.Circuit, number_of_runs, error_rate, input_states):
        moments = list(circuit.moments)
        max_times_steps = 10
        time_steps = np.min([len(moments), max_times_steps])
        step_size = len(moments) // time_steps
        results = np.zeros((time_steps,))

        for m in range(time_steps):

            step = m * step_size

            error_occured = 0
            correct_flags = 0
            missed_flags = 0
            false_flags = 0
            no_flag = 0

            for s in range(len(input_states)):
                state = input_states[s]
                prepared_circuit = prepare_circuit_from_string(circuit, state)
                split_circuit = cirq.Circuit(list(prepared_circuit.moments)[:step])
                expected_stim = stimcirq.cirq_circuit_to_stim_circuit(split_circuit)
                simulator_expected = stim.TableauSimulator()
                simulator_expected.do_circuit(expected_stim)
                stabilizers = simulator_expected.canonical_stabilizers()

                for n in range(number_of_runs):

                    noisy_circuit = add_random_noise(split_circuit, error_rate, perfect_flags) #split_circuit.with_noise(cirq.depolarize(p=error_rate))
                    noisy_stim = stimcirq.cirq_circuit_to_stim_circuit(noisy_circuit)
                    simulator = stim.TableauSimulator()
                    simulator.do_circuit(noisy_stim)
                    flag_measurements = simulator.current_measurement_record()
                    stabilizer_measurements = measure_stabilizers(simulator, stabilizers)

                    if not np.any(stabilizer_measurements): 
                        # if no error but flag went off
                        if True in flag_measurements:
                            false_flags += 1
                        else:
                            no_flag += 1
                    else:
                        error_occured += 1
                        # if flags caught error
                        if True in flag_measurements:
                            correct_flags += 1
                        # if flags missed error
                        else:            
                            missed_flags += 1
                
            results[m] = missed_flags / ((no_flag + missed_flags) * len(input_states))
        if plotting:
            scaled_time_steps = range(time_steps) * step_size
            plt.loglog(scaled_time_steps, results, label="flag circuit")
            plt.xlabel('moment')
            plt.ylabel('logical error rate')
            plt.legend()
        return results
    
    def run_time_steps_icm(circuit: cirq.Circuit, number_of_runs, error_rate, input_states):
        moments = list(circuit.moments)
        max_times_steps = 10
        time_steps = np.min([len(moments), max_times_steps])
        step_size = len(moments) // time_steps
        results = np.zeros((time_steps,))

        for m in range(time_steps):

            step = m * step_size
            error_occured = 0

            for s in range(len(input_states)):
                state = input_states[s]
                prepared_circuit = prepare_circuit_from_string(circuit, state)
                split_circuit = cirq.Circuit(list(prepared_circuit.moments)[:step])
                expected_stim = stimcirq.cirq_circuit_to_stim_circuit(split_circuit)
                simulator_expected = stim.TableauSimulator()
                simulator_expected.do_circuit(expected_stim)
                stabilizers = simulator_expected.canonical_stabilizers()

                for n in range(number_of_runs):

                    noisy_circuit = add_random_noise(split_circuit, error_rate, perfect_flags) #split_circuit.with_noise(cirq.depolarize(p=error_rate))
                    noisy_stim = stimcirq.cirq_circuit_to_stim_circuit(noisy_circuit)
                    simulator = stim.TableauSimulator()
                    simulator.do_circuit(noisy_stim)
                    flag_measurements = simulator.current_measurement_record()
                    stabilizer_measurements = measure_stabilizers(simulator, stabilizers)

                    if np.any(stabilizer_measurements): 
                        # if error occured
                        error_occured += 1
                
            results[m] = error_occured / (len(input_states) * number_of_runs)
        
        if plotting:
            scaled_time_steps = range(time_steps) * step_size
            plt.loglog(scaled_time_steps, results, label="icm circuit")
            plt.xlabel('moment')
            plt.ylabel('logical error rate')
            plt.legend()
            #plt.show()
            plt.savefig(output_file)   
        return results
    
    results = run_time_steps_flag(flag_circuit, number_of_runs, error_rate, input_states)
    results_icm = run_time_steps_icm(icm_circuit, number_of_runs, error_rate, input_states)
    return results, results_icm

# helper used to add noise to circuits
def add_random_noise(circuit: cirq.Circuit, error_rate, perfect_flags=False):

    # custom noise model excluding flags:
    class PerfectFlagsDepolarizingNoise(cirq.NoiseModel):
        def noisy_operation(self, op: cirq.Operation):
            if 'f' not in str(op.qubits):
                for q in op.qubits:
                    return [op, cirq.depolarize(p=error_rate).on(q)]
            return op
    
    noisy_circuit = circuit
    if not perfect_flags:
        noisy_circuit = circuit.with_noise(cirq.depolarize(p=error_rate))
    else:
        noisy_circuit = circuit.with_noise(noise=PerfectFlagsDepolarizingNoise())

    return noisy_circuit
