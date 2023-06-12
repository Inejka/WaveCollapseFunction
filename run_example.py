from EvenSimplerTiledModel import EvenSimplerTiledModel
from utils import init_matrix_superposition, load_simple_matrix_from_txt, record_history

if __name__ == "__main__":
    method = EvenSimplerTiledModel(load_simple_matrix_from_txt("SimpleData"))
    f = init_matrix_superposition(100, 100, "*")
    f[5][5] = "S"
    # f = method.fill_with_random_percent(f, 80)
    f = method.collapse(f, 40)
    record_history(method.get_history(), fps=60)
