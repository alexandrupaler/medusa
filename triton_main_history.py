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

    # triton cpus:
    # - lots :)

    number_of_runs = 10000
    error_rate = 0.001
    n_of_circuit_samples = 0
    epsilon_target = 0.005

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


    def run_simulation(icm_circuit, flag_circuit):
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

        circuit_type, circuit_size = inp

        # this is to avoid problems when only dealing with adders (i.e. 0 benchmark circuit samples)
        circuit_samples = max(n_of_circuit_samples, 1)

        """
        last_values = {
            "large_fc_failure_rate": np.zeros(circuit_samples),
            "large_icm_failure_rate": np.zeros(circuit_samples),
            "small_icm_failure_rate": np.zeros(circuit_samples),
            "error_mod": np.zeros(circuit_samples),
            "averages": {
                "large_fc_failure_rate": -1,
                "large_icm_failure_rate": -1,
                "small_icm_failure_rate": -1,
                "error_mod": -1
            }
        }
        """
        logical_error_rates = {
            "fc_failure_rate": np.zeros(circuit_samples),
            "icm_failure_rate": np.zeros(circuit_samples),
            "averages": {
                "fc_failure_rate": -1,
                "icm_failure_rate": -1,
            }
        }

        for sample_id in range(circuit_samples):

            # fetch circuit files
            icm = cirq.read_json(f"{config['circuits']}icm_{circuit_type}_{circuit_size}_{sample_id}.json")
            fc = cirq.read_json(f"{config['circuits']}fc_{circuit_type}_{circuit_size}_{sample_id}.json")

            # run simulation
            fc_failure_rate, icm_failure_rate = run_simulation(icm, fc)

            # Save the last values for later analysis, [0] is because results are in arrays
            logical_error_rates["fc_failure_rate"][sample_id] = fc_failure_rate[0]
            logical_error_rates["icm_failure_rate"][sample_id] = icm_failure_rate[0]

        # Compute averages
        logical_error_rates["averages"]["fc_failure_rate"] = np.average(logical_error_rates["fc_failure_rate"])
        logical_error_rates["averages"]["icm_failure_rate"] = np.average(logical_error_rates["icm_failure_rate"])

        # error: "Object of type ndarray is not JSON serializable"
        # solution is to pass default function to json.dump
        def numpy_to_list(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            raise TypeError('Not serializable')

        with open(f"{config['logs']}/report_{circuit_type}_{circuit_size}_{error_rate}.json", "w") as report:
            json.dump(logical_error_rates, report, default=numpy_to_list)


    # uncomment to generate circuit jsons
    generate_circuits(min_qubits=4, max_qubits=40, number_of_bench_samples=n_of_circuit_samples, path=config["circuits"], chosen_flags = 10)

    circuit_sizes = range(5, 40 + 1)
    circuit_types = ["adder"] #"b1", "b2", "b3"]

    paramlist = list(itertools.product(circuit_types, circuit_sizes))

    procs = len(paramlist) + 1

    # max number of processes
    maxprocs = 120
    pool = Pool(processes=procs)
    pool.map(parallel_simulation, paramlist)
    pool.close()
    pool.join()

    # check what size icm circuit the perfect flag circuit reaches
    smallest_possible_size = np.zeros(len(paramlist))
    for i in range(len(paramlist)):
        params = paramlist[i]
        c_type , size_big = params

        logical_error_rates_big = {}
        with open(f"{config['logs']}/report_{c_type}_{size_big}_{error_rate}.json", "r") as report:
            logical_error_rates_big = json.load(report)

        fc_logical_error = logical_error_rates_big["averages"]["fc_failure_rate"]
        icm_logical_error = logical_error_rates_big["averages"]["icm_failure_rate"]
        
        size_small = size_big

        while fc_logical_error < icm_logical_error and size_small > 4:

            logical_error_rates_small = {}
            with open(f"{config['logs']}/report_{c_type}_{size_small}_{error_rate}.json", "r") as report:
                logical_error_rates_small = json.load(report)
            
            icm_logical_error = logical_error_rates_small["averages"]["icm_failure_rate"]
            size_small -= 1

        smallest_possible_size[i] = size_small
    
    #for (i, item) in enumerate(smallest_possible_size, start=5):
    #    print(i, item)

    # plot
    plt.scatter(circuit_sizes, smallest_possible_size)
    plt.ylabel("smallest possible icm size")
    plt.xlabel("flag circuit size")
    plt.savefig("history.png")