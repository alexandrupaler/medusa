import os
import sys
import matplotlib.pyplot as plt
import cirq
import json
import numpy as np

if __name__ == '__main__':

    if len(sys.argv) < 4:
        CRED = '\033[91m'
        CEND = '\033[0m'
        print(CRED + "Will run only if provided three parameters:\n\t this_script [folder_path] [chosen_circuit_type] [plot_file_name_base]" + CEND)
        exit(1)

    elif len(sys.argv) == 4:
        folder_path = sys.argv[1]
        chosen_circuit_type = sys.argv[2]
        plot_file_name_base = sys.argv[3]

        circuits_path = f"{folder_path}/circuits"
        logs_path = f"{folder_path}/logs"

    fig1, ax1 = plt.subplots(1)
    fig2, ax2 = plt.subplots(1)
    fig3, ax3 = plt.subplots(1)
    fig4, ax4 = plt.subplots(1)
    fig5, ax5 = plt.subplots(1)

    error_rates = [1*0.0001, 5*0.0001, 7*0.0001, 10*0.0001] 

    files = list(filter(lambda f: f.startswith("report_"), os.listdir(logs_path)))
    files.sort(key=lambda w: int(w.split("_")[2]))

    for filename in files:

        parts = filename.split("_")
        circuit_type = parts[1]
        circuit_size = parts[2]

        # Check the circuit type
        if chosen_circuit_type in str(circuit_type):
            # If you know the circuit type, size and error_rate
            # then you can load the json and read the values from the dictionary
            last_values = {}
            with open(f"{logs_path}/{filename}", "r") as report:
                last_values = json.load(report)

            #res = last_values["averages"]["large_fc_failure_rate"]
            #icm_small = last_values["averages"]["small_icm_failure_rate"]
            #error_mod = last_values["averages"]["error_mod"]

            res = last_values["large_fc_failure_rate"]
            icm_small = last_values["small_icm_failure_rate"]
            error_mod = last_values["error_mod"]

            circuit_size_array = np.full(len(error_rates), int(circuit_size))

            # flag and icm error plotted together
            ax1.scatter(circuit_size_array, res, color='red')
            ax1.scatter(circuit_size_array, icm_small, color='blue')
            ax1.set_ylabel("logical error rate")
            ax1.set_xlabel("circuit size")


            # difference between flag and icm error
            ax2.scatter(circuit_size_array, (np.array(res) - np.array(icm_small)), color='red')
            ax2.set_ylabel("logical error rate difference")
            ax2.set_xlabel("circuit size")

            # flag error mod
            colors = ['blue', 'green', 'orange', 'red']
            for e in range(len(error_rates)):
                ax3.scatter(int(circuit_size), float(error_mod[e]), color=colors[e])
            ax3.set_ylabel("flag error mod")
            ax3.set_xlabel("circuit size")

            # qubit amounts
            ns_of_q = np.zeros(10)
            ns_of_dq = np.zeros(10)
            ns_of_fq = np.zeros(10)
            for circuit_sample in range(10):
                try:
                    circuit_file_name = f"fc_{circuit_type}_{circuit_size}_{circuit_sample}"
                    flag_circuit: cirq.Circuit = cirq.read_json(f"{circuits_path}/{circuit_file_name}")
                    print(flag_circuit)
                    all_qs = flag_circuit.all_qubits()
                    fqs = list(filter(lambda q: 'f' in q.name, all_qs))
                    ns_of_q[circuit_sample] = len(all_qs)
                    ns_of_fq[circuit_sample] = len(fqs)
                    ns_of_dq[circuit_sample] = ns_of_q[circuit_sample] - ns_of_fq[circuit_sample]
                except:
                    print("")
            ax4.scatter(circuit_size, np.mean(ns_of_dq), c='red')
            ax4.scatter(circuit_size, np.mean(ns_of_fq), c='blue')
            ax4.scatter(circuit_size, np.mean(ns_of_q), c='green')
            ax4.set_xticks(np.arange(5, 40, 5)) # assumption! for formatting
            ax4.set_ylabel("qubits")
            ax4.set_xlabel("circuit size")


    fig1.tight_layout()
    fig2.tight_layout()
    fig3.tight_layout()
    fig4.tight_layout()

    fig1.savefig(f"{plot_file_name_base}.png")
    fig2.savefig(f"{plot_file_name_base}_diff.png")
    fig3.savefig(f"{plot_file_name_base}_mod.png")
    fig4.savefig(f"{plot_file_name_base}_qubits.png")