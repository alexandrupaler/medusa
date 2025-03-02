import os
import sys
import matplotlib.pyplot as plt
import cirq
import json
import numpy as np

if __name__ == '__main__':

    if len(sys.argv) < 2:
        CRED = '\033[91m'
        CEND = '\033[0m'
        print(CRED + "Will run only if provided one parameters:\n\t this_script [path_of_jsons]" + CEND)
        exit(1)

    elif len(sys.argv) == 2:
        path = sys.argv[1]

    files = list(filter(lambda f: f.startswith("fc_adder_"), os.listdir(path)))
    files.sort(key=lambda w: int(w.split("_")[2]))

    for file in files:
        circ_size = file.split("_")[2]
        flag_circuit: cirq.Circuit = cirq.read_json(path + "/" + file)
        dqs = flag_circuit.all_qubits()
        fqs = list(filter(lambda q: 'f' in q.name, flag_circuit.all_qubits()))
        n_of_q = len(flag_circuit.all_qubits())
        n_of_fq = len(fqs)
        n_of_dq = n_of_q - n_of_fq
        
        print(circ_size, n_of_fq, len(dqs))
        plt.scatter(circ_size, n_of_dq, c='red')
        plt.scatter(circ_size, n_of_fq, c='blue')
        plt.scatter(circ_size, n_of_q, c='green')
        
    #plt.tight_layout()
    plt.xticks(np.arange(5, 40, 5)) # assumption! for formatting
    plt.savefig("qubit_counts_10.png")