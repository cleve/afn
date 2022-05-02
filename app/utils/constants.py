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
    DEBUG = True
    INTEGER = True
    REGION = 5
    LIMIT_TEMPERATURE = 170
