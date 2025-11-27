import json
import itertools
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D



if __name__ == '__main__':

    plt.rcParams.update({'font.size': 18})
    plt.rcParams["figure.figsize"] = (8,3.25)

    base_error = 0.0001
    epsilon_target = 0.0005
    n_of_circuit_samples = 0 # benchmark samples
    min_q = 5
    max_q = 40
    circuit_types = ["adder"]
    flag_n = "all"
    logs_path = f"error_mod_sim/unique_{flag_n}"


    error_rates = [1, 10, 100] 
    error_mods = [1.0, 0.66, 0.33, 0.0]

    e = 1
    error_rate = base_error * error_rates[e]

    circuit_sizes = range(min_q, max_q + 1)
    paramlist = list(itertools.product(circuit_types, circuit_sizes))

    # check what size icm circuit the perfect flag circuit reaches
    smallest_possible_size = np.zeros([len(paramlist),len(error_rates)])

    colors = ['red', 'orange', 'green', 'blue']

    results_fc = np.zeros([max_q - 5, 4])

    x_test = [5, 10, 15]
    y_test = np.zeros([3, 4])
    y_i = 0
    for j in range(len(paramlist)):
        params = paramlist[j]
        c_type , c_size = params

        last_values = {}
        with open(f"{logs_path}/logs/report_{circuit_types[0]}_{c_size}_{error_rates}.json", "r") as report:
                    last_values = json.load(report)
            
        fc_logical_errors = last_values["large_fc_failure_rate"][e]
        results_fc[c_size - 6, :] = fc_logical_errors

        if c_size in x_test:
            y_test[y_i, :] = fc_logical_errors
            y_i += 1


    # plot
    """
    plt.plot(circuit_sizes[0:-1], results_fc[:,0], label=error_mods[0], color='red')
    plt.plot(circuit_sizes[0:-1], results_fc[:,1], label=error_mods[1], color='orange')
    plt.plot(circuit_sizes[0:-1], results_fc[:,2], label=error_mods[2], color='green')
    plt.plot(circuit_sizes[0:-1], results_fc[:,3], label=error_mods[3], color='blue')
    #plt.title(f"with {flag_n} flags, ncs = {error_rate}")
    """
    plt.grid()

    plt.barh(x_test, y_test[:,0], label=error_mods[0], height=2)
    plt.barh(x_test, y_test[:,1], label=error_mods[1], height=2)
    plt.barh(x_test, y_test[:,2], label=error_mods[2], height=2)
    plt.barh(x_test, y_test[:,3], label=error_mods[3], height=2)

    plt.legend() 

    plt.xlabel("logical error rate")
    plt.ylabel("flag circuit size")
    plt.tight_layout()
    #plt.xticks(x_test)
    #bbox_inches='tight'
    plt.savefig(f"paper_plots_error_mod_unique_{flag_n}_wider_testii.png")