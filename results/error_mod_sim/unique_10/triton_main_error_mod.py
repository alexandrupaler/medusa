import json

from datetime import datetime
from pathlib import Path
import os
import pathlib
import shutil

import cirq
import itertools
from multiprocessing import Pool
from evaluation import evaluate
import numpy as np

from util_generator import generate_circuits

if __name__ == '__main__':

    # triton cpus:
    # - lots :)

    # ONLY WORKS WITH ADDERS

    number_of_runs = 10000
    base_error = 0.0001
    error_rates = [1, 10, 100] #[1, 3, 5, 7, 10, 30, 50, 70, 100] 
    error_mods = [1.0, 0.66, 0.33, 0.0]
    n_of_circuit_samples = 0 # benchmark samples
    min_q = 5
    max_q = 40
    circuit_types = ["adder"]
    chosen_flags = 10
    circuits_folder = "precompiled_circuits/unique_10"

    """
        Create backups and logs
    """
    bkp_folder_name = datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
    config = {"circuits": f"{circuits_folder}/", "logs": f"{bkp_folder_name}/logs/"}
    # Create the cicuit folder
    # Path(config["circuits"]).mkdir(parents=True, exist_ok=True)
    # Create the logs folder
    Path(config["logs"]).mkdir(parents=True, exist_ok=True)
    # Copy the main script into the backup folder
    fname = os.path.basename(__file__)
    my_file = pathlib.Path(f"{fname}")
    to_file = pathlib.Path(f"{bkp_folder_name}/{fname}")
    shutil.copy(my_file, to_file)


    def run_simulation(icm_circuit, flag_circuit, error_mod, error_rate):
        results_flag, results_icm, _, _, _, _, _ = \
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
            "large_fc_failure_rate": np.zeros((len(error_rates), len(error_mods))),
            "large_icm_failure_rate": np.zeros((len(error_rates), len(error_mods))),
        }

        # fetch circuit files
        sample_id = 0

        # get icm and flag i logical error rate
        large_icm = cirq.read_json(f"{config['circuits']}icm_{circuit_type}_{circuit_size}_{sample_id}.json")
        large_fc = cirq.read_json(f"{config['circuits']}fc_{circuit_type}_{circuit_size}_{sample_id}.json")

        # TODO: this could be done in parallel maybe
        for e in range(len(error_rates)):
            for m in range(len(error_mods)):

                error_rate = error_rates[e] * base_error
                error_mod = error_mods[m]
                
                large_fc_failure_rate, large_icm_failure_rate = run_simulation(large_icm, large_fc, error_mod, error_rate)

                # Save the last values for later analysis
                last_values["large_fc_failure_rate"][e, m] = large_fc_failure_rate[0]
                last_values["large_icm_failure_rate"][e, m] = large_icm_failure_rate[0]


        # error: "Object of type ndarray is not JSON serializable"
        # solution is to pass default function to json.dump
        def numpy_to_list(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            raise TypeError('Not serializable')

        with open(f"{config['logs']}/report_{circuit_type}_{circuit_size}_{error_rates}.json", "w") as report:
            json.dump(last_values, report, default=numpy_to_list)


    # uncomment to generate circuit jsons
    # generate_circuits(min_qubits=min_q-1, max_qubits=max_q+1, number_of_bench_samples=n_of_circuit_samples, path=config["circuits"], chosen_flags=chosen_flags)

    circuit_sizes = range(min_q, max_q + 1)
    
    paramlist = list(itertools.product(circuit_types, circuit_sizes))

    procs = len(paramlist) + 1

    # max number of processes
    maxprocs = 100
    pool = Pool(processes=min(procs, maxprocs))
    pool.map(parallel_simulation, paramlist)
    pool.close()
    pool.join()
