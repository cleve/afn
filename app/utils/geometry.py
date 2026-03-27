from math import sqrt


def euclidean_distance(p_0, p_1):
    """Return the Euclidean distance between two 2D points."""
    return sqrt((p_1[0] - p_0[0]) ** 2 + (p_1[1] - p_0[1]) ** 2)


def midpoint(left, right):
    """Return the midpoint between two elements with x/y coordinates."""
    return ((left.x + right.x) / 2, (left.y + right.y) / 2)