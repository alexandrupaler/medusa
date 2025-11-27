import os
import sys
import numpy as np
import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


if __name__ == '__main__':

    plt.rcParams.update({'font.size': 18})

    if len(sys.argv) < 2:
        CRED = '\033[91m'
        CEND = '\033[0m'
        print(CRED + "Will run only if provided one parameter:\n\t this_script [plot_file_name]" + CEND)
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
    label_stuff = ['1e-4', '3e-4', '5e-4', '7e-4', '10e-4']
    colors = ['red', 'blue', 'green', 'orange', 'purple']      
    error_mods = np.logspace(-3, 0, 50) # base 10

    fig1, ax1 = plt.subplots(1)
    fig2, ax2 = plt.subplots(1)

    # find corresponding surface code distance for each error rate
    for e_i in range(len(ncs)):
        e = ncs[e_i]
        d = np.ceil(logical_error_scaling(e, error_mods))
        # round to next odd integer
        d[d % 2 == 0] = d[d % 2 == 0] + 1
        #d = logical_error_scaling(e, error_mods)
        ax1.semilogx(error_mods, (2*d**2-1), color=colors[e_i])
        ax2.semilogx(error_mods, d, color=colors[e_i])


    p1 = mpatches.Patch(color=colors[0], label=label_stuff[0])
    p2 = mpatches.Patch(color=colors[1], label=label_stuff[1])
    p3 = mpatches.Patch(color=colors[2], label=label_stuff[2])
    p4 = mpatches.Patch(color=colors[3], label=label_stuff[3])
    p5 = mpatches.Patch(color=colors[4], label=label_stuff[4])

    ax1.legend(handles=[p1, p2, p3, p4, p5])
    ax1.set_xlabel("flag error mod")
    ax1.set_ylabel("surface code total qubits")
    fig1.tight_layout()
    fig1.savefig(f"{plot_fname}.png")

    ax2.legend(handles=[p1, p2, p3, p4, p5])
    ax2.set_xlabel("flag error mod")
    ax2.set_ylabel("surface code distance")
    fig2.tight_layout()
    fig2.savefig(f"{plot_fname}_d.png")
