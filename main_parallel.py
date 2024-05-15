import cirq.circuits
from preparation import compiler, test_circuits
from evaluation import evaluate
import cirq
import numpy as np
import stimcirq
import matplotlib.pyplot as plt
from matplotlib import cm
import warnings
from multiprocessing import Pool, shared_memory
import itertools
import pandas as pd


if __name__ == '__main__':    

    adders = [2, 3, 4]
    flags = [1, 2, 3]
    n = len(adders)

    init_flag0 = np.zeros((n, n))
    init_flag1 = np.zeros((n, n))
    init_flagless0 = np.zeros((n, n))
    init_flagless1 = np.zeros((n, n))

    ntype = init_flag0.dtype

    # add these to the shared memory
    shared_flag0 = shared_memory.SharedMemory(create=True, size=init_flag0.nbytes)
    shared_flag1 = shared_memory.SharedMemory(create=True, size=init_flag1.nbytes)
    shared_flagless0 = shared_memory.SharedMemory(create=True, size=init_flagless0.nbytes)
    shared_flagless1 = shared_memory.SharedMemory(create=True, size=init_flagless1.nbytes)

    name_flag0 = shared_flag0.name
    name_flag1 = shared_flag1.name
    name_flagless0 = shared_flagless0.name
    name_flagless1 = shared_flagless1.name

    res_flag0 = np.ndarray(init_flag0.shape, dtype=ntype, buffer=shared_flag0.buf)
    res_flag1 = np.ndarray(init_flag1.shape, dtype=ntype, buffer=shared_flag1.buf)
    res_flagless0 = np.ndarray(init_flagless0.shape, dtype=ntype, buffer=shared_flagless0.buf)
    res_flagless1 = np.ndarray(init_flagless1.shape, dtype=ntype, buffer=shared_flagless1.buf)


    c = compiler.FlagCompiler()
    
    def parallel_noise(params):

        exist_flag0 = shared_memory.SharedMemory(name=name_flag0)
        exist_flag1 = shared_memory.SharedMemory(name=name_flag1)
        exist_flagless0 = shared_memory.SharedMemory(name=name_flagless0)
        exist_flagless1 = shared_memory.SharedMemory(name=name_flagless1)

        mid_flag0 = np.ndarray((n,n), dtype=ntype, buffer=exist_flag0.buf)
        mid_flag1 = np.ndarray((n,n), dtype=ntype, buffer=exist_flag1.buf)
        mid_flagless0 = np.ndarray((n,n), dtype=ntype, buffer=exist_flagless0.buf)
        mid_flagless1 = np.ndarray((n,n), dtype=ntype, buffer=exist_flagless1.buf)


        i = params[0]
        j = params[1]

        a = adders[i]

        adder = test_circuits.adder(a)

        icm_circuit: cirq.Circuit = c.decompose_to_ICM(adder,i,j)

        # for testing
        # icm_circuit = c.decompose_to_ICM(test_circuits.test_circuit2(),i,j)

        # warning because triton
        warnings.warn("compilation done for i & j, " + str(i) + " & " + str(j))
        
        f = flags[j]
        flag_circuit = c.add_flag(icm_circuit,strategy="heuristic")#number_of_x_flag=f,number_of_z_flag=f)

        number_of_runs = 3
        error_rates = np.linspace(0.001, 0.01, 2) # 1% and 10%
        results, flagless_results = evaluate.random_noise_benchmark(flag_circuit, icm_circuit, number_of_runs, error_rates, False)
        
        mid_flag0[i,j] = results[0,0]
        mid_flag1[i,j] = results[1,0]
        mid_flagless0[i,j] = flagless_results[0,0]
        mid_flagless1[i,j] = flagless_results[1,0]

        # warning because triton
        warnings.warn("run i & j, " + str(i) + " & " + str(j) + ", is done")

        exist_flag0.close()
        exist_flag1.close()
        exist_flagless0.close()
        exist_flagless1.close()

        
    # run the above in parallel
    ij = range(len(adders))
    paramlist = list(itertools.product(ij,ij))
    #print(paramlist)

    pool = Pool(processes=4)
    pool.map(parallel_noise, paramlist)
    pool.close()
    pool.join()

    # plotting
    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
    x, y = np.meshgrid(adders, flags)
    z = res_flag0
    surface = ax.plot_surface(x, y, z, cmap=cm.coolwarm)
    plt.xlabel("adder size")
    plt.ylabel("number of flags")
    plt.title("error: 0.1%")
    plt.colorbar(surface, shrink=0.5, aspect=5)

    #plt.show()
    plt.savefig("results_1_par.png")

    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
    x, y = np.meshgrid(adders, flags)
    z = res_flag1
    surface = ax.plot_surface(x, y, z, cmap=cm.coolwarm)
    plt.xlabel("adder size")
    plt.ylabel("number of flags")
    plt.title("error: 1%")
    plt.colorbar(surface, shrink=0.5, aspect=5)

    #plt.show()
    plt.savefig("results_10_par.png")

    # save as csv
    df = pd.DataFrame(res_flag0)
    df.to_csv('res_flag_01_par.csv',index=False)

    df = pd.DataFrame(res_flag1)
    df.to_csv('res_flag_1_par.csv',index=False)

    shared_flag0.unlink()
    shared_flag1.unlink()
    shared_flagless0.unlink()
    shared_flagless1.unlink()

    shared_flag0.close()
    shared_flag1.close()
    shared_flagless0.close()
    shared_flagless1.close()
