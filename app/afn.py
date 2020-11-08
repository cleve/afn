from utils.stream import Reader
from utils.constants import Constants
from core.star import Star

constants = Constants()
reader = Reader('samples/dj38.tsp', constants)
base_elements = reader.read_tsp()
# TODO: A universe :)
star = Star(base_elements, constants)
star.life()
