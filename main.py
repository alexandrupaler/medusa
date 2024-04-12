from preparation import compiler, test_circuits
from evaluation import evaluate
from preparation.error_map import Error_Map


if __name__ == '__main__':

    c = compiler.FlagCompiler()

    icm_circuit = c.decompose_to_ICM(test_circuits.test_circuit2())

    # f_cir = c.add_flag(icm_circuit,number_of_x_flag=3,number_of_z_flag=3)
    f_cir = c.add_flag(icm_circuit, strategy="map")
    # f_cir = c.add_flag(icm_circuit, strategy="heuristic")

    print("\n")
    print(f_cir)
    print("\n")

    evaluate.evaluate_flag_circuit(f_cir, maximum_number_of_error=1)

    # evaluate.evaluate_flag_circuit(f_cir, maximum_number_of_error=2)

