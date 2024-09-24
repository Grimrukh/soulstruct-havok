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
from dataclasses import dataclass

import numpy as np
from soulstruct.dcx import DCXType

from soulstruct_havok.core import HavokFileFormat
from soulstruct_havok.packfile.structs import PackFileVersion, PackfileHeaderInfo
from soulstruct_havok.types import hk2010, hk2016
from soulstruct_havok.types.hk2016 import *
from soulstruct_havok.utilities.files import HAVOK_PACKAGE_PATH
from soulstruct_havok.utilities.hk_conversion import convert_hk
from soulstruct_havok.utilities.maths import TRSTransform
from soulstruct_havok.wrappers.base import *
from soulstruct_havok.wrappers.hkx2010 import AnimationHKX as AnimationHKX2010

_LOGGER = logging.getLogger("soulstruct_havok")

AnimationContainerType = AnimationContainer[
    hkaAnimationContainer, hkaAnimation, hkaAnimationBinding,
    hkaInterleavedUncompressedAnimation, hkaSplineCompressedAnimation, hkaDefaultAnimatedReferenceFrame,
]
SkeletonType = Skeleton[hkaSkeleton, hkaBone]
SkeletonMapperType = SkeletonMapper[hkaSkeletonMapper]
PhysicsDataType = PhysicsData[hkpPhysicsData, hkpPhysicsSystem]


@dataclass(slots=True, repr=False)
class AnimationHKX(BaseAnimationHKX):
    TYPES_MODULE: tp.ClassVar = hk2016
    root: hkRootLevelContainer = None
    animation_container: AnimationContainerType = None

    def get_spline_hkx(self) -> AnimationHKX:
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
            ret_code = sp.call(
                [compress_anim_path, str(temp_interleaved_path), str(temp_spline_path), "1", "0.001"]
            )
            _LOGGER.debug(f"Done. Return code: {ret_code}")
            if ret_code != 0:
                raise RuntimeError(f"`CompressAnim.exe` had return code {ret_code}.")
            _LOGGER.debug("Reading 2010 spline-compressed animation...")
            hkx2010_spline = AnimationHKX2010.from_path(temp_spline_path)
        finally:
            temp_interleaved_path.unlink(missing_ok=True)
            temp_spline_path.unlink(missing_ok=True)

        _LOGGER.debug("Upgrading to 2015...")
        anim_2015 = self.__class__.from_2010_hkx(hkx2010_spline, dcx_type=dcx_type)

        # Clean-up: restore hash overrides, change binding to refer to same animation, and change animation type.
        anim_2015.hsh_overrides = self.hsh_overrides.copy()
        for i, anim in enumerate(anim_2015.animation_container.animation_container.animations):
            anim_2015.animation_container.animation_container.bindings[i].animation = anim
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
                padding_option=0,
                contents_version_string=b"hk_2010.2.0-r1",
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
        root2015 = convert_hk(hkx2010.root, hk2016.hkRootLevelContainer, hk2016, source_handler, dest_handler)
        print(f"2010 to 2015 time: {time.perf_counter() - t}")
        return cls(
            dcx_type=dcx_type,
            root=root2015,
            hk_format=HavokFileFormat.Tagfile,
            hk_version="2015",
        )

    @classmethod
    def from_dsr_interleaved_template(
        cls,
        skeleton_hkx: SkeletonHKX,
        interleaved_data: list[list[TRSTransform]],
        transform_track_to_bone_indices: list[int] = None,
        root_motion: np.ndarray | None = None,
        is_armature_space=False,
    ) -> AnimationHKX:
        """Open bundled template HKX for Dark Souls Remastered (c2240, Capra Demon, animation 200).

        Arguments reflect the minimal data required to create a new animation from the template.
        """
        template_path = HAVOK_PACKAGE_PATH("resources/AnimationTemplate2015.hkx")
        hkx = cls.from_path(template_path)
        container = hkx.animation_container

        container.spline_to_interleaved()

        container.animation.duration = (len(interleaved_data) - 1) / 30.0  # TODO: assumes 30 FPS (always valid?)

        container.animation_binding.originalSkeletonName = skeleton_hkx.skeleton.skeleton.name
        if transform_track_to_bone_indices is None:
            # Default: same as bone order.
            transform_track_to_bone_indices = list(range(len(skeleton_hkx.skeleton.bones)))
        container.animation_binding.transformTrackToBoneIndices = transform_track_to_bone_indices
        container.animation.numberOfTransformTracks = len(transform_track_to_bone_indices)
        container.animation.annotationTracks = [
            hkaAnnotationTrack(
                trackName=skeleton_hkx.skeleton.bones[bone_index].name,
                annotations=[],
            )
            for bone_index in transform_track_to_bone_indices
        ]

        if is_armature_space:
            # NOTE: Must be called AFTER setting new transform track -> bone mapping above.
            container.set_interleaved_data_from_armature_space(skeleton_hkx.skeleton, interleaved_data)
        else:
            container.interleaved_data = interleaved_data
        container.save_interleaved_data()
        container.animation.floats = []

        if root_motion is None:
            hkx.animation_container.animation.extractedMotion = None
        else:  # template has some reference frame samples already
            hkx.animation_container.set_reference_frame_samples(root_motion)

        return hkx.get_spline_hkx()


@dataclass(slots=True)
class SkeletonHKX(BaseSkeletonHKX):
    TYPES_MODULE: tp.ClassVar = hk2016
    root: hkRootLevelContainer = None
    skeleton: SkeletonType = None


@dataclass(slots=True)
class CollisionHKX(BaseCollisionHKX):
    TYPES_MODULE: tp.ClassVar = hk2016
    root: hkRootLevelContainer = None
    physics_data: PhysicsDataType = None


@dataclass(slots=True)
class ClothHKX(BaseClothHKX):
    TYPES_MODULE: tp.ClassVar = hk2016
    root: hkRootLevelContainer = None
    cloth_physics_data: ClothPhysicsData[hkpPhysicsData, hkpPhysicsSystem] = None


@dataclass(slots=True)
class RagdollHKX(BaseRagdollHKX):
    TYPES_MODULE: tp.ClassVar = hk2016
    root: hkRootLevelContainer = None
    standard_skeleton: SkeletonType = None
    ragdoll_skeleton: SkeletonType = None
    physics_data: PhysicsDataType = None
    animation_to_ragdoll_skeleton_mapper: SkeletonMapperType = None
    ragdoll_to_animation_skeleton_mapper: SkeletonMapperType = None


@dataclass(slots=True)
class RemoAnimationHKX(BaseRemoAnimationHKX):
    TYPES_MODULE: tp.ClassVar = hk2016
    root: hkRootLevelContainer = None
    animation_container: AnimationContainerType = None
    skeleton: SkeletonType = None