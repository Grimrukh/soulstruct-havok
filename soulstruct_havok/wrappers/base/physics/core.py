"""Base classes for various common Havok file types, with wrappers and variant indices for their basic contents.

Must be overridden by each Havok version to provide the correct `hk` types module.
"""
from __future__ import annotations

__all__ = ["BaseCollisionHKX", "BaseClothHKX"]

import abc
from dataclasses import dataclass

from ..core import BaseWrappedHKX
from ..type_vars import *
from .physics_data import PhysicsData
from .cloth_physics_data import ClothPhysicsData


@dataclass(slots=True)
class BaseCollisionHKX(BaseWrappedHKX, abc.ABC):
    """Loads HKX objects that just have collision physics, such as those in `.objbnd` Binders or map collisions."""

    physics_data: PhysicsData = None

    def __post_init__(self):
        super(BaseWrappedHKX, self).__post_init__()
        self.physics_data = PhysicsData(self.TYPES_MODULE, self.get_variant(0, *PHYSICS_DATA_T.__constraints__))


@dataclass(slots=True)
class BaseClothHKX(BaseWrappedHKX, abc.ABC):
    """Loads HKX objects that are found in a "Cloth" HKX file (inside `chrbnd` binder, e.g. `c2410_c.hkx`).

    This file is not used for every character - only those with cloth physics (e.g. capes).
    """

    cloth_physics_data: ClothPhysicsData = None

    def __post_init__(self):
        super(BaseWrappedHKX, self).__post_init__()
        self.cloth_physics_data = ClothPhysicsData(
            self.TYPES_MODULE, self.get_variant(0, *PHYSICS_DATA_T.__constraints__)
        )
