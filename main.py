import cirq.circuits
from preparation import compiler, test_circuits
from evaluation import evaluate
import cirq
import numpy as np
import stimcirq
import matplotlib.pyplot as plt
from matplotlib import cm
import warnings
from multiprocessing import Pool
import itertools


if __name__ == '__main__':

    # todo:
    # - prepare 3d plot: 
        # - error 1% and 10%
        # - set number of flags
        # - adder size, 2-5
    # - prepare & send off to triton
    # - check if there are any bugs

    # bugs:
    # - map heuristic has a bug: doesn't work with the adder circuit

    #c = compiler.FlagCompiler()

    #icm_circuit: cirq.Circuit = c.decompose_to_ICM(test_circuits.test_circuit2())

    #adder2 = test_circuits.adder(2)
    #icm_circuit: cirq.Circuit = c.decompose_to_ICM(adder2)

    #print(icm_circuit)

    #f_cir_map = c.add_flag(icm_circuit, strategy="map")
    #f_cir_random = c.add_flag(icm_circuit,number_of_x_flag=3,number_of_z_flag=3)
    #f_cir_heuristic = c.add_flag(icm_circuit, strategy="heuristic")

    #print("\n")
    #print("Flags inserted!")
    #print("\n")

    #flag_circuit = f_cir_heuristic
    
    # plots the logical error rate of flagged and flagless circuit with different inpout states and error rates
    # the noise is randomized depolarising noise
    #
    #number_of_runs = 10
    #error_rates = np.linspace(0.001, 0.01, 3) #0.001, 0.05, 20)
    #evaluate.random_noise_benchmark(flag_circuit, icm_circuit, number_of_runs, error_rates)

    # calculates a error-propagation "failure" rate based on the weight of the errors for flagged and unflagged circuit
    # the errors are generated manually
    #
    # evaluate.evaluate_flag_circuit(flag_circuit, icm_circuit, 3, 100)


    #
    # 3D PLOT WITH ADDERS
    #

    # physical error, adder size, number of flags
    adders_and_flags = [2]
    n = len(adders_and_flags)

    res_flag0 = np.zeros((n, n))
    res_flag1 = np.zeros((n, n))
    res_flagless0 = np.zeros((n, n))
    res_flagless1 = np.zeros((n, n))


    c = compiler.FlagCompiler()
    
    def parallel_noise(params):

        i = params[0]
        j = params[1]

        a = adders_and_flags[i]

        adder = test_circuits.adder(a)
        icm_circuit: cirq.Circuit = c.decompose_to_ICM(adder,i,j)

        # warning because triton
        warnings.warn("compilation done for i & j, " + str(i) + " & " + str(j))
        
        f = adders_and_flags[j]
        flag_circuit = c.add_flag(icm_circuit,number_of_x_flag=f,number_of_z_flag=f)

        number_of_runs = 1
        error_rates = np.linspace(0.001, 0.01, 2) # 1% and 10%
        results, flagless_results = evaluate.random_noise_benchmark(flag_circuit, icm_circuit, number_of_runs, error_rates)
        res_flag0[i,j] = results[0,0]
        res_flag1[i,j] = results[1,0]
        res_flagless0[i,j] = flagless_results[0,0]
        res_flagless1[i,j] = flagless_results[1,0]

        # warning because triton
        warnings.warn("run i & j, " + str(i) + " & " + str(j) + ", is done")

        
    # run the above in parallel
    ij = range(len(adders_and_flags))
    paramlist = list(itertools.product(ij,ij))
    #print(paramlist)

    pool = Pool(processes=4)
    pool.map(parallel_noise, paramlist)
    pool.close()
    pool.join()
    
    # plotting
    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
    x, y = np.meshgrid(adders_and_flags, adders_and_flags)
    z = res_flag0
    surface = ax.plot_surface(x, y, z, cmap=cm.coolwarm)
    plt.xlabel("adder size")
    plt.ylabel("number of flags")
    plt.title("error: 1%")
    plt.colorbar(surface, shrink=0.5, aspect=5)

    plt.savefig("results_1.png")

    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
    x, y = np.meshgrid(adders_and_flags, adders_and_flags)
    z = res_flag1
    surface = ax.plot_surface(x, y, z, cmap=cm.coolwarm)
    plt.xlabel("adder size")
    plt.ylabel("number of flags")
    plt.title("error: 10%")
    plt.colorbar(surface, shrink=0.5, aspect=5)

    plt.savefig("results_10.png")


