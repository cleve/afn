import random

class Utils:
    def get_randon_number(self):
        return str(random.randint(0, 10000))

    def get_randon_number_between(self, a, b):
        return str(random.randint(a, b))

    def matrix_avg(self, matrix):
        sz_matrix = len(matrix)
        total_sum = 0.0
        elements = 0.0
        for ii in range(sz_matrix):
            for jj in range(len(matrix[ii])):
                if matrix[ii][jj] != 0:
                    total_sum += matrix[ii][jj]
                    elements += 1
        return total_sum / elements if total_sum != 0 else 0