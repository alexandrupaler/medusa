import json

from datetime import datetime
from pathlib import Path
import os
import pathlib
import shutil

import cirq.circuits
import cirq
import warnings
import pandas as pd
import itertools
from multiprocessing import Pool
from evaluation import evaluate
import numpy as np
import matplotlib.pyplot as plt

from util_generator import generate_circuits

if __name__ == '__main__':

    # ONLY WORKS WITH ADDERS

    # triton cpus:
    # - lots :)

    number_of_runs = 10000
    base_error = 0.0001
    error_rates = [1, 5, 7, 10] 
    epsilon_target = 0.0005
    n_of_circuit_samples = 0 # benchmark samples
    min_q = 5
    max_q = 40
    circuit_types = ["adder"]
    chosen_flags = -1

    """
        Create backups and logs
    """
    bkp_folder_name = datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
    config = {"circuits": f"{bkp_folder_name}/circuits/", "logs": f"{bkp_folder_name}/logs/"}
    # Create the cicuit folder
    Path(config["circuits"]).mkdir(parents=True, exist_ok=True)
    # Create the logs folder
    Path(config["logs"]).mkdir(parents=True, exist_ok=True)
    # Copy the main script into the backup folder
    fname = os.path.basename(__file__)
    my_file = pathlib.Path(f"{fname}")
    to_file = pathlib.Path(f"{bkp_folder_name}/{fname}")
    shutil.copy(my_file, to_file)


    def run_simulation(icm_circuit, flag_circuit, error_rate):
        results_flag, results_icm, _, _, _ = \
            evaluate.stabilizers_robustness_and_logical_error(flag_circuit,
                                                              icm_circuit,
                                                              number_of_runs,
                                                              [error_rate],
                                                              plotting=False,
                                                              plot_title="",
                                                              noise_type="perfect flags")
        return results_flag, results_icm


    def parallel_simulation(inp, n_of_circuit_samples=n_of_circuit_samples):
    
        logical_error_rates = {
                "fc_failure_rate": np.zeros(len(error_rates)),
                "icm_failure_rate": np.zeros(len(error_rates)),
        }

        for e in range(len(error_rates)):

            error_rate = base_error * error_rates[e]
            circuit_type, circuit_size = inp

            warnings.warn("error rate: " + str(error_rate))

            # fetch circuit files
            sample_id = 0
            icm = cirq.read_json(f"{config['circuits']}icm_{circuit_type}_{circuit_size}_{sample_id}.json")
            fc = cirq.read_json(f"{config['circuits']}fc_{circuit_type}_{circuit_size}_{sample_id}.json")

            # run simulation
            fc_failure_rate, icm_failure_rate = run_simulation(icm, fc, error_rate)
            
            warnings.warn("failure rate: " + str(fc_failure_rate))

            # Save the last values for later analysis, [0] is because results are in arrays
            logical_error_rates["fc_failure_rate"][e] = fc_failure_rate[0]
            logical_error_rates["icm_failure_rate"][e] = icm_failure_rate[0]


        # error: "Object of type ndarray is not JSON serializable"
        # solution is to pass default function to json.dump
        def numpy_to_list(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            raise TypeError('Not serializable')

        with open(f"{config['logs']}/report_{circuit_type}_{circuit_size}_{error_rates}.json", "w") as report:
            json.dump(logical_error_rates, report, default=numpy_to_list)


    # uncomment to generate circuit jsons
    generate_circuits(min_qubits=min_q-1, max_qubits=max_q+1, number_of_bench_samples=n_of_circuit_samples, path=config["circuits"], chosen_flags = chosen_flags)

    circuit_sizes = range(min_q, max_q + 1)

    paramlist = list(itertools.product(circuit_types, circuit_sizes))

    procs = len(paramlist) + 1

    # max number of processes
    maxprocs = 120
    pool = Pool(processes=procs)
    pool.map(parallel_simulation, paramlist)
    pool.close()
    pool.join()

    # check what size icm circuit the perfect flag circuit reaches
    smallest_possible_size = np.zeros([len(paramlist),len(error_rates)])
    
    for e in range(len(error_rates)):
        error_rate = base_error * error_rates[e]
        
        for i in range(len(paramlist)):
            params = paramlist[i]
            c_type , size_big = params

            logical_error_rates_big = {}
            with open(f"{config['logs']}/report_{c_type}_{size_big}_{error_rates}.json", "r") as report:
                logical_error_rates_big = json.load(report)

            fc_logical_error = logical_error_rates_big["fc_failure_rate"][e]
            icm_logical_error = logical_error_rates_big["icm_failure_rate"][e]
            
            size_small = size_big

            while fc_logical_error < icm_logical_error and size_small > 4:

                logical_error_rates_small = {}
                with open(f"{config['logs']}/report_{c_type}_{size_small}_{error_rates}.json", "r") as report:
                    logical_error_rates_small = json.load(report)
                
                icm_logical_error = logical_error_rates_small["icm_failure_rate"][e]
                size_small -= 1

            plt.scatter(size_big, size_small)

            smallest_possible_size[i,e] = size_small
    
    for (i, item) in enumerate(smallest_possible_size, start=5):
        print(i, item)

    # plot
    plt.ylabel("smallest possible icm size")
    plt.xlabel("flag circuit size")
    plt.savefig("history.png")