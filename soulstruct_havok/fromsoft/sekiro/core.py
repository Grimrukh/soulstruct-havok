from __future__ import annotations

__all__ = [
    "AnimationHKX",
    "SkeletonHKX",
    "CollisionHKX",
    "ClothHKX",
    "RagdollHKX",
    "RemoAnimationHKX",
    "AnimationContainerType",
    "SkeletonType",
    "SkeletonMapperType",
    "PhysicsDataType",
]

import logging
import subprocess as sp
import typing as tp

from soulstruct.dcx import DCXType

from soulstruct_havok.core import HavokFileFormat
from soulstruct_havok.enums import HavokModule
from soulstruct_havok.packfile.structs import PackFileVersion, PackfileHeaderInfo
from soulstruct_havok.types import hk2010, hk2016
from soulstruct_havok.types.hk2016 import *
from soulstruct_havok.utilities.files import HAVOK_PACKAGE_PATH
from soulstruct_havok.utilities.hk_conversion import convert_hk
from soulstruct_havok.fromsoft.base import *
from soulstruct_havok.fromsoft.darksouls1ptde import AnimationHKX as AnimationHKX2010

_LOGGER = logging.getLogger("soulstruct_havok")

AnimationContainerType = AnimationContainer[
    hkaAnimationContainer, hkaAnimation, hkaAnimationBinding,
    hkaInterleavedUncompressedAnimation, hkaSplineCompressedAnimation, hkaDefaultAnimatedReferenceFrame,
]
SkeletonType = Skeleton[hkaSkeleton, hkaBone]
SkeletonMapperType = SkeletonMapper[hkaSkeletonMapper]
PhysicsDataType = PhysicsData[hkpPhysicsData, hkpPhysicsSystem]


