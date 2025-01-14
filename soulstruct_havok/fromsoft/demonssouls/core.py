from __future__ import annotations

__all__ = ["AnimationHKX", "SkeletonHKX", "ClothHKX", "RagdollHKX"]

import copy
import logging
import subprocess as sp
import typing as tp
from pathlib import Path

import numpy as np
from soulstruct_havok.enums import PyHavokModule
from soulstruct_havok.fromsoft.base import *
from soulstruct_havok.packfile.structs import PackfileHeaderInfo, PackFileVersion
from soulstruct_havok.types.hk550 import *
from soulstruct_havok.utilities.files import HAVOK_PACKAGE_PATH
from soulstruct_havok.utilities.maths import TRSTransform

AnimationContainerType = AnimationContainer[
    hkaAnimationContainer, hkaSkeletalAnimation, hkaAnimationBinding,
    hkaInterleavedSkeletalAnimation, hkaSplineSkeletalAnimation, hkaDefaultAnimatedReferenceFrame,
]
SkeletonType = Skeleton[hkaSkeleton, hkaBone]
SkeletonMapperType = SkeletonMapper[hkaSkeletonMapper]
PhysicsDataType = PhysicsData[hkpPhysicsData, hkpPhysicsSystem]

_LOGGER = logging.getLogger("soulstruct_havok")


def call_havok_wavelet_anim(input_path: Path | str, output_path: Path | str, to_wavelet: bool):
    exe_path = HAVOK_PACKAGE_PATH("resources/HavokWaveletAnim.exe")
    args = [str(exe_path), str(input_path), str(output_path), "-towavelet" if to_wavelet else "-fromwavelet"]
    try:
        sp.check_output(args, stderr=sp.STDOUT)
    except sp.CalledProcessError as ex:
        _LOGGER.error(
            f"Wavelet animation conversion failed. Error in `HavokWaveletAnim.exe`: {ex.output.decode()}\n"
            f"Left input HKX file for inspection: {input_path}"
        )
        raise RuntimeError from ex
    # `output_path` should exist for reading by caller at this point.


