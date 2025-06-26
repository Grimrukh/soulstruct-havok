from __future__ import annotations

__all__ = ["AnimationHKX", "SkeletonHKX", "ClothHKX", "RagdollHKX"]

import logging
import subprocess as sp
import typing as tp

from soulstruct.havok.enums import HavokModule
from soulstruct.havok.packfile.structs import PackfileHeaderInfo, PackFileVersion
from soulstruct.havok.types.hk2010 import *
from soulstruct.havok.fromsoft.base import *
from soulstruct.havok.utilities.files import HAVOK_PACKAGE_PATH

AnimationContainerType = AnimationContainer[
    hkaAnimationContainer, hkaAnimation, hkaAnimationBinding,
    hkaInterleavedUncompressedAnimation, hkaSplineCompressedAnimation, hkaDefaultAnimatedReferenceFrame,
]
SkeletonType = Skeleton[hkaSkeleton, hkaBone]
SkeletonMapperType = SkeletonMapper[hkaSkeletonMapper]
PhysicsDataType = PhysicsData[hkpPhysicsData, hkpPhysicsSystem]

_LOGGER = logging.getLogger(__name__)


class AnimationHKX(BaseAnimationHKX):
    HAVOK_MODULE: tp.ClassVar[HavokModule] = HavokModule.hk2010
    root: hkRootLevelContainer = None
    animation_container: AnimationContainerType = None

    @classmethod
    def get_default_hkx_kwargs(cls) -> dict[str, tp.Any]:
        kwargs = super(AnimationHKX, cls).get_default_hkx_kwargs()
        kwargs |= dict(
            packfile_header_info=PackfileHeaderInfo(
                header_version=PackFileVersion.Version0x08,
                pointer_size=4,
                is_little_endian=True,
                reuse_padding_optimization=0,
                contents_version_string=VERSION,
                flags=0,
                header_extension=None,
            )
        )
        return kwargs

    def to_spline_hkx(self) -> AnimationHKX:
        """Uses Horkrux's compiled converter to convert interleaved HKX to spline HKX.

        Returns an entire new instance of this class.
        """
        if not self.animation_container.is_interleaved:
            raise TypeError("Can only convert interleaved animations to spline animations.")

        temp_interleaved_path = HAVOK_PACKAGE_PATH("__temp_interleaved__.hkx")
        temp_spline_path = HAVOK_PACKAGE_PATH("__temp_spline__.hkx")

        dcx_type = self.dcx_type
        hkx2010 = self  # already 2010
        try:
            _LOGGER.debug("Writing 2010 file...")
            hkx2010.write(temp_interleaved_path)
            _LOGGER.debug("Calling `CompressAnim`...")
            compress_anim_path = str(HAVOK_PACKAGE_PATH("resources/CompressAnim.exe"))
            try:
                sp.check_output(
                    [compress_anim_path, str(temp_interleaved_path), str(temp_spline_path), "1", "0.001"],
                    stderr=sp.STDOUT,
                )
            except sp.CalledProcessError as ex:
                _LOGGER.error(
                    f"Spline animation compression failed. Error in `CompressAnim.exe`: {ex.output.decode()}\n"
                    f"Left temp interleaved HKX file for inspection: {temp_interleaved_path}"
                )
                raise RuntimeError from ex
            temp_interleaved_path.unlink(missing_ok=True)
            _LOGGER.debug("Reading 2010 spline-compressed animation...")
            spline_2010 = self.__class__.from_path(temp_spline_path)
            spline_2010.dcx_type = dcx_type
        finally:
            temp_spline_path.unlink(missing_ok=True)

        _LOGGER.info("Successfully converted interleaved animation to hk2010 spline animation.")
        return spline_2010


class SkeletonHKX(BaseSkeletonHKX):
    HAVOK_MODULE: tp.ClassVar[HavokModule] = HavokModule.hk2010
    root: hkRootLevelContainer = None
    skeleton: SkeletonType = None


class CollisionHKX(BaseCollisionHKX):
    HAVOK_MODULE: tp.ClassVar[HavokModule] = HavokModule.hk2010
    root: hkRootLevelContainer = None
    physics_data: PhysicsDataType = None


class ClothHKX(BaseClothHKX):
    HAVOK_MODULE: tp.ClassVar[HavokModule] = HavokModule.hk2010
    root: hkRootLevelContainer = None
    cloth_physics_data: ClothPhysicsData[hkpPhysicsData, hkpPhysicsSystem] = None


class RagdollHKX(BaseRagdollHKX):
    HAVOK_MODULE: tp.ClassVar[HavokModule] = HavokModule.hk2010
    root: hkRootLevelContainer = None
    animation_skeleton: SkeletonType = None
    ragdoll_skeleton: SkeletonType = None
    physics_data: PhysicsDataType = None
    animation_to_ragdoll_skeleton_mapper: SkeletonMapperType = None
    ragdoll_to_animation_skeleton_mapper: SkeletonMapperType = None