class AnimationHKX(BaseAnimationHKX):
    HAVOK_MODULE: tp.ClassVar[HavokModule] = HavokModule.hk2016
    root: hkRootLevelContainer = None
    animation_container: AnimationContainerType = None

    def to_spline_hkx(self) -> AnimationHKX:
        """Uses Horkrux's compiled converter to convert interleaved HKX to spline HKX.

        Returns an entire new instance of this class.
        """
        if not self.animation_container.is_interleaved:
            raise TypeError("Can only convert interleaved animations to spline animations.")

        temp_interleaved_path = HAVOK_PACKAGE_PATH("__temp_interleaved__.hkx")
        temp_spline_path = HAVOK_PACKAGE_PATH("__temp_spline__.hkx")

        dcx_type = self.dcx_type
        _LOGGER.debug("Downgrading to 2010...")
        hkx2010 = self.to_2010_hkx()
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
            hkx2010_spline = AnimationHKX2010.from_path(temp_spline_path)
        finally:
            temp_spline_path.unlink(missing_ok=True)

        _LOGGER.debug("Upgrading to 2015...")
        anim_2015 = self.__class__.from_2010_hkx(hkx2010_spline, dcx_type=dcx_type)

        # Clean-up: restore hash overrides, change binding to refer to same animation, and change animation type.
        anim_2015.hsh_overrides = self.hsh_overrides.copy()
        for i, anim in enumerate(anim_2015.animation_container.hkx_container.animations):
            anim_2015.animation_container.hkx_container.bindings[i].animation = anim
            anim.type = 3  # spline-compressed in Havok 2015 (was 5 in Havok 2010)

        _LOGGER.info("Successfully converted interleaved animation to hk2016 spline animation.")
        return anim_2015

    def to_2010_hkx(self) -> AnimationHKX2010:
        """Construct a 2010 Havok file (with packfile type) from this 2015 tagfile.

        This is done using Capra Demon's animation 3000 from PTDE as a base, and injecting this file's data into it.

        (I am adding these specific conversion functions as needed for Nightfall.)
        """
        if self.animation_container.is_spline:
            self.animation_container.save_spline_data()
        elif self.animation_container.is_interleaved:
            self.animation_container.save_interleaved_data()

        def source_error_handler(_, name: str, value, dest_kwargs: dict[str, tp.Any]):
            if name == "refCount":
                dest_kwargs["referenceCount"] = value
                return ["referenceCount"]
            if name in ("partitionIndices", "frameType"):  # absent from 2010
                return []

        import time
        t = time.perf_counter()
        root2010 = convert_hk(self.root, hk2010.hkRootLevelContainer, hk2010, source_error_handler)
        _LOGGER.info(f"Converted 2015 Animation HKX to 2010 in {time.perf_counter() - t} s.")
        return AnimationHKX2010(
            dcx_type=DCXType.Null,
            root=root2010,
            hk_format=HavokFileFormat.Packfile,
            hk_version="2010",
            packfile_header_info=PackfileHeaderInfo(
                header_version=PackFileVersion.Version0x08,
                pointer_size=4,
                is_little_endian=True,
                reuse_padding_optimization=0,
                contents_version_string=VERSION,
                flags=0,
                header_extension=None,
            ),
        )

    @classmethod
    def from_2010_hkx(cls, hkx2010: AnimationHKX2010, dcx_type: DCXType = None) -> AnimationHKX:
        """Construct a 2015 Havok animation tagfile from a 2010 Havok animation packfile.

        `dcx_type` defaults to be the same as `hkx2010`. It does NOT default to the standard DSR DCX type, because most
        HKX files appear inside compressed binders and are NOT compressed themselves.
        """

        def source_handler(_, name: str, value, dest_kwargs: dict[str, tp.Any]):
            if name == "referenceCount":
                dest_kwargs["refCount"] = value
                return ["refCount"]

        def dest_handler(dest_type: type[hk], dest_kwargs: dict[str, tp.Any], name: str):
            if dest_type is hk2016.hkaAnimationBinding and name == "partitionIndices":
                dest_kwargs["partitionIndices"] = []
                return True
            return False

        if dcx_type is None:
            dcx_type = hkx2010.dcx_type

        import time
        t = time.perf_counter()
        root2016 = convert_hk(hkx2010.root, hk2016.hkRootLevelContainer, hk2016, source_handler, dest_handler)
        _LOGGER.info(f"Converted hk2010 animation to hk2016 animation in {time.perf_counter() - t:.3f} s.")
        return cls(
            dcx_type=dcx_type,
            root=root2016,
            hk_format=HavokFileFormat.Tagfile,
            hk_version="20160200",
        )


class SkeletonHKX(BaseSkeletonHKX):
    HAVOK_MODULE: tp.ClassVar[HavokModule] = HavokModule.hk2016
    root: hkRootLevelContainer = None
    skeleton: SkeletonType = None


class CollisionHKX(BaseCollisionHKX):
    HAVOK_MODULE: tp.ClassVar[HavokModule] = HavokModule.hk2016
    root: hkRootLevelContainer = None
    physics_data: PhysicsDataType = None


class ClothHKX(BaseClothHKX):
    HAVOK_MODULE: tp.ClassVar[HavokModule] = HavokModule.hk2016
    root: hkRootLevelContainer = None
    cloth_physics_data: ClothPhysicsData[hkpPhysicsData, hkpPhysicsSystem] = None


class RagdollHKX(BaseRagdollHKX):
    HAVOK_MODULE: tp.ClassVar[HavokModule] = HavokModule.hk2016
    root: hkRootLevelContainer = None
    standard_skeleton: SkeletonType = None
    ragdoll_skeleton: SkeletonType = None
    physics_data: PhysicsDataType = None
    animation_to_ragdoll_skeleton_mapper: SkeletonMapperType = None
    ragdoll_to_animation_skeleton_mapper: SkeletonMapperType = None


class RemoAnimationHKX(BaseRemoAnimationHKX):
    HAVOK_MODULE: tp.ClassVar[HavokModule] = HavokModule.hk2016
    root: hkRootLevelContainer = None
    animation_container: AnimationContainerType = None
    skeleton: SkeletonType = None
