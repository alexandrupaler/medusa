import cirq.circuits
import cirq 
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from collections import Counter
import itertools
import os
import sys


#if __name__ == '__main__' and __package__ is None:
#    from os import sys, path
#    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
#    from evaluation import evaluate


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

    is_unique = []

    for file in files:
        circ_size = file.split("_")[2]
        flag_circuit: cirq.Circuit = cirq.read_json(path + "/" + file)
        
        # assuming everything is in its own moment
        n_of_moments = len(flag_circuit.moments)

        flag_qubits = list(filter(lambda q: 'f' in q.name, flag_circuit.all_qubits()))

        def is_this_a_moment_with_cnot(moment: cirq.Moment):
            for op in moment.operations:
                if len(op.qubits) == 2:
                    return True
            return False

        moments_with_index = list(zip(list(flag_circuit.moments), range(n_of_moments)))
        moments_with_cnot_and_index = list(filter(lambda a: is_this_a_moment_with_cnot(a[0]), moments_with_index))

        # group flags based on the qubit that they protect
        def group_func(fq: cirq.Qid):
            moments_with_fq = list(filter(lambda m: fq in m[0].qubits, moments_with_cnot_and_index))
            first_moment_with_fq = moments_with_fq[0]
            # find the qubit that is protected
            protected_qubit = first_moment_with_fq[0].operations[0].qubits[0] # control, target
            if 'z' in fq.name:
                protected_qubit = first_moment_with_fq[0].operations[0].qubits[1]
            return protected_qubit
        
        # group flags
        protected_qubits = []
        for k, g in itertools.groupby(flag_qubits, key=group_func):
            protected_qubits.extend([k])
            
        counts_of_protected_qubits = Counter(protected_qubits)

        #print(counts_of_protected_qubits.keys())
        #print(counts_of_protected_qubits.values())
        circuit_is_unique = all(x < 2 for x in counts_of_protected_qubits.values())
        is_unique.extend([circuit_is_unique])
    
    print(all(is_unique))