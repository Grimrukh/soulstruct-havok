"""Operations for meshes, mostly for use with Havok navmeshes."""
from __future__ import annotations

import io

import numpy as np
from scipy.spatial import KDTree

from soulstruct.utilities.maths import Vector3

try:
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    plt = None


class Mesh:
    vertices: np.ndarray
    faces: list[list[int]]  # does NOT assume triangles
    triangulated_faces: dict[int, list[tuple[list[int], bool]]]  # `faces` -> lists of triangles and their convexity

    def __init__(self, vertices: np.ndarray, faces: list[list[int]]):
        self.vertices = vertices
        self.faces = faces
        self.triangulated_faces = {}

    @property
    def vertex_count(self):
        return len(self.vertices)

    @property
    def face_count(self):
        return len(self.faces)

    @property
    def has_triangles_only(self):
        for face in self.faces:
            if len(face) != 3:
                return False
        return True

    def get_string(self, **header) -> str:
        """Get a string of the mesh data, suitable for writing to a text file.

        `name` must be required to add to top of file.
        """
        bio = io.BytesIO()
        # noinspection PyTypeChecker
        np.savetxt(bio, self.vertices)
        s = "\n".join(f"# {k} = {v}" for k, v in header.items())
        if s:
            s += "\n\n"
        s += "# vertices\n"
        s += bio.getvalue().decode("latin1") + "\n"
        s += "# faces\n"
        for f in self.faces:
            s += " ".join(str(i) for i in f) + "\n"
        return s

    def plot_mesh(
        self,
        circularity_threshold=0.4,
        boundary_edge_threshold=0.5,
        scatter_vertices=False,
        scatter_face_centroids=True,
        label_vertices=False,
        label_faces=False,
        edge_plot_kwargs=None,
        boundary_edge_plot_kwargs=None,
        ax: plt.Axes = None,
    ) -> tuple[plt.Figure, plt.Axes]:

        if plt is None:
            raise ImportError("Matplotlib must be installed to plot meshes.")

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
        vertices = self.vertices.copy()
        vertices[:, 1], vertices[:, 2] = vertices[:, 2], vertices[:, 1].copy()

        # Detect boundary edges across the mesh.
        boundary_edges = set()  # type: set[tuple[int, int]]
        common_edges = set()  # type: set[tuple[int, int]]  # direction dropped
        for face in self.faces:
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

        if scatter_vertices:
            ax.scatter(
                vertices[:, 0], vertices[:, 1], vertices[:, 2], marker=".", color="black", s=10, label="Vertices"
            )
        if label_vertices:
            for i, vert in enumerate(vertices):
                ax.text(vert[0], vert[1], vert[2] + 1, s=f"{i}", color='black', ha='center', va='center')

        drawn_edges = set()  # type: set[tuple[tuple, tuple], ...]
        for i, face in enumerate(self.faces):
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

            centroid = self.get_face_centroid(face_edge_starts, face_edge_ends)
            circularity = self.get_face_circularity(face_edge_starts, face_edge_ends)

            for b, v_a, v_b in zip(is_edge_boundary, face_edge_starts, face_edge_ends, strict=True):

                edge = tuple(sorted((tuple(v_a), tuple(v_b))))
                if edge in drawn_edges:
                    continue

                # Plot edge line.
                ax.plot(
                    *[(v_a[i], v_b[i]) for i in range(3)],
                    **(boundary_edge_plot_kwargs if b else edge_plot_kwargs),
                )
                drawn_edges.add(edge)

            if boundary_edge_proportion > boundary_edge_threshold:
                c_color = "orange"
            elif circularity < circularity_threshold:
                c_color = "red"
            else:
                c_color = "green"

            if label_faces:
                text = f"[{i}] C={circularity:.1f} | B={boundary_edge_proportion:.1f}"
                ax.text(*centroid, s=text, color=c_color, ha='center', va='center')
            elif scatter_face_centroids:
                # Draw centroid point.
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

    def merge_vertices_by_distance(self, merge_dist: float = 0.5) -> Mesh:
        """Reduce `Mesh` by merging all vertices within `merge_dist` of each other into their mean 3D position.

        This may involve face side count changing. Degenerate faces will be handled.
        """

        vertices_tree = KDTree(self.vertices)
        is_merged = np.zeros(len(self.vertices), dtype=bool)

        for i, vertex in enumerate(self.vertices):
            if not is_merged[i]:
                # Get vertex indices within the merge distance.
                indices = vertices_tree.query_ball_point(vertex, merge_dist)
                # Merge points by taking mean.
                if len(indices) > 1:
                    mean_vertex = np.mean(self.vertices[indices], axis=0)
                    self.vertices[indices] = mean_vertex
                    is_merged[indices] = True

        # Filter out duplicate (merged) vertices, and get mapping from old vertex indices to new ones.
        merged_vertices, old_to_merged = np.unique(self.vertices, axis=0, return_inverse=True)

        # Update vertex indices of faces, carefully to spot now-degenerate faces or even now-split concave faces.
        merged_faces = []
        for face in self.faces:
            merged_face = [old_to_merged[face[0]]]  # initialize with first merged vertex
            for old_i in face[1:]:
                i = old_to_merged[old_i]
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

        return Mesh(merged_vertices, merged_faces)

    def get_vertex_to_face_map(self) -> dict[int, list[int]]:
        """Get a dictionary mapping indices of `vertices` to indices of `faces` that use that vertex.

        Makes it much faster to detect connected faces.
        """
        vertex_to_faces = {}
        for i, face in enumerate(self.faces):
            for v_i in face:
                vertex_to_faces.setdefault(v_i, []).append(i)
        return vertex_to_faces

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
            tri_areas.append(Mesh.get_triangle_area(tri))

        # Get average of those centroids, weighted by the signed areas.
        return Vector3(np.average(tri_centroids, axis=0, weights=tri_areas))
