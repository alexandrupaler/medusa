import os
import sys
import matplotlib.pyplot as plt
import cirq
import json

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
        flag_circuit: cirq.Circuit = cirq.read_json(path + "/" + file)
        fqs = list(filter(lambda q: 'f' in q.name, flag_circuit.all_qubits()))
        n_of_fq = len(fqs)
        print(n_of_fq)