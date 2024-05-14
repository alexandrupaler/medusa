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


    """
    adders = [2, 3]
    flags = [1, 2]
    n = len(adders)

    res_flag0 = np.zeros((n, n))
    res_flag1 = np.zeros((n, n))
    res_flagless0 = np.zeros((n, n))
    res_flagless1 = np.zeros((n, n))


    c = compiler.FlagCompiler()
    
    def parallel_noise(params):

        i = params[0]
        j = params[1]

        a = adders[i]

        adder = test_circuits.adder(a)

        # testing
        #adder = test_circuits.replace_t_with_Z_map(adder)
        # testing

        icm_circuit: cirq.Circuit = c.decompose_to_ICM(adder,i,j)

        icm_circuit = c.decompose_to_ICM(test_circuits.test_circuit2(),i,j)

        # warning because triton
        warnings.warn("compilation done for i & j, " + str(i) + " & " + str(j))
        
        f = flags[j]
        flag_circuit = c.add_flag(icm_circuit,strategy="heuristic")#number_of_x_flag=f,number_of_z_flag=f)

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
    ij = range(len(adders))
    paramlist = list(itertools.product(ij,ij))
    #print(paramlist)

    for p in paramlist:
        parallel_noise(p)
    #pool = Pool(processes=4)
    #pool.map(parallel_noise, paramlist)
    #pool.close()
    #pool.join()
    
    # plotting
    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
    x, y = np.meshgrid(adders, flags)
    z = res_flag0
    surface = ax.plot_surface(x, y, z, cmap=cm.coolwarm)
    plt.xlabel("adder size")
    plt.ylabel("number of flags")
    plt.title("error: 1%")
    plt.colorbar(surface, shrink=0.5, aspect=5)

    plt.show()#plt.savefig("results_1.png")

    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
    x, y = np.meshgrid(adders, flags)
    z = res_flag1
    surface = ax.plot_surface(x, y, z, cmap=cm.coolwarm)
    plt.xlabel("adder size")
    plt.ylabel("number of flags")
    plt.title("error: 10%")
    plt.colorbar(surface, shrink=0.5, aspect=5)

    plt.show()#savefig("results_10.png")
    

    """
    #
    # 3D PLOT WITH ADDERS
    #

    adders = [2,3,4]
    flags = [1,2,3]

    na = len(adders)
    nf = len(flags)

    res_flag0 = np.zeros((na, nf))
    res_flag1 = np.zeros((na, nf))
    res_flagless0 = np.zeros((na, nf))
    res_flagless1 = np.zeros((na, nf))

    c = compiler.FlagCompiler()

    # adder size
    for i in range(len(adders)):
        a = adders[i]
        adder = test_circuits.adder(a)

        icm_circuit: cirq.Circuit = c.decompose_to_ICM(adder,i,0)#c.decompose_to_ICM(adder2)

        # number of flags
        for j in range(len(flags)):

            f = flags[j]
            flag_circuit = c.add_flag(icm_circuit,number_of_x_flag=f,number_of_z_flag=f)

            number_of_runs = 10
            error_rates = np.linspace(0.001, 0.01, 2) # 1% and 10%
            results, flagless_results = evaluate.random_noise_benchmark(flag_circuit, icm_circuit, number_of_runs, error_rates, plotting=False)
            res_flag0[i,j] = results[0,0]
            res_flag1[i,j] = results[1,0]
            res_flagless0[i,j] = flagless_results[0,0]
            res_flagless1[i,j] = flagless_results[1,0]

            # warning because triton
            warnings.warn("run done for i & j, " + str(i) + " & " + str(j))

    # plotting
    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
    x, y = np.meshgrid(adders, flags)
    z = res_flag0
    surface = ax.plot_surface(x, y, z, cmap=cm.coolwarm)
    plt.xlabel("adder size")
    plt.ylabel("number of flags")
    plt.title("error: 0.1%")
    plt.colorbar(surface, shrink=0.5, aspect=5)

    plt.savefig("results_1.png")

    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
    x, y = np.meshgrid(adders, flags)
    z = res_flag1
    surface = ax.plot_surface(x, y, z, cmap=cm.coolwarm)
    plt.xlabel("adder size")
    plt.ylabel("number of flags")
    plt.title("error: 1%")
    plt.colorbar(surface, shrink=0.5, aspect=5)

    plt.savefig("results_10.png")