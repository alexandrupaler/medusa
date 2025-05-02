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

    number_of_runs = 100 #10000
    base_error = 0.0001
    error_rates = [1, 3, 5, 7, 10] 
    epsilon_target = 0.0005
    n_of_circuit_samples = 10 # benchmark samples
    min_q = 5
    max_q = 10
    circuit_types = ["b1"]
    chosen_flags = -5

    """
        Create backups and logs
    """
    bkp_folder_name = datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
    config = {"circuits": f"precomputed/{chosen_flags}/circuits/", "logs": f"{bkp_folder_name}/logs/"}
    # Create the logs folder
    Path(config["logs"]).mkdir(parents=True, exist_ok=True)
    # Copy the main script into the backup folder
    fname = os.path.basename(__file__)
    my_file = pathlib.Path(f"{fname}")
    to_file = pathlib.Path(f"{bkp_folder_name}/{fname}")
    shutil.copy(my_file, to_file)

    def get_precomp_errors(circuit_type, circuit_size):

        # format:
        # last_values = {
        #    "fc_failure_rate": np.zeros((circuit_samples,len(error_rates))),
        #    "icm_failure_rate": np.zeros((circuit_samples,len(error_rates))),
        #    "averages": {
        #        "fc_failure_rate": np.zeros(len(error_rates)),
        #        "icm_failure_rate": np.zeros(len(error_rates)),
        #    }
        # }

        filename = f"report_{circuit_type}_{circuit_size}_{error_rates}.json"
        logs_path = config["circuits"]

        with open(f"{logs_path}/{filename}", "r") as report:
                last_values = json.load(report)
        
        icm_failure_rate = last_values["averages"]["icm_failure_rate"]

        return icm_failure_rate


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

        last_values = {
            "large_fc_failure_rate": np.zeros((circuit_samples,len(error_rates))),
            "large_icm_failure_rate": np.zeros((circuit_samples,len(error_rates))),
            "small_icm_failure_rate": np.zeros((circuit_samples,len(error_rates))),
            "error_mod": np.zeros((circuit_samples,len(error_rates))),
            "averages": {
                "large_fc_failure_rate": np.zeros(len(error_rates)),
                "large_icm_failure_rate": np.zeros(len(error_rates)),
                "small_icm_failure_rate": np.zeros(len(error_rates)),
                "error_mod": np.zeros(len(error_rates))
            }
        }

        # get precomputed error rates
        small_icm_failure_rates = get_precomp_errors(circuit_type, circuit_size)

        for sample_id in range(circuit_samples):

            # get icm and flag i logical circuits
            large_icm = cirq.read_json(f"{config['circuits']}icm_{circuit_type}_{circuit_size}_{sample_id}.json")
            large_fc = cirq.read_json(f"{config['circuits']}fc_{circuit_type}_{circuit_size}_{sample_id}.json")

            # TODO: this could be done in parallel maybe
            for e in range(len(error_rates)):

                error_rate = error_rates[e] * base_error

                # get precomputed error rate for icm small
                small_icm_failure_rate = small_icm_failure_rates[e]

                # expected range
                er_a = 0.0
                er_b = 1.0

                done = False
                max_runs = 100
                while (not done) and (max_runs > 0):

                    max_runs -= 1

                    error_mod = (er_a + er_b) / 2
                    large_fc_failure_rate, large_icm_failure_rate = run_simulation(large_icm, large_fc, error_mod, error_rate)

                    diff = small_icm_failure_rate - large_fc_failure_rate
                    warnings.warn(str(diff))

                    if abs(diff) < epsilon_target:  # abs(diff) / res_icm_small < goal:
                        done = True

                        # Save the last values for later analysis
                        last_values["large_fc_failure_rate"][sample_id, e] = large_fc_failure_rate[0]
                        last_values["large_icm_failure_rate"][sample_id, e] = large_icm_failure_rate[0]
                        last_values["small_icm_failure_rate"][sample_id, e] = small_icm_failure_rate[0]
                        last_values["error_mod"][sample_id, e] = error_mod

                    elif diff < 0:
                        print("-")
                        er_b = error_mod
                    else:
                        print("+")
                        er_a = error_mod

        # Compute averages
        last_values["averages"]["large_fc_failure_rate"] = np.average(last_values["large_fc_failure_rate"], axis=0)
        last_values["averages"]["large_icm_failure_rate"] = np.average(last_values["large_icm_failure_rate"], axis=0)
        last_values["averages"]["small_icm_failure_rate"] = np.average(last_values["small_icm_failure_rate"], axis=0)
        last_values["averages"]["error_mod"] = np.average(last_values["error_mod"], axis=0)

        # error: "Object of type ndarray is not JSON serializable"
        # solution is to pass default function to json.dump
        def numpy_to_list(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            raise TypeError('Not serializable')

        with open(f"{config['logs']}/report_{circuit_type}_{circuit_size}_{error_rates}.json", "w") as report:
            json.dump(last_values, report, default=numpy_to_list)


    circuit_sizes = range(min_q, max_q + 1)
    
    paramlist = list(itertools.product(circuit_types, circuit_sizes))

    procs = len(paramlist) + 1

    # max number of processes
    maxprocs = 100
    pool = Pool(processes=min(procs, maxprocs))
    pool.map(parallel_simulation, paramlist)
    pool.close()
    pool.join()
