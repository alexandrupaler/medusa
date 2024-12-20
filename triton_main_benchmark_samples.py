import cirq.circuits
import cirq
import matplotlib.pyplot as plt
import pandas as pd
from multiprocessing import Pool
from preparation import compiler, test_circuits
from evaluation import evaluate
import numpy as np



if __name__ == '__main__':

    def parallel_simulation(i):

        qubits = i
        edge_probability = 0.5
        hadamards = 1.0

        number_of_runs = 1000
        error_rates = [0.0001, 0.0002, 0.0004, 0.0008, 0.001, 0.00125, 0.0025, 0.005, 0.01]
        
        e_num = len(error_rates)
        samples = 10

        results_1 = np.zeros(e_num)
        results_1_icm = np.zeros(e_num)
        results_2 = np.zeros(e_num)
        results_2_icm = np.zeros(e_num)
        results_3 = np.zeros(e_num)
        results_3_icm = np.zeros(e_num)

        for s in range(samples):

            c1 = compiler.FlagCompiler()
            c2 = compiler.FlagCompiler()
            c3 = compiler.FlagCompiler()

            icm_1: cirq.Circuit = c1.decompose_to_ICM(test_circuits.circuit_generator_1(qubits, edge_probability, hadamards), i=i)
            icm_2: cirq.Circuit = c2.decompose_to_ICM(test_circuits.circuit_generator_1(qubits, edge_probability, hadamards), i=i)
            icm_3: cirq.Circuit = c3.decompose_to_ICM(test_circuits.circuit_generator_1(qubits, edge_probability, hadamards), i=i)

            flag_1 = c1.add_flag(icm_1, strategy="heuristic")
            flag_2 = c2.add_flag(icm_2, strategy="heuristic")
            flag_3 = c3.add_flag(icm_3, strategy="heuristic")
        
            res_1, res_icm_1, a, b, c = evaluate.stabilizers_robustness_and_logical_error(flag_1, icm_1, number_of_runs, error_rates, False, "Adder " + str(i), "new noise model")
            res_2, res_icm_2, a, b, c = evaluate.stabilizers_robustness_and_logical_error(flag_2, icm_2, number_of_runs, error_rates, False, "Adder " + str(i), "new noise model")
            res_3, res_icm_3, a, b, c = evaluate.stabilizers_robustness_and_logical_error(flag_3, icm_3, number_of_runs, error_rates, False, "Adder " + str(i), "new noise model")

            results_1 = results_1 + res_1
            results_2 = results_2 + res_2
            results_3 = results_3 + res_3
            results_1_icm = results_1_icm + res_icm_1
            results_2_icm = results_2_icm + res_icm_2
            results_3_icm = results_3_icm + res_icm_3

        results_1 = results_1 / e_num
        results_2 = results_2 / e_num
        results_3 = results_3 / e_num
        results_1_icm = results_1_icm / e_num
        results_2_icm = results_2_icm / e_num
        results_3_icm = results_3_icm / e_num

        # save as csvs
        res_df_1 = pd.DataFrame(results_1)
        res_df_2 = pd.DataFrame(results_2)
        res_df_3 = pd.DataFrame(results_3)

        res_icm_df_1 = pd.DataFrame(results_1_icm)
        res_icm_df_2 = pd.DataFrame(results_2_icm)
        res_icm_df_3 = pd.DataFrame(results_3_icm)

        res_df_1.to_csv("results_1" + str(i) + ".csv",index=False)
        res_df_2.to_csv("results_2" + str(i) + ".csv",index=False)
        res_df_3.to_csv("results_3" + str(i) + ".csv",index=False)

        res_icm_df_1.to_csv("results_icm_1" + str(i) + ".csv",index=False)
        res_icm_df_2.to_csv("results_icm_2" + str(i) + ".csv",index=False)
        res_icm_df_3.to_csv("results_icm_3" + str(i) + ".csv",index=False)


    paramlist = [3,4,5,6,7] #[2,3,4,5,6,7]
    error_rates = [0.0001, 0.0002, 0.0004, 0.0008, 0.001, 0.00125, 0.0025, 0.005, 0.01]
    pool = Pool()
    pool.map(parallel_simulation, paramlist)
    pool.close()
    pool.join()

    # plotting
    
    plt.title("Imeprefct Flags on 10 Benchmark Circuits")
    for p in paramlist:
        results1 = pd.read_csv("results_1" + str(p) + ".csv")
        results2 = pd.read_csv("results_2" + str(p) + ".csv")
        results3 = pd.read_csv("results_3" + str(p) + ".csv")

        icm1 = pd.read_csv("results_icm_1" + str(p) + ".csv")
        icm2 = pd.read_csv("results_icm_2" + str(p) + ".csv")
        icm3 = pd.read_csv("results_icm_3" + str(p) + ".csv")

        plt.loglog(error_rates, results1, label="b1 flag")
        plt.loglog(error_rates, results2, label="b2 flag")
        plt.loglog(error_rates, results3, label="b3 flag")

        plt.loglog(error_rates, icm1, label="b1 icm")
        plt.loglog(error_rates, icm2, label="b2 icm")
        plt.loglog(error_rates, icm3, label="b3 icm")


    plt.xlabel('noise channel strength')
    plt.ylabel('logical error rate')
    plt.legend()
    filename = "becnhmark_samples_imperfect.png"
    plt.savefig(filename)
    plt.close()
