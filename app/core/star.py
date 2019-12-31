from utils.utils import Utils
from core.element import Element

class Star:
    """Conditions are:

        Hight temperature: 100MK
        Fusion distance: 1x10-15m
    """
    def __init__(self):
        self.name = 'sun'

        # Physics parameters.
        self.temperature_map = None

        # Geometry.
        self.distances = None

    def ignition(self):
        pass