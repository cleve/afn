from enum import Enum


class ElementType(Enum):
    '''Three possible states
    '''
    HIDROGEN = 0
    HELIUM = 1
    CARBON = 2


class Constants:
    '''Main class
    '''

    def __init__(self):
        self.DEBUG = True

        # Config
        self.INTEGER = True  # Distance
        self.REGION = 5      # Units of separation for temperature representation
