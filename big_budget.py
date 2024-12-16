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

from generator_utils import generate_circuits

if __name__ == '__main__':

    # triton cpus:
    # - lots :)

    number_of_runs = 10
    error_rate = 0.001
    epsilon_target = 0.005

    """
        Create backups and logs
    """
    bkp_folder_name = datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
    config = {"circuits": "/circuits/", "logs": f"{bkp_folder_name}/logs/"}
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


    def parallel_simulation(inp, number_of_samples):

        circuit_type, circuit_size = inp

        last_values = {
            "large_fc_failure_rate": np.zeros(number_of_samples),
            "large_icm_failure_rate": np.zeros(number_of_samples),
            "small_icm_failure_rate": np.zeros(number_of_samples),
            "error_mod": np.zeros(number_of_samples),
            "averages": {
                "large_fc_failure_rate": -1,
                "large_icm_failure_rate": -1,
                "small_icm_failure_rate": -1,
                "error_mod": -1
            }
        }

        for sample_i in range(number_of_samples):

            # fetch circuit files
            # get icm i-1 logical error rate
            small_icm = cirq.read_json(f"{config['circuits']}/icm_{circuit_type}_{circuit_size - 1}_{sample_i}.json")
            small_fc = cirq.read_json(f"{config['circuits']}/fc_{circuit_type}_{circuit_size - 1}_{sample_i}.json")

            # get icm and flag i logical error rate
            large_icm = cirq.read_json(f"{config['circuits']}/icm_{circuit_type}_{circuit_size}_{sample_i}.json")
            large_fc = cirq.read_json(f"{config['circuits']}/fc_{circuit_type}_{circuit_size}_{sample_i}.json")

            # TODO: the i-1 could be done elsewhere
            _, small_icm_failure_rate = run_simulation(small_icm, small_fc, 1, error_rate)

            # expected range is [0.3, 1.0]
            er_a = 0.3
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
                    last_values["large_fc_failure_rate"][sample_i] = large_fc_failure_rate
                    last_values["large_icm_failure_rate"][sample_i] = large_icm_failure_rate
                    last_values["small_icm_failure_rate"][sample_i] = small_icm_failure_rate
                    last_values["error_mod"][sample_i] = error_mod

                elif diff < 0:
                    print("-")
                    er_b = error_mod
                else:
                    print("+")
                    er_a = error_mod


        # Compute averages
        last_values["averages"]["large_fc_failure_rate"] = np.average(last_values["large_fc_failure_rate"])
        last_values["averages"]["large_icm_failure_rate"] = np.average(last_values["large_icm_failure_rate"])
        last_values["averages"]["small_icm_failure_rate"] = np.average(last_values["small_icm_failure_rate"])
        last_values["averages"]["error_mod"] = np.average(last_values["error_mod"])

        with open(f"{config['logs']}/report_{circuit_type}_{circuit_size}_{error_rate}.json", "w") as report:
            json.dump(last_values, report)

        # save as CSVs - single value per file - legacy
        err_mod_avg = last_values["averages"]["error_mod"]
        res_df = pd.DataFrame(last_values["averages"]["large_fc_failure_rate"])
        res_df.to_csv(f"{config['logs']}/fc_{circuit_type}_{circuit_size}_{err_mod_avg}_{error_rate}.csv", index=False)
        res_icm_df = pd.DataFrame(last_values["averages"]["large_icm_failure_rate"])
        res_icm_df.to_csv(f"{config['logs']}/icm_{circuit_type}_{circuit_size}_{err_mod_avg}_{error_rate}.csv",
                          index=False)
        res_icm_small_df = pd.DataFrame(last_values["averages"]["small_icm_failure_rate"])
        res_icm_small_df.to_csv(
            f"{config['logs']}/icm_small_{circuit_type}_{circuit_size}_{err_mod_avg}_{error_rate}.csv", index=False)


    # uncomment to generate circuit jsons
    generate_circuits(min_qubits=4, max_qubits=40, number_of_bench_samples=1)

    circuit_sizes = range(5, 40 + 1)
    # circuit_types = ["adder", "b1", "b2", "b3"]
    circuit_types = ["b1", "b2", "b3"]

    paramlist = list(itertools.product(circuit_types, circuit_sizes))

    procs = len(paramlist) + 1

    # max number of processes
    maxprocs = 4
    pool = Pool(processes=procs)
    pool.map(parallel_simulation, paramlist)
    pool.close()
    pool.join()
