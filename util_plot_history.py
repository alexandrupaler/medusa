import json
import itertools
import numpy as np
import matplotlib.pyplot as plt


if __name__ == '__main__':

    base_error = 0.0001
    error_rates = [1, 3, 5, 7, 10, 30, 50, 70, 100] 
    epsilon_target = 0.0005
    n_of_circuit_samples = 0 # benchmark samples
    min_q = 5
    max_q = 40
    circuit_types = ["adder"]
    logs_path = "history_new/unique_all"

    circuit_sizes = range(min_q, max_q + 1)
    paramlist = list(itertools.product(circuit_types, circuit_sizes))

    # check what size icm circuit the perfect flag circuit reaches
    smallest_possible_size = np.zeros([len(paramlist),len(error_rates)])
    
    for e in range(len(error_rates)):
        error_rate = base_error * error_rates[e]
        
        for i in range(len(paramlist)):
            params = paramlist[i]
            c_type , size_big = params

            logical_error_rates_big = {}
            with open(f"{logs_path}/logs/report_{c_type}_{size_big}_{error_rates}.json", "r") as report:
                logical_error_rates_big = json.load(report)

            fc_logical_error = logical_error_rates_big["fc_failure_rate"][e]
            icm_logical_error = logical_error_rates_big["icm_failure_rate"][e]
            
            size_small = size_big

            while fc_logical_error < icm_logical_error and size_small > 4:

                logical_error_rates_small = {}
                with open(f"{logs_path}/logs/report_{c_type}_{size_small}_{error_rates}.json", "r") as report:
                    logical_error_rates_small = json.load(report)
                
                icm_logical_error = logical_error_rates_small["icm_failure_rate"][e]
                size_small -= 1

            plt.scatter(size_big, size_small)

            smallest_possible_size[i,e] = size_small
    
    for (i, item) in enumerate(smallest_possible_size, start=5):
        print(i, item)

    # plot
    plt.title("with all flags")
    plt.ylabel("smallest possible icm size")
    plt.xlabel("flag circuit size")
    plt.savefig("history_unique_all.png")