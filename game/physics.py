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


def line(vector_a, vector_b, line_length):
    if len(vector_a) != len(vector_b):
        raise PhysicsException("Vectors of different lengths: {}, {}".format(vector_a, vector_b))
    line_vector = []
    for index, part in enumerate(vector_a):
        line_vector.append(part - vector_b[index])
    line_vector = [line_length*vector_part for vector_part in line_vector]
    for index, part in enumerate(vector_a):
        line_vector[index] = part + line_vector[index]
    return [vector_a, line_vector]
