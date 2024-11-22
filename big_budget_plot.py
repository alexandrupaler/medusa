import matplotlib.pyplot as plt
import pandas as pd
import os


if __name__ == '__main__':

    path = "adder2"
    error_rate = 0.001
    
    files = list(filter(lambda f: f.startswith("fc_"), os.listdir(path)))
    files.sort(key = lambda w: int(w.split("_")[2]))

    for filename in files:

        parts = filename.split("_")
        circuit_type = parts[1]
        circuit_size = parts[2]
        error_mod = parts[3]

        # "fc_" + circuit_type + "_" + str(circuit_size) + "_" + str(error_mod) + "_" + str(error_rate) + ".csv"
        res = pd.read_csv("adder2/fc_" + circuit_type + "_" + circuit_size + "_" + error_mod + "_" + str(error_rate) + ".csv")
        icm_small = pd.read_csv("adder2/icm_small_" + circuit_type + "_" + circuit_size + "_" + error_mod + "_" + str(error_rate) + ".csv")

        # uncomment below for flag and icm error plotted together
        #plt.scatter(int(circuit_size), res, color='red')
        #plt.scatter(int(circuit_size), icm_small, color='blue')
        #plt.ylabel("logical error rate")

        # uncomment below for difference between flag and icm error
        plt.scatter(int(circuit_size), (res - icm_small), color='red')
        plt.ylabel("logical error rate difference")
        
        # uncomment below for flag error mod
        #plt.scatter(int(circuit_size), error_mod, color='blue')
        #plt.ylabel("flag error mod")

    plt.xlabel("circuit size")
    plt.savefig("bigbudget2diff.png")