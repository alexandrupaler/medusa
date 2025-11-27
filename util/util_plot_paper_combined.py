import os
import sys
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches
import cirq
import json
import numpy as np

if __name__ == '__main__':

    plt.rcParams.update({'font.size': 18})

    if len(sys.argv) < 5:
        CRED = '\033[91m'
        CEND = '\033[0m'
        print(CRED + "Will run only if provided three parameters:\n\t this_script [folder_path] [chosen_circuit_type] [qubit_setting] [plot_file_name_base]" + CEND)
        exit(1)

    elif len(sys.argv) == 5:
        folder_path = sys.argv[1]
        chosen_circuit_types = sys.argv[2]
        qubit_setting = sys.argv[3]
        plot_file_name_base = sys.argv[4]

        logs_path_1 = f"paper/10-3/{folder_path}/logs"
        logs_path_2 = f"paper/10-4/{folder_path}/logs"

    results_fc = np.zeros((8,10)) # size, error_rate
    results_icm = np.zeros((8,10)) # size, error_rate
    results_acc = np.zeros((8,10)) # size, error_rate

    files = list(filter(lambda f: f.startswith("report_"), os.listdir(logs_path_1)))
    files.sort(key=lambda w: int(w.split("_")[2]))
    
    chosen_circuit_sizes = [5, 10, 15, 20, 25, 30, 35, 40]

    for filename in files:

        parts = filename.split("_")
        circuit_type = parts[1]
        circuit_size = int(parts[2])

        if chosen_circuit_types in str(circuit_type) and circuit_size in chosen_circuit_sizes:
            # If you know the circuit type, size and error_rate
            # then you can load the json and read the values from the dictionary
            last_values = {}
            with open(f"{logs_path_1}/{filename}", "r") as report:
                last_values = json.load(report)

            fc_res = last_values["large_fc_failure_rate"]
            icm_res = last_values["large_icm_failure_rate"]
            acceptance = last_values["acceptance"]

            results_fc[circuit_size // 5 - 1, 5:10] = fc_res
            results_icm[circuit_size // 5 - 1, 5:10] = icm_res
            results_acc[circuit_size // 5 - 1, 5:10] = acceptance

    files = list(filter(lambda f: f.startswith("report_"), os.listdir(logs_path_2)))
    files.sort(key=lambda w: int(w.split("_")[2]))

    for filename in files:

        parts = filename.split("_")
        circuit_type = parts[1]
        circuit_size = int(parts[2])

        if chosen_circuit_types in str(circuit_type) and circuit_size in chosen_circuit_sizes:
            # If you know the circuit type, size and error_rate
            # then you can load the json and read the values from the dictionary
            last_values = {}
            with open(f"{logs_path_2}/{filename}", "r") as report:
                last_values = json.load(report)

            fc_res = last_values["large_fc_failure_rate"]
            icm_res = last_values["large_icm_failure_rate"]
            acceptance = last_values["acceptance"]

            results_fc[circuit_size // 5 - 1, 0:5] = fc_res
            results_icm[circuit_size // 5 - 1, 0:5] = icm_res
            results_acc[circuit_size // 5 - 1, 0:5] = acceptance


    # plotting
    fig1, ax1 = plt.subplots(1)
    fig2, ax2 = plt.subplots(1)
    fig3, ax3 = plt.subplots(1)

    colors = ['red', 'blue', 'green', 'orange', 'purple', 'olive', 'cyan', 'pink']
    error_rates = np.array([1, 3, 5, 7, 10, 10, 30, 50, 70, 100]) * 0.0001 
    
    for i in range(0,8):

        circuit_size_color = colors[i]

        ax1.loglog(error_rates, results_icm[i,:] - results_fc[i,:], color=circuit_size_color, label=f"size {i*5+5}")
        
        ax2.loglog(error_rates, results_acc[i,:], color=circuit_size_color, label=f"size {i*5+5}")

        ax3.loglog(error_rates, results_fc[i,:], color=circuit_size_color, label=f"size {i*5+5}")

        
    #ax1.set_title(f"with {qubit_setting} flags")
    #ax2.set_title(f"with {qubit_setting} flags")
    ax1.set_ylabel(u'Δ logical error rate')
    ax1.set_xlabel("noise channel strength")
    ax2.set_ylabel("acceptance rate")
    ax2.set_xlabel("noise channel strength")
    ax3.set_ylabel("logical error rate")
    ax3.set_xlabel("noise channel strength")
    ax1.grid()
    ax2.grid()
    ax3.grid()
    ax1.legend()
    ax2.legend()
    ax3.legend()
    fig1.tight_layout()
    fig1.savefig(f"paper_plots_{plot_file_name_base}_delta.png")
    fig2.tight_layout()
    #fig2.savefig(f"paper_plots_{plot_file_name_base}_acceptance.png")
    fig3.tight_layout()
    #fig3.savefig(f"paper_plots_{plot_file_name_base}.png")

