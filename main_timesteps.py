import cirq.circuits
import cirq
import matplotlib.pyplot as plt
from preparation import compiler, test_circuits
from evaluation import evaluate


if __name__ == '__main__':

    # ONLY FOR TESTING PURPOSES ATM

    number_of_runs = 100
    error_rates = [0.0001, 0.0002, 0.0004, 0.0008, 0.001, 0.00125, 0.0025, 0.005, 0.01]
    c = compiler.FlagCompiler()
    circ = test_circuits.adder(3)

    # decompose
    icm_circuit: cirq.Circuit = c.decompose_to_ICM(circ)

    # add flags
    flag_circuit = c.add_flag(icm_circuit, number_of_x_flag=1, number_of_z_flag=1)

    # run simulation
    results, results_icm = evaluate.stabilizers_benchmark_with_timesteps(flag_circuit, icm_circuit, number_of_runs, error_rates[-1], True, "timesteps_perfect_flags.png", True)

    # plotting
    #plt.title("Logical Error Rate with Perfect Flags, Adder 5")
    #plt.loglog(error_rates, results)
    #plt.xlabel('noise channel strength')
    #plt.ylabel('logical error rate')
    #plt.show()
    #plt.savefig(filename)

