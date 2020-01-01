from utils.stream import Reader
from utils.constants import Constants
from core.star import Star

constants = Constants()
reader = Reader('app/samples/dj38.tsp', constants)
distance_matrix = reader.read_tsp()

# TODO: A universe :)
star = Star(distance_matrix, constants)
star.ignition()

