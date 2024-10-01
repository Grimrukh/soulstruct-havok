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

from soulstruct.dcx import DCXType

from soulstruct_havok.core import HavokFileFormat
from soulstruct_havok.packfile.structs import PackFileVersion, PackfileHeaderInfo
from soulstruct_havok.types import hk2010, hk2015
from soulstruct_havok.types.hk2015 import *
from soulstruct_havok.utilities.files import HAVOK_PACKAGE_PATH
from soulstruct_havok.utilities.hk_conversion import convert_hk
from soulstruct_havok.fromsoft.base import *
from soulstruct_havok.fromsoft.darksouls1ptde import AnimationHKX as AnimationHKX_PTDE

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
    TYPES_MODULE: tp.ClassVar = hk2015
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
            hkx2010_spline = AnimationHKX_PTDE.from_path(temp_spline_path)
        finally:
            temp_spline_path.unlink(missing_ok=True)

        _LOGGER.debug("Upgrading to 2015...")
        anim_2015 = self.__class__.from_2010_hkx(hkx2010_spline, dcx_type=dcx_type)

        # Clean-up: restore hash overrides, change binding to refer to same animation, and change animation type.
        anim_2015.hsh_overrides = self.hsh_overrides.copy()
        for i, anim in enumerate(anim_2015.animation_container.animation_container.animations):
            anim_2015.animation_container.animation_container.bindings[i].animation = anim
            anim.type = 3  # spline-compressed in Havok 2015 (was 5 in Havok 2010)

        _LOGGER.info("Successfully converted interleaved animation to hk2015 spline animation.")
        return anim_2015

    def to_2010_hkx(self) -> AnimationHKX_PTDE:
        """Construct a 2010 Havok file (with packfile type) from this 2015 tagfile.

        This is done using Capra Demon's animation 3000 from PTDE as a base, and injecting this file's data into it.

        (I am adding these specific conversion functions as needed for Nightfall.)
        """
        if self.animation_container.is_spline:
            self.animation_container.save_spline_data()
        elif self.animation_container.is_interleaved:
            self.animation_container.save_interleaved_data()

        def source_error_handler(source_obj: hk, name: str, __, ___):
            if isinstance(source_obj, hk2015.hkaAnimatedReferenceFrame) and name == "frameType":
                return []  # not serializable anyway
            if isinstance(source_obj, hk2015.hkaAnimationBinding) and name == "partitionIndices":
                return []

        import time
        t = time.perf_counter()
        root2010 = convert_hk(self.root, hk2010.hkRootLevelContainer, hk2010, source_error_handler)
        _LOGGER.info(f"Converted 2015 Animation HKX to 2010 in {time.perf_counter() - t} s.")
        return AnimationHKX_PTDE(
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
    def from_2010_hkx(cls, hkx2010: AnimationHKX_PTDE, dcx_type: DCXType = None) -> AnimationHKX:
        """Construct a 2015 Havok animation tagfile from a 2010 Havok animation packfile.

        `dcx_type` defaults to be the same as `hkx2010`. It does NOT default to the standard DSR DCX type, because most
        HKX files appear inside compressed binders and are NOT compressed themselves.
        """

        def dest_handler(dest_type: type[hk], dest_kwargs: dict[str, tp.Any], name: str):
            if dest_type is hk2015.hkaAnimatedReferenceFrame and name == "frameType":
                dest_kwargs["frameType"] = 0  # not serializable anyway
                return True
            if dest_type is hk2015.hkaAnimationBinding and name == "partitionIndices":
                dest_kwargs["partitionIndices"] = []
                return True
            return False

        if dcx_type is None:
            dcx_type = hkx2010.dcx_type

        import time
        t = time.perf_counter()
        root2015 = convert_hk(hkx2010.root, hk2015.hkRootLevelContainer, hk2015, None, dest_handler)
        _LOGGER.info(f"Converted hk2010 animation to hk2015 animation in {time.perf_counter() - t:.3f} s.")
        return cls(
            dcx_type=dcx_type,
            root=root2015,
            hk_format=HavokFileFormat.Tagfile,
            hk_version="20150100",
        )


@dataclass(slots=True)
class SkeletonHKX(BaseSkeletonHKX):
    TYPES_MODULE: tp.ClassVar = hk2015
    root: hkRootLevelContainer = None
    skeleton: SkeletonType = None


@dataclass(slots=True)
class CollisionHKX(BaseCollisionHKX):
    TYPES_MODULE: tp.ClassVar = hk2015
    root: hkRootLevelContainer = None
    physics_data: PhysicsDataType = None


@dataclass(slots=True)
class ClothHKX(BaseClothHKX):
    TYPES_MODULE: tp.ClassVar = hk2015
    root: hkRootLevelContainer = None
    cloth_physics_data: ClothPhysicsData[hkpPhysicsData, hkpPhysicsSystem] = None


@dataclass(slots=True)
class RagdollHKX(BaseRagdollHKX):
    TYPES_MODULE: tp.ClassVar = hk2015
    root: hkRootLevelContainer = None
    animation_skeleton: SkeletonType = None
    ragdoll_skeleton: SkeletonType = None
    physics_data: PhysicsDataType = None
    animation_to_ragdoll_skeleton_mapper: SkeletonMapperType = None
    ragdoll_to_animation_skeleton_mapper: SkeletonMapperType = None

    def inject_animation_skeleton(
        self,
        animation_skeleton_hkx: SkeletonHKX,
        bone_redirect_func: tp.Callable[[str], str] = None,
    ):
        """Replace first skeleton in ragdoll HKX with skeleton in given `skeleton_hkx` (e.g. from ANIBND) and attempt
        to remap bones by name.

        If `bone_redirect_func` is given, it will be used to convert old bone names to new bone names when repairing the
        bone references in both skeleton mappers. Otherwise, the same bone names must appear.
        """
        anim_skeleton = animation_skeleton_hkx.skeleton  # wrapper

        a_to_r = self.animation_to_ragdoll_skeleton_mapper.skeleton_mapper.mapping
        old_animation_skeleton = a_to_r.skeletonA
        a_to_r.skeletonA = anim_skeleton.skeleton  # `hkaSkeleton` instance
        for simple_mapping in a_to_r.simpleMappings:
            bone_a_index = simple_mapping.boneA
            bone_a_name = old_animation_skeleton.bones[bone_a_index].name
            new_bone_a_name = bone_redirect_func(bone_a_name) if bone_redirect_func else bone_a_name
            try:
                simple_mapping.boneA = anim_skeleton.bones_by_name[new_bone_a_name].index
            except KeyError:
                raise ValueError(f"Simple map bone '{bone_a_name}' not found in new animation skeleton.")
        for chain_mapping in a_to_r.chainMappings:
            start_bone_a_index = chain_mapping.startBoneA
            start_bone_a_name = old_animation_skeleton.bones[start_bone_a_index].name
            new_start_bone_a_name = bone_redirect_func(start_bone_a_name) if bone_redirect_func else start_bone_a_name
            try:
                chain_mapping.startBoneA = anim_skeleton.bones_by_name[new_start_bone_a_name].index
            except KeyError:
                raise ValueError(f"Chain map start bone '{start_bone_a_name}' not found in new animation skeleton.")

            end_bone_a_index = chain_mapping.endBoneA
            end_bone_a_name = old_animation_skeleton.bones[end_bone_a_index].name
            new_end_bone_a_name = bone_redirect_func(end_bone_a_name) if bone_redirect_func else end_bone_a_name
            try:
                chain_mapping.endBoneA = anim_skeleton.bones_by_name[new_end_bone_a_name].index
            except KeyError:
                raise ValueError(f"Chain map end bone '{end_bone_a_name}' not found in new animation skeleton.")

        r_to_a = self.ragdoll_to_animation_skeleton_mapper.skeleton_mapper.mapping
        old_animation_skeleton = r_to_a.skeletonB
        r_to_a.skeletonB = anim_skeleton.skeleton  # `hkaSkeleton` instance
        for simple_mapping in r_to_a.simpleMappings:
            bone_b_index = simple_mapping.boneB
            bone_b_name = old_animation_skeleton.bones[bone_b_index].name
            new_bone_b_name = bone_redirect_func(bone_b_name) if bone_redirect_func else bone_b_name
            try:
                simple_mapping.boneB = anim_skeleton.bones_by_name[new_bone_b_name].index
            except KeyError:
                raise ValueError(f"Simple map bone '{bone_b_name}' not found in new animation skeleton.")
        for chain_mapping in r_to_a.chainMappings:
            start_bone_b_index = chain_mapping.startBoneB
            start_bone_b_name = old_animation_skeleton.bones[start_bone_b_index].name
            new_start_bone_b_name = bone_redirect_func(start_bone_b_name) if bone_redirect_func else start_bone_b_name
            try:
                chain_mapping.startBoneB = anim_skeleton.bones_by_name[new_start_bone_b_name].index
            except KeyError:
                raise ValueError(f"Chain map start bone '{start_bone_b_name}' not found in new animation skeleton.")

            end_bone_b_index = chain_mapping.endBoneB
            end_bone_b_name = old_animation_skeleton.bones[end_bone_b_index].name
            new_end_bone_b_name = bone_redirect_func(end_bone_b_name) if bone_redirect_func else end_bone_b_name
            try:
                chain_mapping.endBoneB = anim_skeleton.bones_by_name[new_end_bone_b_name].index
            except KeyError:
                raise ValueError(f"Chain map end bone '{end_bone_b_name}' not found in new animation skeleton.")

        # Replace animation skeleton wrapper.
        self.animation_skeleton = Skeleton(self.TYPES_MODULE, anim_skeleton.skeleton)
        # Note that we do NOT need to change the ragdoll skeleton in `hkaRagdollInstance` (variant 2).


@dataclass(slots=True)
class RemoAnimationHKX(BaseRemoAnimationHKX):
    TYPES_MODULE: tp.ClassVar = hk2015
    root: hkRootLevelContainer = None
    animation_container: AnimationContainerType = None
    skeleton: SkeletonType = None
