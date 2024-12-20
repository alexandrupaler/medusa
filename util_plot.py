import os
import sys
import matplotlib.pyplot as plt

import json

# Some notes:
#
# 1. `/circuits` adders and 10 samples of b1, b2 and b3. All with heuristic strategy (icm, icm small, fc)
# 2. `/bigbudget` has benchmark circuit type results from 1. Only i=5 was obtained?
# 3. `/adder2` has adder circuit type results from 1. All sizes were obtained.
#
# 4. `/circuits2` adders and 1 sample of b1, b2 and b3. All with "important" heuristic strategy (icm, icm small, fc)
# 5. `/importancebudget` has the adder results from 4. Only i>8 was obtained.

if __name__ == '__main__':

    if len(sys.argv) < 3:
        CRED = '\033[91m'
        CEND = '\033[0m'
        print(CRED + "Will run only if provided two parameters:\n\t this_script [path_of_jsons] [plot_file_name]" + CEND)
        exit(1)

    elif len(sys.argv) == 3:
        path = sys.argv[1]
        plot_fname = sys.argv[2]

    # path = "importancebudget/"
    error_rate = 0.001

    files = list(filter(lambda f: f.startswith("fc_"), os.listdir(path)))
    files.sort(key=lambda w: int(w.split("_")[2]))

    for filename in files:

        parts = filename.split("_")
        circuit_type = parts[1]
        circuit_size = parts[2]

        # Check the circuit type
        # if 'b' in str(circuit_type):
        if 'a' in str(circuit_type):
            # If you know the circuit type, size and error_rate
            # then you can load the json and read the values from the dictionary
            last_values = {}
            with open(f"{path}/report_{circuit_type}_{circuit_size}_{error_rate}.json", "r") as report:
                last_values = json.load(report)

            """
            The format of the JSON is the following:
            
                last_values["large_fc_failure_rate"][sample_i]
                last_values["large_icm_failure_rate"][sample_i]
                last_values["small_icm_failure_rate"][sample_i]
                last_values["error_mod"][sample_i]
    
                # Compute averages
                last_values["averages"]["large_fc_failure_rate"]
                last_values["averages"]["large_icm_failure_rate"]
                last_values["averages"]["small_icm_failure_rate"]
                last_values["averages"]["error_mod"]
            """

            # In case one needs to iterate over
            # for i in range(len(last_values)):

            res = last_values["averages"]["large_fc_failure_rate"]
            icm_small = last_values["averages"]["small_icm_failure_rate"]
            error_mod = last_values["averages"]["error_mod"]

            # uncomment below` for flag and icm error plotted together
            plt.scatter(int(circuit_size), res, color='red')
            plt.scatter(int(circuit_size), icm_small, color='blue')
            plt.ylabel("logic`al error rate")

            # uncomment below for difference between flag and icm error
            # plt.scatter(int(circuit_size), (res - icm_small), color='red')
            # plt.ylabel("logical error rate difference")

            # uncomment below for flag error mod
            # plt.scatter(int(circuit_size), float(error_mod), color='blue')
            # plt.ylabel("flag error mod")

            # # uncomment below for flag qubit amount
            # import cirq
            # circuits_path = "misc/circuits2/"  # remember to pick correct path!
            # flag_circuit_path = circuits_path + "fc_" + circuit_type + "_" + str(circuit_size) + ".json"
            # flag_circuit: cirq.Circuit = cirq.read_json(flag_circuit_path)
            # fqs = list(filter(lambda q: 'f' in q.name, flag_circuit.all_qubits()))
            # n_of_fq = len(fqs)
            # plt.scatter(n_of_fq, float(error_mod))
            # plt.ylabel("flag error mod")
            # plt.xlabel("number of flag qubits, " + r'$\approx\sqrt{dq}$')

    plt.tight_layout()
    # plt.xlabel("circuit size")
    # plt.savefig("bigbudgetb123.png")

    # "./plots/bigbdgtadderimprtmodfq.png"
    plt.savefig(plot_fname)
