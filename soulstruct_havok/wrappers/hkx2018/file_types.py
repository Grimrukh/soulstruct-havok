from __future__ import annotations

__all__ = [
    "AnimationHKX",
    "SkeletonHKX",
    "AnimationContainerType",
    "SkeletonType",
    "SkeletonMapperType",
]

import logging
import typing as tp
from dataclasses import dataclass

import numpy as np

from soulstruct_havok.types import hk2018
from soulstruct_havok.types.hk2018 import *
from soulstruct_havok.utilities.mesh import Mesh
from soulstruct_havok.wrappers.base import *

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
