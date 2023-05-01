__all__ = ["invert_matrix3", "invert_matrix4"]

from scipy.linalg import inv

from soulstruct.utilities.maths import Matrix3, Matrix4


def invert_matrix3(matrix: Matrix3) -> Matrix3:
    return Matrix3(inv(matrix.data))


def invert_matrix4(matrix: Matrix4) -> Matrix4:
    return Matrix4(inv(matrix.data))