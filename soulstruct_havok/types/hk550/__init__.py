"""
Types for Havok 5.5.0.

TODO: Only the types for map collisions -- `hkpEntity`, `CustomParamStorageExtendedMeshShape`, and friends -- have been
 manually constructed so far. The rest have been copied from `hk2010` and will probably have numerous errors.
"""
from .core import *
from ._hka import *
from ._hkp import *
from ._hkx import *

from .CustomMeshParameter import CustomMeshParameter
from .CustomParamStorageExtendedMeshShape import CustomParamStorageExtendedMeshShape

from .hkAabb import hkAabb
from .hkLocalFrame import hkLocalFrame
from .hkMoppBvTreeShapeBase import hkMoppBvTreeShapeBase
from .hkMotionState import hkMotionState
from .hkMultiThreadCheck import hkMultiThreadCheck
from .hkRootLevelContainer import hkRootLevelContainer
from .hkRootLevelContainerNamedVariant import hkRootLevelContainerNamedVariant
from .hkSweptTransform import hkSweptTransform
from .hkWorldMemoryAvailableWatchDog import hkWorldMemoryAvailableWatchDog


VERSION = "Havok-5.5.0-r1"
