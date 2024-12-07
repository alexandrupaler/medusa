import cirq.circuits
import cirq
import matplotlib.pyplot as plt
import warnings
import pandas as pd
import itertools
from multiprocessing import Pool, shared_memory
from evaluation import evaluate
import numpy as np
import os


if __name__ == '__main__':

    # triton cpus:
    # - lots :)

    number_of_runs = 10000
    error_rate = 0.001
    path = "history/"

    circuit_sizes = range(5, 40+1)
    #circuit_types = ["adder", "b1", "b2", "b3"]
    circuit_types = ["adder"]

    paramlist = list(itertools.product(circuit_types, circuit_sizes))

    # use shared memory cause neater format for results
    init_res = np.zeros((len(circuit_sizes)))
    ntype = init_res.dtype
    shared_shape = init_res.shape
    shared_res = shared_memory.SharedMemory(create=True, size=init_res.nbytes)
    name_shared = shared_res.name
    final_res = np.ndarray(shared_shape, dtype=ntype, buffer=shared_res.buf)
    
    def run_simulation(icm_circuit, flag_circuit):
        results, _, _, _, _ = evaluate.stabilizers_robustness_and_logical_error(flag_circuit, icm_circuit, number_of_runs, [error_rate], False, "", "perfect flags")
        return results

    def parallel_simulation(inp):

        exist_res = shared_memory.SharedMemory(name=name_shared)
        mid_res = np.ndarray(shared_shape, dtype=ntype, buffer=exist_res.buf)

        circuit_type, circuit_size = inp

        # fetch flag qubit circuit files
        jsons_path = "circuits/"
        icm_file = jsons_path + "icm_" + circuit_type + "_" + str(circuit_size) + ".json"
        icm_circuit = cirq.read_json(icm_file)
        fc_file = jsons_path + "fc_" + circuit_type + "_" + str(circuit_size) + ".json"
        flag_circuit = cirq.read_json(fc_file)


        # run perfect flag simulation
        res = run_simulation(icm_circuit, flag_circuit)

        # check which icm adder this meets
        icm_res_path = "adder2/"        
        icm_files = list(filter(lambda f: f.startswith("icm_") and ("small" not in f), os.listdir(icm_res_path)))
        icm_files.sort(key = lambda w: int(w.split("_")[2]))

        i = -1
        for filename in icm_files:

            parts = filename.split("_")
            type = parts[1]
            size = parts[2]
            mod = parts[3]

            warnings.warn(size)

            if type == circuit_type:
                icm_res = pd.read_csv(icm_res_path + "icm_" + circuit_type + "_" + size + "_" + mod + "_" + str(error_rate) + ".csv")
                # update i and break loop when icm_res < res
                i = size
                if icm_res.to_numpy()[0][0] > res:
                    break
        warnings.warn("done: " + str(circuit_size))
        # save results
        mid_res[circuit_size - 5] = i
        exist_res.close()

    procs = len(paramlist) + 1
    pool = Pool()#processes=procs)
    pool.map(parallel_simulation, paramlist)
    pool.close()
    pool.join()

    # plotting
    x = range(5, 40+1)
    plt.scatter(x, final_res)
    plt.xlabel("circuit size")
    plt.ylabel("achieved icm size")
    plt.savefig("history.png")

    # save result as csv
    df = pd.DataFrame(final_res)
    df.to_csv('history_adder.csv',index=False)

    shared_res.unlink()
    shared_res.close()

