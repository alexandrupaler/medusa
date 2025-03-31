import os
import sys
import numpy as np
import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


if __name__ == '__main__':

    if len(sys.argv) < 2:
        CRED = '\033[91m'
        CEND = '\033[0m'
        print(CRED + "Will run only if provided two parameters:\n\t this_script [plot_file_name]" + CEND)
        exit(1)

    elif len(sys.argv) == 2:
        plot_fname = sys.argv[1]

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

    ncs = np.array([0.0001, 0.0003, 0.0005, 0.0007, 0.001])
    colors = ['red', 'blue', 'green', 'orange', 'purple']      
    error_mods = np.logspace(0.001, 1, 50)

    # find corresponding surface code distance for each error rate
    for e_i in range(len(ncs)):
        e = ncs[e_i]
        d = logical_error_scaling(e, error_mods)
        #plt.loglog(error_mods, (2*d**2-1), color=colors[e_i])
        plt.loglog(error_mods, d, color=colors[e_i])


    p1 = mpatches.Patch(color=colors[0], label=str(ncs[0]))
    p2 = mpatches.Patch(color=colors[1], label=str(ncs[1]))
    p3 = mpatches.Patch(color=colors[2], label=str(ncs[2]))
    p4 = mpatches.Patch(color=colors[3], label=str(ncs[3]))
    p5 = mpatches.Patch(color=colors[4], label=str(ncs[4]))

    plt.legend(handles=[p1, p2, p3, p4, p5])
    plt.xlabel("flag error mod")
    plt.ylabel("surface code distance")
    #plt.ylabel("surface code total qubits")
    plt.savefig(plot_fname)
