import os
import sys
import numpy as np
import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


if __name__ == '__main__':

    if len(sys.argv) < 4:
        CRED = '\033[91m'
        CEND = '\033[0m'
        print(CRED + "Will run only if provided two parameters:\n\t this_script [path_of_jsons] [plot_file_name] [qubit_setting]" + CEND)
        exit(1)

    elif len(sys.argv) == 4:
        path = sys.argv[1]
        plot_fname = sys.argv[2]
        qubit_setting = sys.argv[3]

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

    files = list(filter(lambda f: f.startswith("report_"), os.listdir(path)))
    files.sort(key=lambda w: int(w.split("_")[2]))

    # physical error rate for flag qubits is 2 or 3 * ncs -> avg 2.5 * ncs
    ncs = np.array([1, 5, 7, 10]) * 0.0001 #* 2.5

    for filename in files:

        parts = filename.split("_")
        circuit_type = parts[1]
        circuit_size = int(parts[2])

        if 'adder' in str(circuit_type):
            
            # get error mod from file
            last_values = {}
            with open(f"{path}/{filename}", "r") as report:
                last_values = json.load(report)
            error_mods = last_values["error_mod"]
            
            data_count = (circuit_size * 3) - 1 # 3x-1
            flag_count = (circuit_size * 5) - 5 # 5x-5 all flags

            # 10 flags
            if qubit_setting == "10":
                flag_count = 10
            # all unique flags
            elif qubit_setting == "all_unique":
                flag_count = data_count
            # all flags 5x-5
            elif qubit_setting == "log":
                flag_count = round(3 * np.log2(circuit_size))

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

            ncs = np.array([0.0001, 0.0005, 0.0007, 0.001])
            colors = ['red', 'blue', 'green', 'orange']      

            # find corresponding surface code distance for each error rate
            for e_i in range(len(ncs)):
                e = ncs[e_i]
                error_mod = error_mods[e_i]
                d = np.ceil(logical_error_scaling(e, error_mod))
                surface_q_count = 2*d**2-1
                total_qubits = data_count + (flag_count * surface_q_count)
                plt.scatter(error_mod, total_qubits, color=colors[e_i])

    p1 = mpatches.Patch(color=colors[0], label=str(ncs[0]))
    p2 = mpatches.Patch(color=colors[1], label=str(ncs[1]))
    p3 = mpatches.Patch(color=colors[2], label=str(ncs[2]))
    p4 = mpatches.Patch(color=colors[3], label=str(ncs[3]))

    plt.legend(handles=[p1, p2, p3, p4])
    plt.xlabel("flag error mod")
    #plt.xlabel("circuit size")
    plt.ylabel("total qubits")
    print(plot_fname)
    plt.savefig(plot_fname)
