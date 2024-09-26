"""
Types for Havok 5.5.0.

TODO: Only the types for map collisions -- `hkpEntity`, `CustomParamStorageExtendedMeshShape`, and friends -- have been
 manually constructed so far. The rest have been copied from `hk2010` and will probably have numerous errors.
"""
from .core import *

from .hka import *
from .hkp import *
from .hkx import *

from .CustomMeshParameter import CustomMeshParameter
from .CustomParamStorageExtendedMeshShape import CustomParamStorageExtendedMeshShape

from soulstruct_havok.types.hk550.hkAabb import hkAabb
from soulstruct_havok.types.hk550.hkLocalFrame import hkLocalFrame
from soulstruct_havok.types.hk550.hkMoppBvTreeShapeBase import hkMoppBvTreeShapeBase
from soulstruct_havok.types.hk550.hkMotionState import hkMotionState
from soulstruct_havok.types.hk550.hkMultiThreadCheck import hkMultiThreadCheck
from soulstruct_havok.types.hk550.hkRootLevelContainer import hkRootLevelContainer
from soulstruct_havok.types.hk550.hkRootLevelContainerNamedVariant import hkRootLevelContainerNamedVariant
from soulstruct_havok.types.hk550.hkSweptTransform import hkSweptTransform
from soulstruct_havok.types.hk550.hkWorldMemoryAvailableWatchDog import hkWorldMemoryAvailableWatchDog


VERSION = "Havok-5.5.0-r1"
