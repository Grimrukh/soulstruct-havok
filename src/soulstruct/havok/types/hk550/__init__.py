"""
Types for Havok 5.5.0.

TODO: Only the types for animations and map collisions -- `hkpEntity`, `CustomParamStorageExtendedMeshShape`, and
friends -- have been manually constructed so far. The rest have been copied from `hk2010` and will probably have
numerous errors.

TODO: Since Demon's Souls is currently the only user of this SDK, the baked-in member offsets of derived classes always
 assume that `reuse_padding_optimization == 1` in the packfile header. This means that a subclass that inherits from
 a `hk` class with `hkVector4` (size 16) and `int` (size 4) members, for example, will have its first member at offset
 20, not 32 (assuming its own member type alignment is 4), as the subclass members ARE permitted to "reuse" the
 automatic alignment padding of the base class. But even if it has just one `int` member, the subclass total size will
 be 32 due to the alignment rules of the base class.
    - All that said, if this were the case, I thought I would've run into errors when reading these files after
    exporting them for PC (still 5.5.0) with the actual Havok SDK. But I haven't. It's possible that the files I've
    looked at so far happen to not have any classes affected by this setting (not many subclasses used, etc.).
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
