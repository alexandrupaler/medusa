import os
import sys
import numpy as np
import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


if __name__ == '__main__':

    if len(sys.argv) < 3:
        CRED = '\033[91m'
        CEND = '\033[0m'
        print(CRED + "Will run only if provided two parameters:\n\t this_script [path_of_jsons] [plot_file_name]" + CEND)
        exit(1)

    elif len(sys.argv) == 3:
        path = sys.argv[1]
        plot_fname = sys.argv[2]

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

        if 'adder' in str(circuit_type):
            
            # get error mod from file
            last_values = {}
            with open(f"{path}/{filename}", "r") as report:
                last_values = json.load(report)
            error_mods = last_values["error_mod"]

            # find corresponding surface code distance for each error rate
            colors = ['red','blue', 'green', 'orange']
            for e_i in range(len(ncs)):
                e = ncs[e_i]
                mod = error_mods[e_i]
                d = logical_error_scaling(e, mod)
                plt.scatter(mod, d, color=colors[e_i])

    reds = mpatches.Patch(color='red', label=str(ncs[0]))
    blues = mpatches.Patch(color='blue', label=str(ncs[1]))
    greens = mpatches.Patch(color='green', label=str(ncs[2]))
    oranges = mpatches.Patch(color='orange', label=str(ncs[3]))

    plt.legend(handles=[reds, blues, greens, oranges])
    plt.xlabel("flag error mod")
    plt.ylabel("surface code distance")
    plt.savefig(plot_fname)
