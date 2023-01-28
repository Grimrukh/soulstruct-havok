from __future__ import annotations

__all__ = ["AnimationHKX", "SkeletonHKX", "ClothHKX", "RagdollHKX", "RemoAnimationHKX"]

import subprocess as sp

from soulstruct_havok.packfile.structs import PackFileVersion, PackfileHeaderInfo
from soulstruct_havok.types import hk, hk2010, hk2015
from soulstruct_havok.wrappers.base import (
    BaseAnimationHKX,
    BaseSkeletonHKX,
    BaseClothHKX,
    BaseRagdollHKX,
    BaseRemoAnimationHKX,
)
from soulstruct_havok.wrappers.hkx2010 import AnimationHKX as AnimationHKX2010
from soulstruct_havok.utilities.hk_conversion import convert_hk


class HKXMixin2015:
    root: hk2015.hkRootLevelContainer
    TYPES_MODULE = hk2015


class AnimationHKX(HKXMixin2015, BaseAnimationHKX):

    def to_spline_animation(self) -> AnimationHKX:
        """Uses Horkrux's compiled converter to convert interleaved to spline."""
        if not self.is_interleaved:
            raise TypeError("Can only convert interleaved animations to spline animations.")
        print("Downgrading to 2010...")
        hkx2010 = self.to_2010_hkx()
        print("Writing 2010 file...")
        hkx2010.write("__temp_interleaved__.hkx")
        print("Calling `CompressAnim`...")
        ret_code = sp.call(
            ["C:\\Dark Souls\\CompressAnim.exe", "__temp_interleaved__.hkx", "__temp_spline__.hkx", "1", "0.001"]
        )
        print(f"Done. Return code: {ret_code}")
        if ret_code != 0:
            raise RuntimeError(f"`CompressAnim.exe` had return code {ret_code}.")
        print("Reading 2010 spline-compressed animation...")
        hkx2010_spline = AnimationHKX2010("__temp_spline__.hkx")
        print("Upgrading to 2015...")
        return AnimationHKX.from_2010_hkx(hkx2010_spline)

    def to_2010_hkx(self) -> AnimationHKX2010:
        """Construct a 2010 Havok file (with packfile type) from this 2015 tagfile.

        This is done using Capra Demon's animation 3000 from PTDE as a base, and injecting this file's data into it.

        (I am adding these specific conversion functions as needed for Nightfall.)
        """
        if self.is_spline:
            self.save_spline_data()
        elif self.is_interleaved:
            self.save_interleaved_data()

        def source_handler(_, name: str, value, dest: hk):
            if name == "refCount":
                setattr(dest, "referenceCount", value)
                return ["referenceCount"]
            if name in ("partitionIndices", "frameType"):  # absent from 2010
                return []

        import time
        t = time.perf_counter()
        root2010 = convert_hk(self.root, hk2010.hkRootLevelContainer, hk2010, source_handler)
        print(f"2015 to 2010 time: {time.perf_counter() - t}")
        hkx2010 = AnimationHKX2010(hk_format=AnimationHKX2010.PACKFILE)
        hkx2010.hk_version = "2010"
        hkx2010.set_root(root2010)
        hkx2010.packfile_header_info = PackfileHeaderInfo(
            header_version=PackFileVersion.Version0x08,
            pointer_size=4,
            is_little_endian=True,
            padding_option=0,
            contents_version_string=b"hk_2010.2.0-r1",
            flags=0,
            header_extension=None,
        )
        return hkx2010

    @classmethod
    def from_2010_hkx(cls, hkx2010: AnimationHKX2010) -> AnimationHKX:

        def source_handler(_, name: str, value, dest: hk):
            if name == "referenceCount":
                setattr(dest, "refCount", value)
                return ["refCount"]

        def dest_handler(dest: hk, name: str):
            if isinstance(dest, hk2015.hkaAnimationBinding) and name == "partitionIndices":
                dest.partitionIndices = []
                return True
            return False

        import time
        t = time.perf_counter()
        root2015 = convert_hk(hkx2010.root, hk2015.hkRootLevelContainer, hk2015, source_handler, dest_handler)
        print(f"2015 to 2010 time: {time.perf_counter() - t}")
        hkx2015 = cls(hk_format=AnimationHKX.TAGFILE)
        hkx2015.hk_version = "2015"
        hkx2015.set_root(root2015)
        return hkx2015


class SkeletonHKX(HKXMixin2015, BaseSkeletonHKX):
    pass


class ClothHKX(HKXMixin2015, BaseClothHKX):
    pass


class RagdollHKX(HKXMixin2015, BaseRagdollHKX):
    pass


class RemoAnimationHKX(HKXMixin2015, BaseRemoAnimationHKX):
    pass
