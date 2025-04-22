import json

from datetime import datetime
from pathlib import Path
import os
import pathlib
import shutil

import cirq.circuits
import cirq
import matplotlib.pyplot as plt
import warnings
import pandas as pd
import itertools
from multiprocessing import Pool
from preparation import compiler, test_circuits
from evaluation import evaluate
import numpy as np

from util_generator import generate_circuits

if __name__ == '__main__':

    # triton cpus:
    # - lots :)

    number_of_runs = 10000
    base_error = 0.0001
    error_rates = [1, 3, 5, 7, 10] 
    n_of_circuit_samples = 10 # benchmark samples
    min_q = 5
    max_q = 10
    circuit_types = ["adder","b1", "b2", "b3"]
    chosen_flags = -5

    """
        Create backups and logs
    """
    bkp_folder_name = f"precomputed/{chosen_flags}" #datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
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


    def run_simulation(icm_circuit, flag_circuit, error_mod, error_rate):
        results_flag, results_icm, _, _, _ = \
            evaluate.stabilizers_robustness_and_logical_error(flag_circuit,
                                                              icm_circuit,
                                                              number_of_runs,
                                                              [error_rate],
                                                              plotting=False,
                                                              plot_title="",
                                                              noise_type=f"budget{error_mod}")
        return results_flag, results_icm


    def parallel_simulation(inp, n_of_circuit_samples=n_of_circuit_samples):

        circuit_type, circuit_size = inp

        # this is to avoid problems when only dealing with adders (i.e. 0 benchmark circuit samples)
        circuit_samples = max(n_of_circuit_samples, 1)
        if circuit_type == "adder":
            circuit_samples = 1

        last_values = {
            "fc_failure_rate": np.zeros((circuit_samples,len(error_rates))),
            "icm_failure_rate": np.zeros((circuit_samples,len(error_rates))),
            "averages": {
                "fc_failure_rate": np.zeros(len(error_rates)),
                "icm_failure_rate": np.zeros(len(error_rates)),
            }
        }

        for sample_id in range(circuit_samples):

            # get icm i-1 logical error rate
            icm = cirq.read_json(f"{config['circuits']}icm_{circuit_type}_{circuit_size}_{sample_id}.json")
            fc = cirq.read_json(f"{config['circuits']}fc_{circuit_type}_{circuit_size}_{sample_id}.json")

            # TODO: this could be done in parallel maybe
            for e in range(len(error_rates)):

                error_rate = error_rates[e] * base_error

                # TODO: the i-1 could be done elsewhere
                fc_failure_rate, icm_failure_rate = run_simulation(icm, fc, 1, error_rate)
                
                last_values["fc_failure_rate"][sample_id, e] = fc_failure_rate[0]
                last_values["icm_failure_rate"][sample_id, e] = icm_failure_rate[0]

        # Compute averages
        last_values["averages"]["fc_failure_rate"] = np.average(last_values["fc_failure_rate"], axis=0)
        last_values["averages"]["icm_failure_rate"] = np.average(last_values["icm_failure_rate"], axis=0)

        # error: "Object of type ndarray is not JSON serializable"
        # solution is to pass default function to json.dump
        def numpy_to_list(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            raise TypeError('Not serializable')

        with open(f"{config['logs']}/report_{circuit_type}_{circuit_size}_{error_rates}.json", "w") as report:
            json.dump(last_values, report, default=numpy_to_list)


    # uncomment to generate circuit jsons
    generate_circuits(min_qubits=min_q-1, max_qubits=max_q+1, number_of_bench_samples=n_of_circuit_samples, path=config["circuits"], chosen_flags=chosen_flags)

    circuit_sizes = range(min_q, max_q + 1)
    
    paramlist = list(itertools.product(circuit_types, circuit_sizes))

    procs = len(paramlist) + 1

    # max number of processes
    maxprocs = 100
    pool = Pool(processes=min(procs, maxprocs))
    pool.map(parallel_simulation, paramlist)
    pool.close()
    pool.join()
