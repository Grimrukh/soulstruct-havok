from __future__ import annotations

__all__ = [
    "AnimationHKX",
    "SkeletonHKX",
    "AnimationContainerType",
    "SkeletonType",
    "SkeletonMapperType",
]

import io
import logging
import typing as tp
from dataclasses import dataclass, field

import matplotlib.pyplot as plt
import numpy as np

from soulstruct_havok.types import hk2018
from soulstruct_havok.types.hk2018 import *
from soulstruct_havok.utilities.maths import Vector3
from soulstruct_havok.wrappers.base import *

_LOGGER = logging.getLogger("soulstruct_havok")

AnimationContainerType = AnimationContainer[
    hkaAnimationContainer, hkaAnimation, hkaAnimationBinding,
    hkaInterleavedUncompressedAnimation, hkaSplineCompressedAnimation, hkaDefaultAnimatedReferenceFrame,
]
SkeletonType = Skeleton[hkaSkeleton, hkaBone]
SkeletonMapperType = SkeletonMapper[hkaSkeletonMapper]


@dataclass(slots=True)
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

    def get_simple_mesh_data(self, merge_dist=0) -> tuple[np.ndarray, list[list[int]]]:
        """Return an Nx3 vertex array and a list of faces' vertex indices, of varying length, into that array.

        Note that unlike older games, not all faces need be triangles, or even quads.

        We don't need the edge data in the HKX file, as each edge is unique to a face, and only exist as Havok instances
        so edge-specific information can be defined (which we don't care about here).
        """
        hkai_navmesh = self.get_variant(0, hkaiNavMesh)

        if hkai_navmesh.vertices == [] or not hkai_navmesh.faces:
            _LOGGER.warning("Navmesh has no vertices and/or faces.")
            return np.empty((0, 3)), []

        vertices = np.array(hkai_navmesh.vertices[:, :3])  # discard fourth column

        faces = []
        for face in hkai_navmesh.faces:
            face_vert_indices = [
                hkai_navmesh.edges[i].a
                for i in range(face.startEdgeIndex, face.startEdgeIndex + face.numEdges)
            ]
            faces.append(face_vert_indices)

        if merge_dist > 0:
            old_v_count, old_f_count = len(vertices), len(faces)
            vertices, faces = self.reduce_mesh(vertices, faces, merge_dist=merge_dist)
            _LOGGER.info(
                f"Reduced mesh from {old_v_count} vertices and {old_f_count} faces to "
                f"{len(vertices)} vertices and {len(faces)} faces."
            )

        return vertices, faces

    @staticmethod
    def get_simple_mesh_string(vertices: np.ndarray, faces: list[list[int]], **header) -> str:
        """Get a string of the mesh data, suitable for writing to a text file.

        `name` must be required to add to top of file.
        """
        bio = io.BytesIO()
        # noinspection PyTypeChecker
        np.savetxt(bio, vertices)
        s = "\n".join(f"# {k} = {v}" for k, v in header.items())
        if s:
            s += "\n\n"
        s += "# vertices\n"
        s += bio.getvalue().decode("latin1") + "\n"
        s += "# faces\n"
        for f in faces:
            s += " ".join(str(i) for i in f) + "\n"
        return s

    @classmethod
    def plot_simple_mesh(
        cls,
        vertices: np.ndarray,
        faces: list[list[int]],
        circularity_threshold=0.4,
        boundary_edge_threshold=0.5,
        label_vertices=False,
        label_faces=False,
        edge_plot_kwargs=None,
        boundary_edge_plot_kwargs=None,
        ax: plt.Axes = None,
    ) -> tuple[plt.Figure, plt.Axes]:

        if not ax:
            fig = plt.figure()
            ax = fig.add_subplot(projection="3d")
        else:
            fig = ax.get_figure()

        if edge_plot_kwargs is None:
            edge_plot_kwargs = {
                "color": "black",
                "linewidth": 1,
                "alpha": 0.5,
            }
        if boundary_edge_plot_kwargs is None:
            boundary_edge_plot_kwargs = {
                "color": "red",
                "linewidth": 2,
                "alpha": 0.5,
            }

        # Swap Y and Z for plotting.
        vertices = vertices.copy()
        vertices[:, 1], vertices[:, 2] = vertices[:, 2], vertices[:, 1].copy()

        # Detect boundary edges across the mesh.
        boundary_edges = set()  # type: set[tuple[int, int]]
        common_edges = set()  # type: set[tuple[int, int]]  # direction dropped
        for face in faces:
            for i in range(len(face)):
                a, b = face[i], face[(i + 1) % len(face)]
                if a > b:
                    a, b = b, a
                edge = (a, b)
                if edge in common_edges:
                    continue
                elif edge in boundary_edges:
                    # Second (and should be final) occurrence.
                    boundary_edges.remove(edge)
                    common_edges.add(edge)
                else:
                    # First occurrence.
                    boundary_edges.add(edge)

        ax.scatter(
            vertices[:, 0], vertices[:, 1], vertices[:, 2], marker=".", color="black", s=10, label="Vertices"
        )
        if label_vertices:
            for i, vert in enumerate(vertices):
                ax.text(vert[0], vert[1], vert[2] + 1, s=f"{i}", color='black', ha='center', va='center')

        for i, face in enumerate(faces):
            face_roll = np.roll(face, -1)
            face_edges = [
                tuple(sorted((face[j], face_roll[j])))
                for j in range(len(face))
            ]
            is_edge_boundary = [edge in boundary_edges for edge in face_edges]

            face_edge_starts = vertices[face]
            face_edge_ends = np.roll(face_edge_starts, -1, axis=0)

            # Calculate edge lengths.
            face_edge_lengths = np.linalg.norm(face_edge_ends - face_edge_starts, axis=1)
            # Check unique edge length ratio.
            total_unique_length = face_edge_lengths[is_edge_boundary].sum()
            boundary_edge_proportion = total_unique_length / face_edge_lengths.sum()
            
            centroid = cls.get_face_centroid(face_edge_starts, face_edge_ends)
            circularity = cls.get_face_circularity(face_edge_starts, face_edge_ends)

            for b, v_a, v_b in zip(is_edge_boundary, face_edge_starts, face_edge_ends, strict=True):
                # Plot edge line.
                ax.plot(
                    *[(v_a[i], v_b[i]) for i in range(3)],
                    **(boundary_edge_plot_kwargs if b else edge_plot_kwargs),
                )

            if boundary_edge_proportion > boundary_edge_threshold:
                c_color = "orange"
            elif circularity < circularity_threshold:
                c_color = "red"
            else:
                c_color = "green"

            if label_faces:
                text = f"[{i}] C={circularity:.1f} | B={boundary_edge_proportion:.1f}"
                ax.text(*centroid, s=text, color=c_color, ha='center', va='center')
            else:
                # Draw dot in centroid.
                ax.scatter(*centroid, marker="x", color=c_color)

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')

        # For x, y, z, calculate min and max values.
        min_x, max_x = vertices[:, 0].min(), vertices[:, 0].max()
        min_y, max_y = vertices[:, 1].min(), vertices[:, 1].max()
        min_z, max_z = vertices[:, 2].min(), vertices[:, 2].max()
        # Calculate range of each axis.
        range_x = max_x - min_x
        range_y = max_y - min_y
        range_z = max_z - min_z
        # Get max range.
        max_range = max(range_x, range_y, range_z)
        # Set limits to half max range on either side of center.
        ax.set_xlim(min_x - max_range / 2, max_x + max_range / 2)
        ax.set_ylim(min_y - max_range / 2, max_y + max_range / 2)
        ax.set_zlim(min_z - max_range / 2, max_z + max_range / 2)

        return fig, ax

    @staticmethod
    def get_triangle_area(tri: np.ndarray) -> float:
        """Calculate the area of triangle defined by 3x3 `tri` array."""
        a, b, c = tri[0], tri[1], tri[2]
        ab = b - a
        ac = c - a
        # noinspection PyUnreachableCode
        cross = np.cross(ab, ac)
        return 0.5 * np.linalg.norm(cross)

    @staticmethod
    def get_face_circularity(face_edge_starts: np.ndarray, face_edge_ends: np.ndarray) -> float:
        """Get circularity of the polygon defined by edges starting at `face_edge_starts` and ending at `face_edge_ends` (should
        be rolled by 1).

        Note that we ignore Z (height) for this and assume the polygon is flat, which is totally fine because we're using
        this to determine where it's safe to spawn things, and so only care about face shape in a top-down projection.
        """

        # Shoelace formula for area.
        ax_by = face_edge_starts[:, 0] * face_edge_ends[:, 1]
        bx_ay = face_edge_ends[:, 0] * face_edge_starts[:, 1]
        signed_area = (ax_by - bx_ay).sum()
        area = np.abs(signed_area) / 2.0

        # Calculate perimeter.
        perimeter = np.linalg.norm(face_edge_starts - face_edge_ends, axis=1).sum()

        # Return circularity (1 == circle).
        return (4 * np.pi * area) / (perimeter ** 2)

    @staticmethod
    def get_face_centroid(face_edge_starts: np.ndarray, face_edge_ends: np.ndarray) -> Vector3:
        """Get 3D centroid of the polygon defined by edges starting at `face_edge_starts` and ending at
        `face_edge_ends` (should be rolled by 1).
        """

        if face_edge_starts.shape[0] == 3:
            # Triangle. Centroid is simple average of vertices.
            return Vector3(face_edge_starts.mean(axis=0))

        # First, estimate the centroid by taking the mean of all face vertices.
        origin = face_edge_starts.mean(axis=0)  # estimate skewed by vertex density
        tri_areas = []
        tri_centroids = []

        for vert_a, vert_b in zip(face_edge_starts, face_edge_ends):
            tri = np.array([vert_a, vert_b, origin])
            tri_centroids.append(tri.mean(axis=0))
            tri_areas.append(NavmeshHKX.get_triangle_area(tri))

        # Get average of those centroids, weighted by the signed areas.
        return Vector3(np.average(tri_centroids, axis=0, weights=tri_areas))

    @staticmethod
    def reduce_mesh(vertices: np.ndarray, faces: list[list[int]], merge_dist=0.5):
        """Reduce mesh by merging all vertices within `merge_dist` of each other into their mean 3D position.

        This may involve face side count changing. Degenerate faces will be handled.
        """

        merge_dist_sq = merge_dist ** 2

        # Iterate over vertices and merge any that are within `merge_dist` of each other (to their Cartesian mean).
        # Maintain a list mapping original vertex indices to merged unique vertex indices.
        merged_vertices = []
        old_to_merged_vertex_indices = []
        for_averaging = {}
        for i, vertex in enumerate(vertices):
            for j, merged_vertex in enumerate(merged_vertices):
                if np.sum((vertex - merged_vertex) ** 2) < merge_dist_sq:
                    # Found an existing merged vertex.
                    old_to_merged_vertex_indices.append(j)
                    if j not in for_averaging:
                        # Some merging actually occurred at this vertex. Start dictionary entry for averaging later.
                        for_averaging[j] = [merged_vertex]
                    for_averaging[j].append(vertex)
                    break
            else:
                # Use this vertex as a new merged vertex.
                old_to_merged_vertex_indices.append(len(merged_vertices))
                merged_vertices.append(vertex)

        # Calculate means of merged vertices.
        for j, merged in for_averaging.items():
            merged_vertices[j] = np.mean(merged, axis=0)

        merged_vertices = np.array(merged_vertices)

        # Update vertex indices of faces, carefully to spot now-degenerate faces or even now-split concave faces.
        merged_faces = []
        for face in faces:
            merged_face = [old_to_merged_vertex_indices[face[0]]]  # initialize with first merged vertex
            for old_i in face[1:]:
                i = old_to_merged_vertex_indices[old_i]
                if merged_face[-1] == i:
                    # Vertex repeated (this edge has vanished). Just skip this repeated occurrence.
                    continue
                if i in merged_face:
                    # Same merged vertex is already in face.
                    if merged_face[-2] == i:
                        # Face contains the same edge in both directions. Previous vertex is degenerate, and we skip
                        # this repeated one.
                        merged_face = merged_face[:-1]
                        continue
                    # Finish current merged face (will loop back to this repeated vertex) and start a new one.
                    if len(merged_face) >= 3:
                        merged_faces.append(merged_face)
                    merged_face = [i]
                else:
                    # Continue face normally.
                    merged_face.append(i)

            # Face completed naturally. We just check size, and if the last vertex has merged with the first.

            if merged_face[-1] == merged_face[0]:
                merged_face = merged_face[:-1]  # ignore last vertex
            if len(merged_face) < 3:
                continue  # ignore degenerate face

            merged_faces.append(merged_face)

        return merged_vertices, merged_faces
