# attempt of implementation of https://robertheaton.com/2018/12/17/wavefunction-collapse-algorithm/
import copy
import math
import random
from math import trunc


class EvenSimplerTiledModel:
    def __init__(self, initial_matrix: list[list]) -> None:
        self._initial_matrix = initial_matrix
        self._entry_nums = {}
        self._rules = set()
        self._dictionary = set()
        self._superposition = "*"
        self._history = []
        for i in initial_matrix:
            for j in i:
                if j in self._entry_nums:
                    self._entry_nums[j] += 1
                else:
                    self._entry_nums[j] = 1
                    self._dictionary.add(j)

        for i in range(len(initial_matrix)):
            for j in range(len(initial_matrix[i])):
                if i > 0:
                    self._rules.add((initial_matrix[i - 1][j], initial_matrix[i][j], "UP"))
                if i < len(initial_matrix) - 1:
                    self._rules.add((initial_matrix[i + 1][j], initial_matrix[i][j], "DOWN"))
                if j > 0:
                    self._rules.add((initial_matrix[i][j - 1], initial_matrix[i][j], "LEFT"))
                if j < len(initial_matrix[i]) - 1:
                    self._rules.add((initial_matrix[i][j + 1], initial_matrix[i][j], "RIGHT"))

    def fill_with_random_percent(self, matrix: list[list], percent_fill: int) -> list[list]:
        total_len = len(matrix) * len(matrix[0])
        indexes = list(range(total_len))
        copied_matrix = copy.copy(matrix)
        to_choose_from = list(self._dictionary)
        for _i in range(round(total_len * percent_fill / 100)):
            j = indexes[random.randrange(0, len(indexes), 1)]
            indexes.remove(j)
            copied_matrix[trunc(j / len(matrix))][j % len(matrix[0])] = random.choice(to_choose_from)
        return copied_matrix

    def get_superposition(self) -> str:
        return self._superposition

    def collapse(self, matrix: list[list], max_attempts: int = -1) -> list[list]:
        current_attempts = 0
        while current_attempts < max_attempts or max_attempts == -1:
            copied_matrix = copy.deepcopy(matrix)
            self._history.clear()
            for i in range(len(matrix)):
                for j in range(len(matrix[i])):
                    if copied_matrix[i][j] == self._superposition:
                        copied_matrix[i][j] = copy.deepcopy(self._dictionary)
            while not self.is_diverges(copied_matrix):
                self.update_history(copied_matrix)
                copied_matrix_with_rules = self.apply_rules(copied_matrix)
                pos = self.get_minimal_index_by_shannon_entropy_for_square(copied_matrix_with_rules)
                self.collapse_element(copied_matrix_with_rules, pos)
                copied_matrix = copied_matrix_with_rules
                if self.is_collapsed(copied_matrix):
                    self.update_history(copied_matrix)
                    return copied_matrix
            current_attempts += 1
        raise Exception("Failed to collapse, exceeded max attempts.")

    def is_collapsed(self, matrix: list[list]) -> bool:
        for i in matrix:
            for j in i:
                if j not in self._dictionary:
                    return False
        return True

    def is_diverges(self, matrix: list[list]) -> bool:
        for i in matrix:
            for j in i:
                if isinstance(j, set) and len(j) == 0:
                    return True
        return False

    def apply_rules(self, matrix: list[list]) -> list[list]:
        matrix_copy = copy.deepcopy(matrix)
        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                if not isinstance(matrix[i][j], set):
                    continue
                possible_variants_up = set()
                possible_variants_down = set()
                possible_variants_left = set()
                possible_variants_right = set()
                for rule_dictator, possible_variant, position in self._rules:
                    match position:
                        case "UP":
                            if i > 0 and (matrix[i - 1][j] == rule_dictator or
                                          (isinstance(matrix[i - 1][j], set) and rule_dictator in matrix[i - 1][j])):
                                possible_variants_up.add(possible_variant)
                            elif i == 0:
                                possible_variants_up.update(self._dictionary)
                        case "DOWN":
                            if i < len(matrix) - 1 and (matrix[i + 1][j] == rule_dictator or
                                                        (isinstance(matrix[i + 1][j], set) and rule_dictator in
                                                         matrix[i + 1][j])):
                                possible_variants_down.add(possible_variant)
                            elif i == len(matrix) - 1:
                                possible_variants_down.update(self._dictionary)
                        case "LEFT":
                            if j > 0 and (matrix[i][j - 1] == rule_dictator or
                                          (isinstance(matrix[i][j - 1], set) and rule_dictator in matrix[i][j - 1])):
                                possible_variants_left.add(possible_variant)
                            elif j == 0:
                                possible_variants_left.update(self._dictionary)
                        case "RIGHT":
                            if j < len(matrix[i]) - 1 and (
                                    matrix[i][j + 1] == rule_dictator or
                                    (isinstance(matrix[i][j + 1], set) and rule_dictator in matrix[i][j + 1])):
                                possible_variants_right.add(possible_variant)
                            elif j == len(matrix[i]) - 1:
                                possible_variants_right.update(self._dictionary)
                matrix_copy[i][j].intersection_update(possible_variants_up, possible_variants_down,
                                                      possible_variants_left, possible_variants_right)

        return matrix_copy

    def get_minimal_index_by_shannon_entropy_for_square(self, matrix: list[list]) -> (int, int):
        current_min = float("inf")
        pos = None
        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                if not isinstance(matrix[i][j], set):
                    continue
                sum_of_weights = 0
                sum_of_weight_log_weights = 0
                for k in matrix[i][j]:
                    sum_of_weights += self._entry_nums[k]
                    sum_of_weight_log_weights += self._entry_nums[k] * math.log(self._entry_nums[k])
                shannon_entropy_for_square = math.log(sum_of_weights) - (sum_of_weight_log_weights / sum_of_weights)
                if current_min > shannon_entropy_for_square:
                    current_min = shannon_entropy_for_square
                    pos = (i, j)
        return pos

    def collapse_element(self, matrix: list[list], pos: (int, int)) -> None:
        i, j = pos
        items = list(matrix[i][j])
        matrix[i][j] = random.choices(items, weights=[self._entry_nums[x] for x in items])[0]

    def update_history(self, matrix: list[list]) -> None:
        temp = copy.deepcopy(matrix)
        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                if temp[i][j] not in self._dictionary:
                    temp[i][j] = copy.deepcopy(self._superposition)
        self._history.append(temp)

    def get_history(self) -> list[list]:
        return self._history
