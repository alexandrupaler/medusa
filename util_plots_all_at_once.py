import os
import sys
import matplotlib.pyplot as plt
import cirq
import json
import numpy as np

if __name__ == '__main__':

    if len(sys.argv) < 3:
        CRED = '\033[91m'
        CEND = '\033[0m'
        print(CRED + "Will run only if provided three parameters:\n\t this_script [folder_path] [chosen_circuit_type] [plot_file_name_base]" + CEND)
        exit(1)

    elif len(sys.argv) == 3:
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

            # flag and icm error plotted together
            ax1.scatter(int(circuit_size), res, color='red')
            ax1.scatter(int(circuit_size), icm_small, color='blue')
            ax1.ylabel("logical error rate")

            # difference between flag and icm error
            ax2.scatter(int(circuit_size), (res - icm_small), color='red')
            ax2.ylabel("logical error rate difference")

            # flag error mod
            colors = ['blue', 'green', 'orange', 'red']
            for e in range(len(error_rates)):
                ax3.scatter(int(circuit_size), float(error_mod[e]), color=colors[e])
            ax3.ylabel("flag error mod")

            # qubit amounts
            for circuit_sample in range(10):
                try:
                    circuit_file_name = f"fc_{circuit_type}_{circuit_size}_{circuit_sample}"
                    flag_circuit: cirq.Circuit = cirq.read_json(f"{circuits_path}/{circuit_file_name}")
                    all_qs = flag_circuit.all_qubits()
                    fqs = list(filter(lambda q: 'f' in q.name, all_qs))
                    n_of_q = len(all_qs)
                    n_of_fq = len(fqs)
                    n_of_dq = n_of_q - n_of_fq
                except:
                    print("no more circuit samples")
        
            ax4.scatter(circuit_size, n_of_dq, c='red')
            ax4.scatter(circuit_size, n_of_fq, c='blue')
            ax4.scatter(circuit_size, n_of_q, c='green')
            ax4.xticks(np.arange(5, 40, 5)) # assumption! for formatting

    fig1.tight_layout()
    fig2.tight_layout()
    fig3.tight_layout()
    fig4.tight_layout()

    fig1.savefig(f"{plot_file_name_base}.png")
    fig2.savefig(f"{plot_file_name_base}_diff.png")
    fig3.savefig(f"{plot_file_name_base}_mod.png")
    fig4.savefig(f"{plot_file_name_base}_qubits.png")