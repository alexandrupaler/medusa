import os
import sys
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches
import cirq
import json
import numpy as np

if __name__ == '__main__':

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

        circuits_path = f"{folder_path}/circuits"
        logs_path = f"{folder_path}/logs"

    fig1, ax1 = plt.subplots(1)
    fig2, ax2 = plt.subplots(1)
    fig3, ax3 = plt.subplots(1)
    fig4, ax4 = plt.subplots(1)
    fig5, ax5 = plt.subplots(1)
    fig6, ax6 = plt.subplots(1)

    error_rates = [1*0.0001, 3*0.0001, 5*0.0001, 7*0.0001, 10*0.0001] 

    files = list(filter(lambda f: f.startswith("report_"), os.listdir(logs_path)))
    files.sort(key=lambda w: int(w.split("_")[2]))

    # calculates surface code distance which corresponds to certain error mod
    def logical_error_scaling(p_phys, mod):
        c = 0.08
        pth = 0.0053
        #de = 0.58 * d - 0.27
        #pl = c * (p_phys / pth)**(de)
        p_logic = p_phys * mod
        de = np.emath.logn(p_phys / pth, p_logic / c)
        d = (de + 0.27) / 0.58
        return d
    
    chosen_circuit_sizes = [5, 10, 15, 20, 25, 30, 35, 40]
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'olive', 'cyan', 'pink']

    for filename in files:

        parts = filename.split("_")
        circuit_type = parts[1]
        circuit_size = int(parts[2])

        if chosen_circuit_types in str(circuit_type) and circuit_size in chosen_circuit_sizes:
            # If you know the circuit type, size and error_rate
            # then you can load the json and read the values from the dictionary
            last_values = {}
            with open(f"{logs_path}/{filename}", "r") as report:
                last_values = json.load(report)

            fc_res = last_values["large_fc_failure_rate"]
            icm_res = last_values["large_icm_failure_rate"]
            acceptance = last_values["acceptance"]

            circuit_size_color = colors[circuit_size // 5 - 1]

            # flag and icm error plotted together
            ax1.scatter(error_rates, fc_res, color=circuit_size_color)
            ax1.set_ylabel("logical error rate")
            ax1.set_xlabel("noise channel strength")
            #custom_lines = [Line2D([0], [0], color='blue', lw=4), Line2D([0], [0], color='red', lw=4)]
            #ax1.legend(custom_lines, ['flag', 'icm'])          

    ax1.grid()
    fig1.tight_layout()
    fig1.savefig(f"{plot_file_name_base}.png")