class AnimationHKX(BaseAnimationHKX):
    """NOTE: Demon's Souls animations are wavelet-compressed, which is an annoying old format to deal with."""

    HAVOK_MODULE: tp.ClassVar[PyHavokModule] = PyHavokModule.hk550
    root: hkRootLevelContainer = None
    animation_container: AnimationContainerType = None

    @classmethod
    def get_default_hkx_kwargs(cls) -> dict[str, tp.Any]:
        kwargs = super(AnimationHKX, cls).get_default_hkx_kwargs()
        kwargs |= dict(
            packfile_header_info=PackfileHeaderInfo(
                header_version=PackFileVersion.Version0x05,
                pointer_size=4,
                is_little_endian=False,
                reuse_padding_optimization=1,
                contents_version_string=VERSION,
                flags=-1,
                header_extension=None,
            )
        )
        return kwargs

    def to_interleaved_hkx(self) -> tp.Self:
        """Uses `HavokWaveletAnim` to convert wavelet-compressed to interleaved animation.

        Cannot be done at the `AnimationContainer` level because we need to read/write whole valid HKX files during the
        conversion process.

        Steps:
            - Write this wavelet-compressed HKX as a temp file, with `is_big_endian=False`.
            - Call `HavokWaveletAnim` to convert it to interleaved format.
            - Read the new interleaved HKX file.
            - Restore old `is_big_endian` and set `reuse_padding_optimization = 1`.

        TODO: Currently assuming that `reuse_padding_optimization` doesn't actually change how these files are read.
         I haven't noticed any read/write errors; it's possible that it happens to not matter for these `hka` classes.
        """
        if self.animation_container.is_spline:
            # Base method can handle splines (but Havok 550 doesn't have spline animations).
            return super().to_interleaved_hkx()

        if not self.animation_container.is_wavelet:
            raise ValueError(
                "Can only convert spline-compressed or wavelet-compressed animations to interleaved animations."
            )

        temp_wavelet_path = HAVOK_PACKAGE_PATH("__temp_wavelet__.hkx")
        temp_interleaved_path = HAVOK_PACKAGE_PATH("__temp_interleaved__.hkx")

        # C++ converter requires LE, but we save the current value to restore it later to the interleaved HKX.
        old_is_big_endian = self.is_big_endian

        # 1. Write little-endian wavelet-compressed file.
        le_wavelet_hkx = copy.deepcopy(self)
        le_wavelet_hkx.is_big_endian = False
        le_wavelet_hkx.write(temp_wavelet_path)
        _LOGGER.debug(f"Wrote temporary little-endian wavelet-compressed HKX file: {temp_wavelet_path}")

        # 2. Call `HavokWaveletAnim` to convert to interleaved.
        call_havok_wavelet_anim(temp_wavelet_path, temp_interleaved_path, to_wavelet=False)
        _LOGGER.debug(f"Converted wavelet-compressed HKX to interleaved HKX: {temp_interleaved_path}")

        # 3. Read new interleaved HKX file and enable fields.
        interleaved_hkx = self.__class__.from_path(temp_interleaved_path)
        interleaved_hkx.is_big_endian = old_is_big_endian
        interleaved_hkx.packfile_header_info.reuse_padding_optimization = 1
        _LOGGER.debug(f"Read new interleaved HKX file: {temp_interleaved_path}")

        # Clean-up.
        temp_wavelet_path.unlink(missing_ok=True)
        temp_interleaved_path.unlink(missing_ok=True)

        _LOGGER.info("Converted wavelet-compressed animation to interleaved.")

        return interleaved_hkx

    def to_spline_hkx(self) -> AnimationHKX:
        """Zero need for this. If this is being ported between games, change Havok version first."""
        raise TypeError("Cannot convert Demon's Souls animations (Havok 5.5.0) to spline-compressed.")

    def to_wavelet_hkx(self) -> tp.Self:
        """Uses `HavokWaveletAnim` to convert wavelet-compressed to interleaved animation.

        Cannot be done at the `AnimationContainer` level because we need to read/write whole valid HKX files during the
        conversion process.

        Steps:
            - Write this wavelet-compressed HKX as a temp file, with `is_big_endian=False`.
            - Call `HavokWaveletAnim` to convert it to interleaved.
            - Read the new interleaved HKX file.
            - Restore `is_big_endian` and set `reuse_padding_optimization = 1`.

        TODO: Currently assuming that `reuse_padding_optimization` doesn't actually change how these files are read.
         I haven't noticed any read/write errors; it's possible that it happens to not matter for these `hka` classes.
        """
        if not self.animation_container.is_interleaved:
            raise ValueError("Can only convert interleaved animations to wavelet-compressed animations.")

        temp_interleaved_path = HAVOK_PACKAGE_PATH("__temp_interleaved__.hkx")
        temp_wavelet_path = HAVOK_PACKAGE_PATH("__temp_wavelet__.hkx")

        # C++ converter requires LE, but we save the current value to restore it later to the interleaved HKX.
        old_is_big_endian = self.is_big_endian

        # 1. Write little-endian interleaved file. (Probably already little-endian, but we copy and set it anyway.)
        le_interleaved_hkx = copy.deepcopy(self)
        le_interleaved_hkx.is_big_endian = False
        le_interleaved_hkx.write(temp_interleaved_path)
        _LOGGER.debug(f"Wrote temporary little-endian interleaved HKX file: {temp_interleaved_path}")

        # 2. Call `HavokWaveletAnim` to convert to wavelet-compressed.
        call_havok_wavelet_anim(temp_interleaved_path, temp_wavelet_path, to_wavelet=True)
        _LOGGER.debug(f"Converted interleaved HKX to wavelet-compressed HKX: {temp_wavelet_path}")

        # 3. Read new wavelet-compressed HKX file and enable fields.
        wavelet_hkx = self.__class__.from_path(temp_wavelet_path)
        wavelet_hkx.is_big_endian = old_is_big_endian
        wavelet_hkx.packfile_header_info.reuse_padding_optimization = 1
        _LOGGER.debug(f"Read new wavelet-comprsesed HKX file: {temp_interleaved_path}")

        # Clean-up.
        temp_interleaved_path.unlink(missing_ok=True)
        temp_wavelet_path.unlink(missing_ok=True)

        _LOGGER.info("Converted interleaved animation to wavelet-compressed.")

        return wavelet_hkx

    @classmethod
    def from_minimal_data_interleaved(
        cls,
        frame_transforms: list[list[TRSTransform]],  # outer list is frames, inner list is tracks (must be regular)
        transform_track_bone_indices: list[int],
        root_motion_array: np.ndarray | None = None,  # four columns: X, Y, Z, Y rotation
        original_skeleton_name="master",
        frame_rate: float = 30.0,
        skeleton_for_armature_to_local: BaseSkeletonHKX = None,
        track_names: list[str] = (),
        scene_asset_name="",
    ) -> tp.Self:
        """Demon's Souls (Havok 550) animation files contain a `hkxScene` variant, which is required for conversion
        to wavelet-compressed format.

        We also remove all `annotationTracks` from the animation, which aren't supported.

        `scene_asset_name` will be written to that scene if present, though it's almost certainly not needed. E.g.:
            "N:\\DemonsSoul\\data\\Model\\chr\\c5020\\motion\\a00_0000【待機】.max"
        """

        animation_hkx = super(AnimationHKX, cls).from_minimal_data_interleaved(
            frame_transforms=frame_transforms,
            transform_track_bone_indices=transform_track_bone_indices,
            root_motion_array=root_motion_array,
            original_skeleton_name=original_skeleton_name,
            frame_rate=frame_rate,
            skeleton_for_armature_to_local=skeleton_for_armature_to_local,
            track_names=track_names,
        )

        # Remove all annotation tracks. These cause the wavelet converter to crash and aren't present in DeS files.
        animation_hkx.animation_container.hkx_animation.annotationTracks = []

        # Add `hkxScene` to animation container.
        scene = hkxScene(
            modeller="3ds max 9.0.0",
            asset=scene_asset_name,
            sceneLength=animation_hkx.animation_container.hkx_animation.duration,
            appliedTransform=(1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0),  # default, for clarity
        )

        animation_hkx.root.namedVariants.append(
            hkRootLevelContainerNamedVariant(
                name="Scene Data",
                className="hkxScene",
                variant=scene,
                variantClass=None,
            )
        )

        return animation_hkx


