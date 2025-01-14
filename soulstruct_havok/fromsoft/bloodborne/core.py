"""TODO: Bloodborne/DS3 cloth and ragdoll files have no Python types yet."""

from __future__ import annotations

__all__ = ["AnimationHKX", "SkeletonHKX"]

import logging
import subprocess as sp
import typing as tp

from soulstruct.dcx import DCXType

from soulstruct_havok.enums import PyHavokModule
from soulstruct_havok.packfile.structs import PackFileVersion, PackfileHeaderInfo, PackFileHeaderExtension
from soulstruct_havok.types import hk2010, hk2014
from soulstruct_havok.types.hk2014 import *
from soulstruct_havok.fromsoft.base import *
from soulstruct_havok.fromsoft.darksouls1ptde import AnimationHKX as AnimationHKX_PTDE
from soulstruct_havok.utilities.hk_conversion import convert_hk
from soulstruct_havok.utilities.files import HAVOK_PACKAGE_PATH

_LOGGER = logging.getLogger("soulstruct_havok")

AnimationContainerType = AnimationContainer[
    hkaAnimationContainer, hkaAnimation, hkaAnimationBinding,
    hkaInterleavedUncompressedAnimation,
    hkaSplineCompressedAnimation,
    hkaDefaultAnimatedReferenceFrame,
]
SkeletonType = Skeleton[hkaSkeleton, hkaBone]
SkeletonMapperType = SkeletonMapper[hkaSkeletonMapper]


class AnimationHKX(BaseAnimationHKX):
    HAVOK_MODULE: tp.ClassVar[PyHavokModule] = PyHavokModule.hk2014
    root: hkRootLevelContainer = None
    animation_container: AnimationContainerType = None

    @classmethod
    def get_default_hkx_kwargs(cls) -> dict[str, tp.Any]:
        kwargs = super(AnimationHKX, cls).get_default_hkx_kwargs()
        kwargs |= dict(
            packfile_header_info=PackfileHeaderInfo(
                header_version=PackFileVersion.Version0x0B,
                pointer_size=8,
                is_little_endian=True,
                reuse_padding_optimization=1,
                contents_version_string=VERSION,
                flags=0,
                header_extension=PackFileHeaderExtension(
                    unk_x3c=21,
                    section_offset=16,
                    unk_x40=20,
                    unk_x44=0,
                    unk_x48=0,
                    unk_x4c=0,
                ),
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

        _LOGGER.debug("Upgrading to 2014...")
        anim_2014 = self.__class__.from_2010_hkx(hkx2010_spline, dcx_type=dcx_type)

        # Clean-up: restore hash overrides, change binding to refer to same animation, and change animation type.
        anim_2014.hsh_overrides = self.hsh_overrides.copy()
        for i, anim in enumerate(anim_2014.animation_container.hkx_container.animations):
            anim_2014.animation_container.hkx_container.bindings[i].animation = anim
            anim.type = 3  # spline-compressed in Havok 2014

        _LOGGER.info("Successfully converted interleaved animation to hk2014 spline animation.")
        return anim_2014

    def to_2010_hkx(self) -> AnimationHKX_PTDE:
        """Construct a 2010 Havok file (with packfile type) from this 2014 packfile.

        This is done using Capra Demon's animation 3000 from PTDE as a base, and injecting this file's data into it.

        (I am adding these specific conversion functions as needed for Nightfall.)
        """
        if self.animation_container.is_spline:
            self.animation_container.save_spline_data()
        elif self.animation_container.is_interleaved:
            self.animation_container.save_interleaved_data()

        def source_error_handler(source_obj: hk, name: str, __, ___):
            if isinstance(source_obj, hk2014.hkaAnimatedReferenceFrame) and name == "frameType":
                return []  # not serializable anyway
            if isinstance(source_obj, hk2014.hkaAnimationBinding) and name == "partitionIndices":
                return []

        import time
        t = time.perf_counter()
        root2010 = convert_hk(self.root, hk2010.hkRootLevelContainer, hk2010, source_error_handler)
        _LOGGER.info(f"Converted 2014 Animation HKX to 2010 in {time.perf_counter() - t} s.")
        return AnimationHKX_PTDE(
            dcx_type=DCXType.Null,
            root=root2010,
            **AnimationHKX_PTDE.get_default_hkx_kwargs(),
        )

    @classmethod
    def from_2010_hkx(cls, hkx2010: AnimationHKX_PTDE, dcx_type: DCXType = None) -> tp.Self:
        """Construct a 2014 Havok animation packfile from a 2010 Havok animation packfile.

        `dcx_type` defaults to be the same as `hkx2010`. It does NOT default to the standard BB DCX type, because most
        HKX files appear inside compressed binders and are NOT compressed themselves.
        """

        def dest_handler(dest_type: type[hk], dest_kwargs: dict[str, tp.Any], name: str):
            if dest_type is hk2014.hkaAnimatedReferenceFrame and name == "frameType":
                dest_kwargs["frameType"] = 0  # not serializable anyway
                return True
            if dest_type is hk2014.hkaAnimationBinding and name == "partitionIndices":
                dest_kwargs["partitionIndices"] = []
                return True
            return False

        if dcx_type is None:
            dcx_type = hkx2010.dcx_type

        import time
        t = time.perf_counter()
        root2014 = convert_hk(hkx2010.root, hk2014.hkRootLevelContainer, hk2014, None, dest_handler)
        _LOGGER.info(f"Converted hk2010 animation to hk2014 animation in {time.perf_counter() - t:.3f} s.")

        return cls(dcx_type=dcx_type, root=root2014, **cls.get_default_hkx_kwargs())


class SkeletonHKX(BaseSkeletonHKX):
    HAVOK_MODULE: tp.ClassVar[PyHavokModule] = PyHavokModule.hk2014
    root: hkRootLevelContainer = None
    skeleton: SkeletonType = None
