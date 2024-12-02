from __future__ import annotations

__all__ = ["AnimationHKX", "SkeletonHKX", "ClothHKX", "RagdollHKX"]

import copy
import logging
import subprocess as sp
import typing as tp
from dataclasses import dataclass
from pathlib import Path

from soulstruct_havok.packfile.structs import PackfileHeaderInfo, PackFileVersion
from soulstruct_havok.types import hk550
from soulstruct_havok.types.hk550 import *
from soulstruct_havok.fromsoft.base import *
from soulstruct_havok.utilities.files import HAVOK_PACKAGE_PATH

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


@dataclass(slots=True, repr=False)
class AnimationHKX(BaseAnimationHKX):
    """NOTE: Demon's Souls animations are wavelet-compressed, which is an annoying old format to deal with."""

    TYPES_MODULE = hk550
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
                contents_version_string=hk550.VERSION,
                flags=0,
                header_extension=None,
            )
        )
        return kwargs

    def to_interleaved_hkx(self) -> tp.Self:
        """Uses `HavokWaveletAnim` to convert wavelet-compressed to interleaved animation.

        Cannot be done at the `AnimationContainer` level because we need to read/write whole valid HKX files during the
        conversion process.

        Steps:
            - Write this wavelet-compressed HKX as a temp file, with `big_endian=False`.
            - Call `HavokWaveletAnim` to convert it to interleaved.
            - Read the new interleaved HKX file.
            - Re-enable `big_endian=True` and `reuse_padding_optimization=1`.

        TODO: Currently assuming that `reuse_padding_optimization` doesn't actually change how these files are read.
         I haven't noticed any read/write errors; it's possible that it happens to not matter for these `hka` classes.
        """
        if self.animation_container.is_spline:
            return super().to_interleaved_hkx()
        if not self.animation_container.is_wavelet:
            raise ValueError(
                "Can only convert spline-compressed or wavelet-compressed animations to interleaved animations."
            )

        temp_wavelet_path = HAVOK_PACKAGE_PATH("__temp_wavelet__.hkx")
        temp_interleaved_path = HAVOK_PACKAGE_PATH("__temp_interleaved__.hkx")

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
        interleaved_hkx.is_big_endian = True
        interleaved_hkx.packfile_header_info.reuse_padding_optimization = 1
        _LOGGER.debug(f"Read new interleaved HKX file: {temp_interleaved_path}")

        # Clean-up.
        temp_wavelet_path.unlink(missing_ok=True)
        temp_interleaved_path.unlink(missing_ok=True)

        return interleaved_hkx

    def to_spline_hkx(self) -> AnimationHKX:
        """Zero need for this. If this is being ported between games, change Havok version first."""
        raise TypeError("Cannot convert Demon's Souls animations (Havok 5.5.0) to spline-compressed.")

    def to_wavelet_hkx(self) -> tp.Self:
        """Uses `HavokWaveletAnim` to convert wavelet-compressed to interleaved animation.

        Cannot be done at the `AnimationContainer` level because we need to read/write whole valid HKX files during the
        conversion process.

        Steps:
            - Write this wavelet-compressed HKX as a temp file, with `big_endian=False`.
            - Call `HavokWaveletAnim` to convert it to interleaved.
            - Read the new interleaved HKX file.
            - Re-enable `big_endian=True` and `reuse_padding_optimization=1`.

        TODO: Currently assuming that `reuse_padding_optimization` doesn't actually change how these files are read.
         I haven't noticed any read/write errors; it's possible that it happens to not matter for these `hka` classes.
        """
        if not self.animation_container.is_interleaved:
            raise ValueError("Can only convert interleaved animations to wavelet-compressed animations.")

        temp_interleaved_path = HAVOK_PACKAGE_PATH("__temp_interleaved__.hkx")
        temp_wavelet_path = HAVOK_PACKAGE_PATH("__temp_wavelet__.hkx")

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
        wavelet_hkx.is_big_endian = True
        wavelet_hkx.packfile_header_info.reuse_padding_optimization = 1
        _LOGGER.debug(f"Read new wavelet-comprsesed HKX file: {temp_interleaved_path}")

        # Clean-up.
        temp_interleaved_path.unlink(missing_ok=True)
        temp_wavelet_path.unlink(missing_ok=True)

        return wavelet_hkx


@dataclass(slots=True, repr=False)
class SkeletonHKX(BaseSkeletonHKX):
    TYPES_MODULE = hk550
    root: hkRootLevelContainer = None
    skeleton: SkeletonType = None


@dataclass(slots=True, repr=False)
class CollisionHKX(BaseCollisionHKX):
    TYPES_MODULE = hk550
    root: hkRootLevelContainer = None
    physics_data: PhysicsDataType = None


@dataclass(slots=True, repr=False)
class ClothHKX(BaseClothHKX):
    TYPES_MODULE = hk550
    root: hkRootLevelContainer = None
    cloth_physics_data: ClothPhysicsData[hkpPhysicsData, hkpPhysicsSystem] = None


@dataclass(slots=True, repr=False)
class RagdollHKX(BaseRagdollHKX):
    TYPES_MODULE = hk550
    root: hkRootLevelContainer = None
    animation_skeleton: SkeletonType = None
    ragdoll_skeleton: SkeletonType = None
    physics_data: PhysicsDataType = None
    animation_to_ragdoll_skeleton_mapper: SkeletonMapperType = None
    ragdoll_to_animation_skeleton_mapper: SkeletonMapperType = None
