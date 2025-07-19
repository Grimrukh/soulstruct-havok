__all__ = [
    "invert_matrix3",
    "invert_matrix4",
    "float32",
    "next_power_of_two",
]

import numpy as np
from scipy.linalg import inv

from soulstruct.utilities.maths import Matrix3, Matrix4


def invert_matrix3(matrix: Matrix3) -> Matrix3:
    return Matrix3(inv(matrix.data))


def invert_matrix4(matrix: Matrix4) -> Matrix4:
    return Matrix4(inv(matrix.data))


def float32(double: float) -> float:
    return float(np.float32(double))


def next_power_of_two(n: int) -> int:
    """Efficient algorithm for returning the closest power of two above `n`."""
    if n == 1:
        return 2
    n -= 1
    n |= n >> 1
    n |= n >> 2
    n |= n >> 4
    n |= n >> 8
    n |= n >> 16
    n += 1
    return n
