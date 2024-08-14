import cirq.circuits
import cirq 
import matplotlib.pyplot as plt
import pandas as pd

if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from evaluation import evaluate


if __name__ == '__main__':

    data = cirq.NamedQubit("1")
    flag = cirq.NamedQubit("0xf")

    base = cirq.Circuit()
    base.append(cirq.CNOT(data, flag))
    base.append(cirq.CNOT(data, flag))
    base.append(cirq.M(flag))
    base.append(cirq.R(flag))

    icm_circuit = cirq.Circuit()
    icm_circuit.append(cirq.I(data))

    error_rates = [0.0001, 0.0002, 0.0004, 0.0008, 0.001, 0.00125, 0.0025, 0.005, 0.01]
    number_of_runs = 100

    # noiseless simulation
    noiseless, a, b, c, d = evaluate.stabilizers_robustness_and_logical_error(base, icm_circuit, number_of_runs, error_rates, False, "" , "noiseless")

    # noisy simulation
    noisy, a, b, c, d = evaluate.stabilizers_robustness_and_logical_error(base, icm_circuit, number_of_runs, error_rates, False, "" , "new noise model")

    # perfect flag simulation
    perfect_flags, a, b, c, d = evaluate.stabilizers_robustness_and_logical_error(base, icm_circuit, number_of_runs, error_rates, False, "" , "perfect flags")

    # save as csv
    df = pd.DataFrame(noiseless)
    df.to_csv('noiseless.csv',index=False)
    df = pd.DataFrame(noisy)
    df.to_csv('noisy.csv',index=False)
    df = pd.DataFrame(perfect_flags)
    df.to_csv('perfect_flags.csv',index=False)

    plt.title("Logical Error Rate for Different Noise Models")
    
    plt.loglog(error_rates, noiseless, label="noiseless")
    plt.loglog(error_rates, noisy, label="noisy")
    plt.loglog(error_rates, perfect_flags, label="perfect flags")

    plt.xlabel('noise channel strength')
    plt.ylabel('logical error rate')
    plt.legend()
    filename = "logical_error_noise_models.png"
    plt.savefig(filename)
    plt.close()