class SkeletonHKX(BaseSkeletonHKX):
    HAVOK_MODULE: tp.ClassVar[PyHavokModule] = PyHavokModule.hk550
    root: hkRootLevelContainer = None
    skeleton: SkeletonType = None


class CollisionHKX(BaseCollisionHKX):
    HAVOK_MODULE: tp.ClassVar[PyHavokModule] = PyHavokModule.hk550
    root: hkRootLevelContainer = None
    physics_data: PhysicsDataType = None


class ClothHKX(BaseClothHKX):
    HAVOK_MODULE: tp.ClassVar[PyHavokModule] = PyHavokModule.hk550
    root: hkRootLevelContainer = None
    cloth_physics_data: ClothPhysicsData[hkpPhysicsData, hkpPhysicsSystem] = None


class RagdollHKX(BaseRagdollHKX):
    HAVOK_MODULE: tp.ClassVar[PyHavokModule] = PyHavokModule.hk550
    root: hkRootLevelContainer = None
    animation_skeleton: SkeletonType = None
    ragdoll_skeleton: SkeletonType = None
    physics_data: PhysicsDataType = None
    animation_to_ragdoll_skeleton_mapper: SkeletonMapperType = None
    ragdoll_to_animation_skeleton_mapper: SkeletonMapperType = None
