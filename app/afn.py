from utils.stream import Reader
from utils.constants import Constants
from utils.helper import Helper
from core.star import Star


def main():
    constants = Constants()
    reader = Reader('samples/dj38.tsp', constants)
    base_elements = reader.read_tsp()
    minimal = None
    min_elements = None
    for i in range(1000):
        star = Star(base_elements, constants)
        star.life()
        elements = Helper.fision(star.elements)
        distance_matrix = reader.build_distance_matrix()
        temporal = int(Helper.path_size(elements, distance_matrix))
        if minimal is None:
            minimal = temporal
            min_elements = elements
        elif temporal < minimal:
            minimal = temporal
            min_elements = elements

    print(min_elements, ':', minimal)


if __name__ == "__main__":
    main()
