import json
import itertools
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D



if __name__ == '__main__':

    base_error = 0.0001
    epsilon_target = 0.0005
    n_of_circuit_samples = 0 # benchmark samples
    min_q = 5
    max_q = 26 #40
    circuit_types = ["adder"]
    logs_path = "error_mod_sim/unique_5log"

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

    for j in range(len(paramlist)):
        params = paramlist[j]
        c_type , c_size = params

        last_values = {}
        with open(f"{logs_path}/logs/report_{circuit_types[0]}_{c_size}_{error_rates}.json", "r") as report:
                    last_values = json.load(report)
            
        fc_logical_errors = last_values["large_fc_failure_rate"][e]
        results_fc[c_size - 6, :] = fc_logical_errors

    # plot
    plt.plot(circuit_sizes[0:-1], results_fc[:,0], label=error_mods[0], color='red')
    plt.plot(circuit_sizes[0:-1], results_fc[:,1], label=error_mods[1], color='orange')
    plt.plot(circuit_sizes[0:-1], results_fc[:,2], label=error_mods[2], color='green')
    plt.plot(circuit_sizes[0:-1], results_fc[:,3], label=error_mods[3], color='blue')
    plt.legend() 
    plt.grid()
    plt.title(f"with 5log flags, ncs = {error_rate}")
    plt.ylabel("logical error rate")
    plt.xlabel("flag circuit size")
    plt.savefig("error_mod_unique_5log.png")