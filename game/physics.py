import math


class PhysicsException(Exception):
    pass


def dist(vector_a, vector_b):
    if len(vector_a) != len(vector_b):
        raise PhysicsException("Vectors of different lengths: {}, {}".format(vector_a, vector_b))
    parts_sum = 0
    for index, part in enumerate(vector_a):
        parts_sum += (part - vector_b[index])**2
    return math.sqrt(parts_sum)
