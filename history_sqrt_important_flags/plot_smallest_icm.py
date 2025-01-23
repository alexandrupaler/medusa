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

    bkp_folder_name = "01_16_2025_16_16_22"
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


    number_of_runs = 10000
    error_rate = 0.001
    n_of_circuit_samples = 0
    epsilon_target = 0.005

    circuit_sizes = range(5, 40 + 1)
    circuit_types = ["adder"] #"b1", "b2", "b3"]

    paramlist = list(itertools.product(circuit_types, circuit_sizes))

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
    
    for (i, item) in enumerate(smallest_possible_size, start=5):
        print(i, item)

    # plot
    plt.scatter(circuit_sizes, smallest_possible_size)
    plt.ylabel("smallest possible icm size")
    plt.xlabel("flag circuit size")
    plt.savefig("history.png")