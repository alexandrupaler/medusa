import cirq.circuits
from preparation import compiler, test_circuits, error_circuit
from evaluation import evaluate
import cirq
import numpy as np
import stimcirq
import matplotlib.pyplot as plt
from matplotlib import cm
import warnings
from multiprocessing import Pool
import itertools
from multiprocessing import Pool, shared_memory
import time
import pandas as pd



if __name__ == '__main__':

    # todo:
    # - only "unique" circuits
    # bugs:
    # - map heuristic has a bug: doesn't work with the adder circuit

    

    c = compiler.FlagCompiler()

    icm_circuit: cirq.Circuit = c.decompose_to_ICM(test_circuits.adder(2))

    print("\n")
    print("Decompose done!")
    print("\n")

    print(icm_circuit)

    #f_cir_map = c.add_flag(icm_circuit, strategy="map")
    #f_cir_random = c.add_flag(icm_circuit,number_of_x_flag=3,number_of_z_flag=3)
    f_cir_heuristic = c.add_flag(icm_circuit, strategy="heuristic")

    print("\n")
    print("Flags inserted!")
    print("\n")

    flag_circuit = f_cir_heuristic

    print(flag_circuit)
    
    number_of_runs = 1000
    error_rates = np.linspace(0.001, 0.01, 5)
    #evaluate.random_noise_on_error_circuit(flag_circuit, icm_circuit, number_of_runs, error_rates, True, "error_results.png")
    evaluate.random_noise_on_error_circuit_alt(flag_circuit, icm_circuit, number_of_runs, error_rates, True, "results_stabilizers_adder5.png")

    """
    # 3D PLOT WITH ADDERS, PARALLEL

    #def adders_3d_parallel():
        
    adders = [2, 3]
    flags = [1, 2]
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

        start = time.time()

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

        # warning because triton
        warnings.warn("compilation done for i & j, " + str(i) + " & " + str(j))
        
        f = flags[j]
        flag_circuit = c.add_flag(icm_circuit,number_of_x_flag=f,number_of_z_flag=f)

        number_of_runs = 20
        error_rates = np.linspace(0.001, 0.01, 2) # 0.1% and 1%
        filename = "results_stabilizers" + str(i) + str(j) + ".png"
        results, flagless_results = evaluate.random_noise_on_error_circuit_alt(flag_circuit, icm_circuit, number_of_runs, error_rates, True, filename)
        
        mid_flag0[i,j] = results[0]
        mid_flag1[i,j] = results[1]
        mid_flagless0[i,j] = flagless_results[0]
        mid_flagless1[i,j] = flagless_results[1]

        # warning because triton
        end = time.time()
        duration = end - start
        warnings.warn("run i & j, " + str(i) + " & " + str(j) + ", is done. Time it took: " + str(duration))

        exist_flag0.close()
        exist_flag1.close()
        exist_flagless0.close()
        exist_flagless1.close()

      
    # run the above in parallel
    ij = range(len(adders))
    paramlist = list(itertools.product(ij,ij))

    #pool = Pool()
    #pool.map(parallel_noise, paramlist)
    #pool.close()
    #pool.join()

    for p in paramlist:
        parallel_noise(p)

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
    plt.savefig("results_error_01.png")

    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
    x, y = np.meshgrid(adders, flags)
    z = res_flag1
    surface = ax.plot_surface(x, y, z, cmap=cm.coolwarm)
    plt.xlabel("adder size")
    plt.ylabel("number of flags")
    plt.title("error: 1%")
    plt.colorbar(surface, shrink=0.5, aspect=5)

    #plt.show()
    plt.savefig("results_error_10.png")

    # save as csv
    df = pd.DataFrame(res_flag0)
    df.to_csv('results_error_01.csv',index=False)

    df = pd.DataFrame(res_flag1)
    df.to_csv('results_error_10.csv',index=False)

    shared_flag0.unlink()
    shared_flag1.unlink()
    shared_flagless0.unlink()
    shared_flagless1.unlink()

    shared_flag0.close()
    shared_flag1.close()
    shared_flagless0.close()
    shared_flagless1.close()

    """