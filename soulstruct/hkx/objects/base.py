from __future__ import annotations

__all__ = ["HKXObject", "HalfFloat", "QuarterFloat", "QsTransform"]

import abc
import typing as tp

from soulstruct.utilities.maths import Vector4, Quaternion

if tp.TYPE_CHECKING:
    from ..nodes import HKXNode


class HKXObject(abc.ABC):

    @abc.abstractmethod
    def __init__(self, node: HKXNode):
        self._node = node
        node.set_py_object(self)

    @property
    def node(self) -> HKXNode:
        return self._node


class HalfFloat(int):
    """Indicates that this integer is holding a `signed short` representation of a half-precision float.

    Used in Havok (`hkHalf16`). Can be unpacked by `numpy`, but not packed again. You are better off experimenting with
    the result of converting bytes to determine the value you want.
    """


class QuarterFloat(int):
    """Indicates that this integer is holding a `signed char` representation of a quarter-precision float.

    There is no common spec for 8-bit floats, but they are used rarely in Havok (`hkUFloat8` class). Not even `numpy`
    can interpret them, so good luck modifying them. (Fortunately, the only value seen so far is 127.)
    """


class QsTransform(HKXObject):
    """hkQsTransform"""

    def __init__(self, node: HKXNode):
        super().__init__(node)
        self.translation = Vector4(node["translation"])
        self.rotation = Quaternion(node["rotation"])
        self.scale = Vector4(node["scale"])
