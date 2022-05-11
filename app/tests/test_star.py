import unittest
from core.element import Element
from core.star import Star
from utils.constants import ElementType


class TestStarMethods(unittest.TestCase):
    
    def setUp(self) -> None:
        self.element = Element(1, 0, 0, ElementType.HIDROGEN)
        self.elements = [(1, 0, 0)]
        self.star = Star([(1, 0, 0)], [[0]])
        return super().setUp()

    def test_get_next_element_type(self):
        assert self.star._get_next_element_type(
            ElementType.HIDROGEN) == ElementType.HELIUM
        assert self.star._get_next_element_type(
            ElementType.HELIUM) == ElementType.CARBON
        assert self.star._get_next_element_type(
            ElementType.CARBON) == ElementType.CARBON
    
    def test_ignition(self):
        assert len(self.star.elements) == 1


if __name__ == '__main__':
    unittest.main()
