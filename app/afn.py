from utils.stream import Reader
from utils.constants import Constants
from utils.helper import Helper
from core.star import Star


def main():
    constants = Constants()
    reader = Reader('samples/dj38.tsp', constants)
    base_elements = reader.read_tsp()
    for i in range(500):
        star = Star(base_elements, constants)
        star.life()
        elements = Helper.fision(star.elements)
        distance_matrix = reader.build_distance_matrix()
        print(elements, ':', int(Helper.path_size(elements, distance_matrix)))


if __name__ == "__main__":
    main()
