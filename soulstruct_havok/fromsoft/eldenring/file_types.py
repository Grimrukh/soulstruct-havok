from __future__ import annotations

__all__ = [
    "AnimationHKX",
    "SkeletonHKX",
    "AnimationContainerType",
    "SkeletonType",
    "SkeletonMapperType",
]

import logging
import subprocess as sp
import typing as tp
from dataclasses import dataclass

import numpy as np

from soulstruct.dcx import DCXType

from soulstruct_havok.core import HavokFileFormat
from soulstruct_havok.packfile.structs import PackFileVersion, PackfileHeaderInfo
from soulstruct_havok.types import hk2010, hk2018
from soulstruct_havok.types.hk2018 import *
from soulstruct_havok.utilities.files import HAVOK_PACKAGE_PATH
from soulstruct_havok.utilities.hk_conversion import convert_hk
from soulstruct_havok.utilities.mesh import Mesh
from soulstruct_havok.fromsoft.base import *
from soulstruct_havok.fromsoft.darksouls1ptde import AnimationHKX as AnimationHKX_PTDE

_LOGGER = logging.getLogger("soulstruct_havok")

AnimationContainerType = AnimationContainer[
    hkaAnimationContainer, hkaAnimation, hkaAnimationBinding,
    hkaInterleavedUncompressedAnimation, hkaSplineCompressedAnimation, hkaDefaultAnimatedReferenceFrame,
]
SkeletonType = Skeleton[hkaSkeleton, hkaBone]
SkeletonMapperType = SkeletonMapper[hkaSkeletonMapper]


@dataclass(slots=True, repr=False)
class AnimationHKX(BaseAnimationHKX):
    TYPES_MODULE: tp.ClassVar = hk2018
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

        _LOGGER.debug("Upgrading to 2018...")
        anim_2018 = self.__class__.from_2010_hkx(hkx2010_spline, dcx_type=dcx_type)

        # Clean-up: restore hash overrides, change binding to refer to same animation, and change animation type.
        anim_2018.hsh_overrides = self.hsh_overrides.copy()
        for i, anim in enumerate(anim_2018.animation_container.animation_container.animations):
            anim_2018.animation_container.animation_container.bindings[i].animation = anim
            anim.type = 3  # spline-compressed in Havok 2018 (was 5 in Havok 2010)

        _LOGGER.info("Successfully converted interleaved animation to hk2018 spline animation.")
        return anim_2018

    def to_2010_hkx(self) -> AnimationHKX_PTDE:
        """Construct a 2010 Havok file (with packfile type) from this 2018 tagfile.

        This is done using Capra Demon's animation 3000 from PTDE as a base, and injecting this file's data into it.

        (I am adding these specific conversion functions as needed for Nightfall.)
        """
        if self.animation_container.is_spline:
            self.animation_container.save_spline_data()
        elif self.animation_container.is_interleaved:
            self.animation_container.save_interleaved_data()

        def source_error_handler(source_obj: hk, name: str, __, ___):
            if name == "propertyBag":
                return []  # fine to ignore
            if isinstance(source_obj, hk2018.hkaAnimatedReferenceFrame) and name == "frameType":
                return []  # not serializable anyway
            if isinstance(source_obj, hk2018.hkaAnimationBinding) and name == "partitionIndices":
                return []

        import time
        t = time.perf_counter()
        root2010 = convert_hk(self.root, hk2010.hkRootLevelContainer, hk2010, source_error_handler)
        _LOGGER.info(f"Converted 2018 Animation HKX to 2010 in {time.perf_counter() - t} s.")
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
        """Construct a 2018 Havok animation tagfile from a 2010 Havok animation packfile.

        `dcx_type` defaults to be the same as `hkx2010`. It does NOT default to the standard DSR DCX type, because most
        HKX files appear inside compressed binders and are NOT compressed themselves.
        """

        def dest_handler(dest_type: type[hk], dest_kwargs: dict[str, tp.Any], name: str):
            if name == "propertyBag":
                dest_kwargs["propertyBag"] = hk2018.hkPropertyBag(bag=None)
                return True
            if dest_type is hk2018.hkaAnimatedReferenceFrame and name == "frameType":
                dest_kwargs["frameType"] = 0  # not serializable anyway
                return True
            if dest_type is hk2018.hkaAnimationBinding and name == "partitionIndices":
                dest_kwargs["partitionIndices"] = []
                return True
            return False

        if dcx_type is None:
            dcx_type = hkx2010.dcx_type

        import time
        t = time.perf_counter()
        root2018 = convert_hk(hkx2010.root, hk2018.hkRootLevelContainer, hk2018, None, dest_handler)
        _LOGGER.info(f"Converted hk2010 animation to hk2018 animation in {time.perf_counter() - t:.3f} s.")
        return cls(
            dcx_type=dcx_type,
            root=root2018,
            hk_format=HavokFileFormat.Tagfile,
            hk_version="20180100",
        )


@dataclass(slots=True)
class SkeletonHKX(BaseSkeletonHKX):
    TYPES_MODULE: tp.ClassVar = hk2018
    root: hkRootLevelContainer = None
    skeleton: SkeletonType = None


@dataclass(slots=True)
class NavmeshHKX(BaseWrappedHKX):
    # TODO: Generic version in `base`.
    TYPES_MODULE: tp.ClassVar = hk2018

    root: hkRootLevelContainer

    def get_simple_mesh(self, merge_dist: float = 0) -> Mesh:
        """Return an Nx3 vertex array and a list of faces' vertex indices, of varying length, into that array.

        Note that unlike older games, not all faces need be triangles, or even quads.

        We don't need the edge data in the HKX file, as each edge is unique to a face, and only exist as Havok instances
        so edge-specific information can be defined (which we don't care about here).
        """
        hkai_navmesh = self.get_variant(0, hkaiNavMesh)

        if hkai_navmesh.vertices == [] or not hkai_navmesh.faces:
            _LOGGER.warning("Navmesh has no vertices and/or faces.")
            return Mesh(np.empty((0, 3)), [])

        vertices = np.array(hkai_navmesh.vertices[:, :3])  # discard fourth column

        faces = []
        for face in hkai_navmesh.faces:
            face_vert_indices = [
                hkai_navmesh.edges[i].a
                for i in range(face.startEdgeIndex, face.startEdgeIndex + face.numEdges)
            ]
            faces.append(face_vert_indices)

        mesh = Mesh(vertices, faces)

        if merge_dist > 0:
            old_v_count, old_f_count = len(vertices), len(faces)
            mesh = mesh.merge_vertices_by_distance(merge_dist=merge_dist)
            _LOGGER.info(
                f"Reduced mesh from {old_v_count} vertices and {old_f_count} faces to "
                f"{len(vertices)} vertices and {len(faces)} faces."
            )

        return mesh
