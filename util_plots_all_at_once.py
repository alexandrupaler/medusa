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
        chosen_circuit_type = sys.argv[2]
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

    error_rates = [1*0.0001, 5*0.0001, 7*0.0001, 10*0.0001] 

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

    for filename in files:

        parts = filename.split("_")
        circuit_type = parts[1]
        circuit_size = int(parts[2])

        # Check the circuit type
        if chosen_circuit_type in str(circuit_type):
            # If you know the circuit type, size and error_rate
            # then you can load the json and read the values from the dictionary
            last_values = {}
            with open(f"{logs_path}/{filename}", "r") as report:
                last_values = json.load(report)

            #res = last_values["averages"]["large_fc_failure_rate"]
            #icm_small = last_values["averages"]["small_icm_failure_rate"]
            #error_mods = last_values["averages"]["error_mod"]

            res = last_values["large_fc_failure_rate"]
            icm_small = last_values["small_icm_failure_rate"]
            error_mods = last_values["error_mod"]

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
                ax3.scatter(int(circuit_size), float(error_mods[e]), color=colors[e])
            ax3.set_ylabel("flag error mod")
            ax3.set_xlabel("circuit size")
            custom_lines = [Line2D([0], [0], color='blue', lw=4),
                Line2D([0], [0], color='green', lw=4),
                Line2D([0], [0], color='orange', lw=4),
                Line2D([0], [0], color='red', lw=4)]
            ax3.legend(custom_lines, ['1e-4', '5e-4', '7e-4', '10e-4'])

            # qubit amounts
            ns_of_q = np.zeros(10)
            ns_of_dq = np.zeros(10)
            ns_of_fq = np.zeros(10)
            for circuit_sample in range(10):
                try:
                    circuit_file_name = f"fc_{circuit_type}_{circuit_size}_{circuit_sample}.json"
                    flag_circuit: cirq.Circuit = cirq.read_json(f"{circuits_path}/{circuit_file_name}")
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

            data_count = (circuit_size * 3) - 1 # 3x-1
            flag_count = (circuit_size * 5) - 5 # 5x-5 all flags

            # 10 flags
            if qubit_setting == "10":
                flag_count = 10
            # all unique flags
            elif qubit_setting == "all_unique":
                flag_count = data_count
            # all flags 5x-5
            elif qubit_setting == "3log":
                flag_count = round(3 * np.log2(circuit_size))
            elif qubit_setting == "5log":
                flag_count = round(5 * np.log2(circuit_size))

            ncs = np.array([0.0001, 0.0005, 0.0007, 0.001])
            colors = ['red', 'blue', 'green', 'orange']      

            # find corresponding surface code distance for each error rate
            for e_i in range(len(ncs)):
                e = ncs[e_i]
                error_mod = error_mods[e_i]
                d = np.ceil(logical_error_scaling(e, error_mod))
                # round to next odd integer
                if d % 2 == 0:
                    d += 1
                surface_q_count = 2*d**2-1
                total_qubits = data_count + (flag_count * surface_q_count)
                ax5.scatter(error_mod, total_qubits, color=colors[e_i])
                ax6.scatter(circuit_size, total_qubits, color=colors[e_i])

            p1 = mpatches.Patch(color=colors[0], label=str(ncs[0]))
            p2 = mpatches.Patch(color=colors[1], label=str(ncs[1]))
            p3 = mpatches.Patch(color=colors[2], label=str(ncs[2]))
            p4 = mpatches.Patch(color=colors[3], label=str(ncs[3]))

            ax5.legend(handles=[p1, p2, p3, p4])
            ax6.legend(handles=[p1, p2, p3, p4])
            ax5.set_ylabel("total qubits")
            ax6.set_ylabel("total qubits")
            ax5.set_xlabel("flag error mod")
            ax6.set_xlabel("circuit size")

    fig1.tight_layout()
    fig2.tight_layout()
    fig3.tight_layout()
    fig4.tight_layout()
    fig5.tight_layout()
    fig6.tight_layout()


    fig1.savefig(f"{plot_file_name_base}.png")
    fig2.savefig(f"{plot_file_name_base}_diff.png")
    fig3.savefig(f"{plot_file_name_base}_mod.png")
    fig4.savefig(f"{plot_file_name_base}_qubits.png")
    fig5.savefig(f"{plot_file_name_base}_surface_mod.png")
    fig6.savefig(f"{plot_file_name_base}_surface_size.png")
