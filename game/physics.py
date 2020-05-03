import math
from typing import List



class PhysicsException(Exception):
    pass


def dist(vector_a: List[int], vector_b: List[int]) -> float:
    """
    Calculate the distance between vector_a and vector_b.

    :param vector_a: A "vector" i.e. list of integers
    :param vector_b: A "vector" i.e. list of integers
    :return: The distance betwenn vector_a and vector_b
    """
    if len(vector_a) != len(vector_b):
        raise PhysicsException("Vectors of different lengths: {}, {}".format(vector_a, vector_b))
    parts_sum = 0
    for index, part in enumerate(vector_a):
        parts_sum += (part - vector_b[index])**2
    return math.sqrt(parts_sum)


def line_point(vector_a: List[int], vector_b: List[int], line_length: int):
    """
    Find a point along that goes along vector_a to vector_b that is the given line_length away.

    :param vector_a: The starting vector
    :param vector_b: The other vector to form the line with.
    :param line_length: The length to travel down the line to find the new vector.
    :return: A vector the same shape as a and b.
    """
    if len(vector_a) != len(vector_b):
        raise PhysicsException("Vectors of different lengths: {}, {}".format(vector_a, vector_b))
    line_vector = []
    for index, part in enumerate(vector_a):
        line_vector.append(part - vector_b[index])
    line_vector = [line_length*vector_part for vector_part in line_vector]
    for index, part in enumerate(vector_a):
        line_vector[index] = part + line_vector[index]
    return line_vector


def is_left(vector_a: List[int], vector_b: List[int], vector_to_check: List[int]) -> bool:
    return (
            (vector_b[0] - vector_a[0])*(vector_to_check[1] - vector_a[1]) -
            (vector_b[1] - vector_a[1])*(vector_to_check[0] - vector_a[0])
    ) > 0
